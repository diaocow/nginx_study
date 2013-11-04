
###配置

webpy代码示例：hello.py

```python
    #!/usr/bin/python
    import web
    
    urls = ("/.*", "hello")
    app = web.application(urls, globals())
    
    class hello:
        def GET(self):
            return 'Welcome to webpy!'
            
    # 这行代码非常重要
    application = app.wsgifunc()
```    
nginx配置：

```sh
    server {
        listen 80; 
        location / { 
            include uwsgi_params;                                                                                
            uwsgi_pass 127.0.0.1:9090;
        }   
    }   
``` 
uWSGI配置：
```sh
    uwsgi --socket 127.0.0.1:9090  \         # 监听在指定端口
          --wsgi-file hello.py \             # 部署的web应用
          --master --processes 2 \           # 创建两个worker进程处理请求
          --daemonize /var/log/uwsgi.log \   # 后台运行uWSGI，并把日志输出到指定文件
          --pidfile /var/log/uwsgi.pid       # pid文件
```    
测试配置
```sh
    $ curl http://127.0.0.1/hello.htm
    Welcome to webpy!
```    
    
###原理分析：
看了上述的配置，你一定很好奇，刚才那些配置究竟起什么作用，uWSGI是什么东西，nginx又是如何转发请求的？

类似java web中servlet规范，python web开发也有自己的规范——[WSGI](http://www.python.org/dev/peps/pep-3333/)，它定义了：**web应用（或者web框架）与web服务器交互接口**
        
而uWSGI就是一个支持WSGI规范的web服务器，也就是说你可以把你的web应用部署到uWSGI中，然后当它接受到请求时，会按照WSGI定义的接口回调web应用处理（这就根我们把java web应用部署到Tomcat，然后Tomcat按照servlet规范回调我们web应用一个道理！），现在我们就看一个按照WSGI规范实现的web应用：simple_app.py
```sh    
    def simple_app(environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type','text/plain')]
        start_response(status, response_headers)
        return ['Hello world!\n']
    
    application = simple_app # 若web应用部署在uWSGI容器中，需要这行代码
```    
其中environ是一个dict类型变量，里面主要包含各种HTTP请求头数据（类似CGI的环境变量），start_response是web服务器提供给web应用的回调接口，用来接受HTTP响应码以及HTTP响应头；最终函数返回对请求的处理结果（这里只是简单的返回一个"Hello World!"字符串）

当我们把这个web应用部署到uWSGI时，uWSGI会把接收到的请求按照指定协议解析，然后把解析的结果（譬如：HTTP各请求头数据）设置到environ变量中，接着按照WSGI规范回调web应用接口（uWSGI默认回调application函数，并且传递environ和start_response两个参数），最终web应用开始处理请求（各种数据库查询，各种函数调用...）并把结果返回给uWSGI

无论是webpy还是django，由于它们都是按照WSGI规范实现的web框架，所以一定提供了类似接口供web服务器回调，譬如webpy：
```python
        def wsgifunc(self, *middleware):                                                                             
            # ... 省略部分代码
            def wsgi(env, start_resp):
                self.load(env)
                # ... 省略部分代码
                result = self.handle_with_processors()
                status, headers = web.ctx.status, web.ctx.headers
                start_resp(status, headers)         
                return result
    
            # 类似java web中的filter概念
            for m in middleware: 
                wsgi = m(wsgi)
            return wsgi
```

uWSGI支持多种协议（包括HTTP协议），所以对于刚才例子，我们可以不使用nginx，而是直接把它当做HTTP服务器使用：
```sh
    # 注意这里的--http，表明采用http协议监听在80端口
    $ uwsgi --http 127.0.0.1:80 --wsgi-file simple_app.py --master --processes 2 --daemonize /var/log/uwsgi.log --pidfile /var/log/uwsgi.pid
    # 访问hello.htm
    $ curl http://127.0.0.1/hello.htm
    Hello world!
```

和Tomcat一样，由于nginx处理静态资源能力非常强悍，而且支持的并发数也高，同时能够提供负载均衡等功能，所以在生产环境中，我们通常采用nginx + uWSGI的方式部署python web应用，然后由nginx处理静态资源请求，对于“动态”请求，nginx**转发**给uWSGI处理:

    location / { 
        include uwsgi_params;                                                                                
        uwsgi_pass 127.0.0.1:9090;
    }   
    
所以这段配置就是告诉nginx：对于满足条件的请求，请使用uwsgi协议转发给127.0.0.1:9090 处理；看到这里你也许有3个问题：
 1. uwsgi_pass和proxy_pass有什么区别？
 2. 为什么要使用uwsgi协议转发？
 3. uWSGI与uwsgi什么关系？

问题1：proxy_pass指令也是把请求转发给其他服务器处理，但是默认采用HTTP协议（可以理解成，nginx收到什么，它就转发什么），而当使用uswgi_pass命令时，nginx会先把请求按照按照uwsgi协议转换（http -> wsgi），然后再转发给其他服务器处理；问题2：为什么要要使用uwsgi协议转发？这其实是从效率上考虑的，http协议本身是一个文本协议，虽然它对人很友好（可读性强），但是对计算机来说就不太友好了，解析起来非常耗时，所以在转发之前先把转换成其他协议（通常是二进制协议，譬如这里的uwsgi)；问题3：uWSGI是一个支持WSGI规范的web容器，它支持多种协议，其中一个就是uwsgi协议，所以uWSGI是两个完全不同的东西，只是名称相似而已;

至此，相信你对刚才那些配置已经非常清楚，而且无论是采用uWSGI或者flup部署web应用，又或者采用uwsgi协议还是fastcgi协议，其实它们的本质是一样的，只要我们结合效率以及方便性采取一种最适合的方式即可

顺便提一下uWSGI还提供了一个工具:uwsgitop命令，用来检测自身运行状态：

```
    # 下载安装文件：
    
    # 启动uWSGI，并添加--stats参数
    uwsgi ...  --stats 127.0.0.1:9191
    
    # 运行uwsgitop命令
    uwsgitop 127.0.0.1:9191
    
    # 你可以在另一个终端执行下面命令： for i in $(seq 100); do curl http://127.0.0.1/hello.htm; done，然后观察数据有何变化
```









    
    
