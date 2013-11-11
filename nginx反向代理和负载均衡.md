-###反向代理
  
 -在生产环境中，我们通常使用nginx处理静态资源（譬如，图片或者静态网页），而对于一些动态请求，会让nginx把它转发给其他服务器处理（譬如Jboss，Tomcat等），并将它们的处理结果返回给客户端，这样nginx就充当了**反向代理**的角色， 那具体如何配置呢？
 -
 -第一步：用python写一个简单的服务器程序（暂且称它为tiny_server），然后监听在9090端口：
 +###配置
 +
 +webpy代码示例：hello.py
 +
 +```python
 +    #!/usr/bin/python
 +    import web
 +    
 +    urls = ("/.*", "hello")
 +    app = web.application(urls, globals())
 +    
 +    class hello:
 +        def GET(self):
 +            return 'Welcome to webpy!'
 +            
 +    # 这行代码非常重要
 +    application = app.wsgifunc()
 +```    
 +nginx配置：
  
  ```sh
 -    python tiny_server.py 127.0.0.1 9090 "Hello, Nginx"  # ip port msg
 -```
 -
 -第二步：设置nginx反向代理，这里把所有请求都转发给tiny_server（可以利用正则只转发部分请求）
 -
 -```sh  
 -  server {
 -    listen 80;
 -
 -    location / {
 -      proxy_pass http://127.0.0.1:9090;  # 关键字 proxy_pass
 -    }
 -  }
 -```
 -
 -第三步：启动tiny_server、nginx并访问：http://localhost/
 -
 +    server {
 +        listen 80; 
 +        location / { 
 +            include uwsgi_params;                                                                                
 +            uwsgi_pass 127.0.0.1:9090;
 +        }   
 +    }   
 +``` 
 +uWSGI配置：
  ```sh
 -    diaocow@ubuntu:~$ curl "http://localhost/"
 -    Hello, Nginx
 +    uwsgi --socket 127.0.0.1:9090  \         # 监听在指定端口
 +          --wsgi-file hello.py \             # 部署的web应用
 +          --master --processes 2 \           # 创建两个worker进程处理请求
 +          --daemonize /var/log/uwsgi.log \   # 后台运行uWSGI，并把日志输出到指定文件
 +          --pidfile /var/log/uwsgi.pid       # pid文件
 +```    
 +测试配置
 +```sh
 +    $ curl http://127.0.0.1/hello.htm
 +    Welcome to webpy!
 +```    
 +    
 +###原理分析：
 +看了上述的配置，你一定很好奇，刚才那些配置究竟起什么作用，uWSGI是什么东西，nginx又是如何转发请求的？
 +
 +类似java web中servlet规范，python web开发也有自己的规范——[WSGI](http://www.python.org/dev/peps/pep-3333/)，它定义了：**web应用（或者web框架）与web服务器交互接口**
 +        
 +而uWSGI就是一个支持WSGI规范的web服务器，也就是说你可以把你的web应用部署到uWSGI中，然后当它接受到请求时，会按照WSGI定义的接口回调web应用处理（这就根我们把java web应用部署到Tomcat，然后Tomcat按照servlet规范回调我们web应用一个道理！），现在我们就看一个按照WSGI规范实现的web应用：simple_app.py
 +```sh    
 +    def simple_app(environ, start_response):
 +        status = '200 OK'
 +        response_headers = [('Content-type','text/plain')]
 +        start_response(status, response_headers)
 +        return ['Hello world!\n']
 +    
 +    application = simple_app # 若web应用部署在uWSGI容器中，需要这行代码
 +```    
 +其中environ是一个dict类型变量，里面主要包含各种HTTP请求头数据（类似CGI的环境变量），start_response是web服务器提供给web应用的回调接口，用来接受HTTP响应码以及HTTP响应头；最终函数返回对请求的处理结果（这里只是简单的返回一个"Hello World!"字符串）
 +
 +当我们把这个web应用部署到uWSGI时，uWSGI会把接收到的请求按照指定协议解析，然后把解析的结果（譬如：HTTP各请求头数据）设置到environ变量中，接着按照WSGI规范回调web应用接口（uWSGI默认回调application函数，并且传递environ和start_response两个参数），最终web应用开始处理请求（各种数据库查询，各种函数调用...）并把结果返回给uWSGI
 +
 +无论是webpy还是django，由于它们都是按照WSGI规范实现的web框架，所以一定提供了类似接口供web服务器回调，譬如webpy：
 +```python
 +        def wsgifunc(self, *middleware):                                                                             
 +            # ... 省略部分代码
 +            def wsgi(env, start_resp):
 +                self.load(env)
 +                # ... 省略部分代码
 +                result = self.handle_with_processors()
 +                status, headers = web.ctx.status, web.ctx.headers
 +                start_resp(status, headers)         
 +                return result
 +    
 +            # 类似java web中的filter概念
 +            for m in middleware: 
 +                wsgi = m(wsgi)
 +            return wsgi
  ```
  
 -
 -默认情况下，反向代理是不会转发请求头中**原生**的Host字段，如果需要转发，必须加上：*proxy_set_header Host $host;*
 -
 +uWSGI支持多种协议（包括HTTP协议），所以对于刚才例子，我们可以不使用nginx，而是直接把它当做HTTP服务器使用：
  ```sh
 -  # 未加proxy_set_header配置
 -  GET / HTTP/1.0
 -  Host: xxxxx         # 这个值为配置项proxy_pass后的值
 -  User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1
 -  Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
 -  ...
 -
 -  # 添加proxy_set_header配置
 -  GET / HTTP/1.0
 -  Host: 127.0.0.1
 -  User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1
 -  Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
 -  ...
 +    # 注意这里的--http，表明采用http协议监听在80端口
 +    $ uwsgi --http 127.0.0.1:80 --wsgi-file simple_app.py --master --processes 2 --daemonize /var/log/uwsgi.log --pidfile /var/log/uwsgi.pid
 +    # 访问hello.htm
 +    $ curl http://127.0.0.1/hello.htm
 +    Hello world!
  ```
  
 -###负载均衡
 -
 -随着网站的访问量增加，一台机器可能无法支撑，这个时候我们可以配备一个集群来提供服务，并且使用nginx来提供负载均衡（即，当nginx接受到一个到动态请求，它会按照一定策略（譬如：轮询或者随机）从集群中选出一台机器处理请求）；那如何配置负载均衡呢？
 +和Tomcat一样，由于nginx处理静态资源能力非常强悍，而且支持的并发数也高，同时能够提供负载均衡等功能，所以在生产环境中，我们通常采用nginx + uWSGI的方式部署python web应用，然后由nginx处理静态资源请求，对于“动态”请求，nginx**转发**给uWSGI处理:
  
 -第一步：配置集群列表（或称上游服务器）以及负载均衡策略
 -
 -```sh  
 -  # backend是集群配置名，你可以自定义该名字
 -  upstream bcakend {    
 -
 -    # server 定义提供服务机器ip & port，eg: server 10.20.155.37 8080
 -    server  机器1;   
 -    server  机器2;    
 -    ....
 -    
 -    # 默认负载均衡策略：轮询
 -  }
 -```
 +    location / { 
 +        include uwsgi_params;                                                                                
 +        uwsgi_pass 127.0.0.1:9090;
 +    }   
 +    
 +所以这段配置就是告诉nginx：对于满足条件的请求，请使用uwsgi协议转发给127.0.0.1:9090 处理；看到这里你也许有3个问题：
 + 1. uwsgi_pass和proxy_pass有什么区别？
 + 2. 为什么要使用uwsgi协议转发？
 + 3. uWSGI与uwsgi什么关系？
  
 -由于我们手头没有那么多测试机器，所以我们创建多个tiny_server监听在不同端口上：
 +问题1：proxy_pass指令也是把请求转发给其他服务器处理，但是默认采用HTTP协议（可以理解成，nginx收到什么，它就转发什么），而当使用uswgi_pass命令时，nginx会先把请求按照按照uwsgi协议转换（http -> wsgi），然后再转发给其他服务器处理；问题2：为什么要要使用uwsgi协议转发？这其实是从效率上考虑的，http协议本身是一个文本协议，虽然它对人很友好（可读性强），但是对计算机来说就不太友好了，解析起来非常耗时，所以在转发之前先把转换成其他协议（通常是二进制协议，譬如这里的uwsgi)；问题3：uWSGI是一个支持WSGI规范的web容器，它支持多种协议，其中一个就是uwsgi协议，所以uWSGI是两个完全不同的东西，只是名称相似而已;
  
 -```sh
 -  upstream backend {   
 -    server 127.0.0.1:9090;
 -    server 127.0.0.1:9091;        
 -  }
 -```
 +至此，相信你对刚才那些配置已经非常清楚，而且无论是采用uWSGI或者flup部署web应用，又或者采用uwsgi协议还是fastcgi协议，其实它们的本质是一样的，只要我们结合效率以及方便性采取一种最适合的方式即可
  
 -第二步： 设置反向代理
 -```sh
 -  server {
 -    listen 80;
 +顺便提一下uWSGI还提供了一个工具:uwsgitop命令，用来检测自身运行状态：
  
 -    location / {
 -      proxy_pass http://backend;  # 关键字 proxy_pass
 -    }
 -  }
  ```
 -
 -第三步: 启动（重启）nginx，并访问：http://localhost/，这时候发现两台提供服务的tiny_server确实被轮询了
 -
 -```sh
 -  # 启动ting_server
 -  python tiny_server.py 127.0.0.1 9090 "hello, i am 9090"
 -  python tiny_server.py 127.0.0.1 9091 "hello, i am 9091"
 -  
 -  # 重载配置
 -  sudo nginx -s reload
 -  
 -  # 访问目标url 5遍
 -  diaocow@ubuntu:~$ for i in $(seq 5); do curl "http://localhost"; done
 -  hello, i am 9090
 -  hello, i am 9091
 -  hello, i am 9090
 -  hello, i am 9091
 -  hello, i am 9090    # 轮询结果
 +    # 下载安装文件：
 +    
 +    # 启动uWSGI，并添加--stats参数
 +    uwsgi ...  --stats 127.0.0.1:9191
 +    
 +    # 运行uwsgitop命令
 +    uwsgitop 127.0.0.1:9191
 +    
 +    # 你可以在另一个终端执行下面命令： for i in $(seq 100); do curl http://127.0.0.1/hello.htm; done，然后观察数据有何变化
  ```
  
  
 -###负载均衡策略
  
 -**轮询**：这是nginx的默认策略，它会把请求依次转发给集群中每一台机器处理（如刚才示例所示），同时nginx还提供权重参数：weight，使得有些机器可以得到更多的处理机会（我们可以给性能高的机器配置较高的权重，给性能低的机器配置较低的权重）
  
 -```sh
 -    upstream backend {   
 -        server 127.0.0.1:9090 weight=2;
 -        server 127.0.0.1:9091;              
 -    }
 -```
 -这时候，如果发送了3个请求，那么第一台机器会有两次机会处理，第二台机器有一次机会：
  
 -```sh
 -    diaocow@ubuntu:~$ for i in $(seq 8); do curl "http://localhost"; done
 -    hello, i am 9091
 -    hello, i am 9090
 -    hello, i am 9090
 -    hello, i am 9091
 -    hello, i am 9090
 -    hello, i am 9090
 -    hello, i am 9091
 -    hello, i am 9090
 -```
 -若某一台机器处理请求时发生错误（譬如宕机），这时候nginx会把请求转发集群中给另一台机器，若还是发生错误，则继续向下转发直到成功（如果都处理失败，则把最后一台机器的处理结果返回给客户端）
  
 -**根据ip地址哈希**：nginx会根据客户端ip算出一个值key，然后与集群中机器数量取，接着把请求发到相应的机器上（这样同一个客户端总是访问固定的机器，这样能够实现某些特定需求）
  
 -```sh
 -    upstream backend {   
 -        server 127.0.0.1:9090;
 -        server 127.0.0.1:9091;    
 -        ip_hash;   # ip哈希策略
 -    }
 -```
 -
 -如果我们使用了ip地址哈希策略，对于集群中要下线的机器不能直接删除配置，而是必须用down关键字标示出来，否则会造成客户端请求无法访问固定的机器（类似memcache，若不采用哈希一致性算法，则导致缓存全部失效）
 -```sh
 -    upstream backend {   
 -        server 127.0.0.1:9090;
 -        server 127.0.0.1:9091; 
 -        server 127.0.0.1:9092 down; # 标示这台机器已经下线
 -        ip_hash;
 -    }
 -```
  
