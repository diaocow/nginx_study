nginx 缓存有两种方式：

###proxy_store:
配置：
```sh
    server {
        listen 80; 

        location / { 
            root /home/diaocow/data;                                                                             
            error_page 404 = @proxy;
        }   
        location @proxy {
            proxy_pass http://127.0.0.1:9090;
            proxy_store on; 
            proxy_store_access user:rw group:rw all:r;
            proxy_temp_path /home/diaocow/tmp;
            root /home/diaocow/data;
        }   
    } 
```

测试（这里的[部署方式](https://github.com/diaocow/nginx_study/blob/master/Nginx%20%2B%20uWSGI%20%2B%20Webpy%E9%85%8D%E7%BD%AE%26%E5%8E%9F%E7%90%86.md)采用了uwsgi，你可以随便使用你喜欢的方式测试）：

```sh
    # 启动web应用并访问
    $ uwsgi --http 127.0.0.1:9090 \
            --wsgi-file simple_app.py \
            --master --processes 2 \
            --daemonize /var/log/uwsgi.log \
            --pidfile /var/log/uwsgi.pid
            
    $ curl http://127.0.0.1/hello.htm
    Hello world!
    # 停止应用再次访问
    $ kill -9 `cat /var/log/uwsgi.pid`
    $ curl http://127.0.0.1/hello.htm
    Hello world!
```

从结果来看，你会发现当我们停止web应用时，nginx依然能够返回内容（如这里的Hello world!），这就是proxy_store作用，它会把：**反向代理的处理结果保存下来**，你可以通过root或者alias命令来指定缓存保存位置（再或者直接通过path参数指定），在刚才的配置中我们指定的保存目录是：/home/diaocow/data：

```sh
    $ tree /home/diaocow/data
    /home/diaocow/data
    └── hello.htm

    0 directories, 1 file
    $ cat /home/diaocow/data/hello.htm 
    Hello world!
```

啊哈，原来nginx把反向代理结果保存到一个文件中，并且文件名就是URI；看到这里我想你对刚才配置的含义已经非常清楚了：它告知nginx，如果指定的资源没有找到（404），然么转发给其他服务器处理并且把返回结果保存下来，这样对于下次同样的URI请求nginx将直接从缓存文件中获取，大大提高了请求处理速度；

当你搞清楚proxy_store的执行原理后，很显然你会发现如果作为缓存，你无法控制何时失效（你可以手动写个脚本，定时删除缓存目录），所以proxy_store功能更像是一个“镜像”（最后补充一点：选用何种xxx_store要根据你反向代理使用的协议，如果使用的是uwsgi转发协议，那么你就要使用uwsgi_store命令）







    
    





