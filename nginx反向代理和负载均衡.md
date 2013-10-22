###反向代理

在生产环境中，我们通常使用nginx处理静态资源（譬如，图片或者静态网页），而对于一些动态请求，会让nginx把它转发给其他服务器处理（譬如Jboss，Tomcat等），并将它们的处理结果返回给客户端，这样nginx就充当了**反向代理**的角色， 那具体如何配置呢？

第一步：用python写一个简单的服务器程序（暂且称它为tiny_server），然后监听在9090端口：

```sh
    python tiny_server.py 127.0.0.1 9090 "Hello, Nginx"  # ip port msg
```

第二步：设置nginx反向代理，这里把所有请求都转发给tiny_server（可以利用正则只转发部分请求）

```sh	
	server {
		listen 80;

		location / {
			proxy_pass http://127.0.0.1:9090;	# 关键字 proxy_pass
		}
	}
```

第三步：启动tiny_server、nginx并访问：http://localhost/

```sh
    diaocow@ubuntu:~$ curl "http://localhost/"
    Hello, Nginx
```

###负载均衡

随着网站的访问量增加，一台机器可能无法支撑，这个时候我们可以配备一个集群来提供服务，并且使用nginx来提供负载均衡（即，当nginx接受到一个到动态请求，它会按照一定策略（譬如：轮询或者随机）从集群中选出一台机器处理请求）；那如何配置负载均衡呢？

第一步：配置集群列表（或称上游服务器）以及负载均衡策略

```sh	
	# backend是集群配置名，你可以自定义该名字
	upstream bcakend {		

		# server 定义提供服务机器ip & port，eg: server 10.20.155.37 8080
		server  机器1;	 
		server  机器2;		
		....
		
		# 默认负载均衡策略：轮询
	}
```

由于我们手头没有那么多测试机器，所以我们创建多个tiny_server监听在不同端口上：

```sh
	upstream backend {   
		server 127.0.0.1:9090;
		server 127.0.0.1:9091;				
	}
```

第二步： 设置反向代理
```sh
	server {
		listen 80;

		location / {
			proxy_pass http://backend;	# 关键字 proxy_pass
		}
	}
```

第三步: 启动（重启）nginx，并访问：http://localhost/，这时候发现两台提供服务的tiny_server确实被轮询了

```sh
	# 启动ting_server
	python tiny_server.py 127.0.0.1 9090 "hello, i am 9090"
	python tiny_server.py 127.0.0.1 9091 "hello, i am 9091"
	
	# 重载配置
	sudo nginx -s reload
	
	# 访问目标url 5遍
	diaocow@ubuntu:~$ for i in $(seq 5); do curl "http://localhost"; done
	hello, i am 9090
	hello, i am 9091
	hello, i am 9090
	hello, i am 9091
	hello, i am 9090    # 轮询结果
```


###负载均衡策略

**轮询**：这是nginx的默认策略，它会把请求依次转发给集群中每一台机器处理（如刚才示例所示），同时nginx还提供权重参数：weight，使得有些机器可以得到更多的处理机会（我们可以给性能高的机器配置较高的权重，给性能低的机器配置较低的权重）

```sh
    upstream backend {   
        server 127.0.0.1:9090 weight=2;
        server 127.0.0.1:9091;              
    }
```
这时候，如果发送了3个请求，那么第一台机器会有两次机会处理，第二台机器有一次机会：

```sh
    diaocow@ubuntu:~$ for i in $(seq 8); do curl "http://localhost"; done
    hello, i am 9091
    hello, i am 9090
    hello, i am 9090
    hello, i am 9091
    hello, i am 9090
    hello, i am 9090
    hello, i am 9091
    hello, i am 9090
```
若某一台机器处理请求时发生错误（譬如宕机），这时候nginx会把请求转发集群中给另一台机器，若还是发生错误，则继续向下转发直到成功（如果都处理失败，则把最后一台机器的处理结果返回给客户端）

根据ip地址哈希：nginx会根据客户端ip算出一个值key，然后与集群中机器数量取，接着把请求发到相应的机器上（这样同一个客户端总是访问固定的机器，这样能够实现某些特定需求）

```sh
    upstream backend {   
        server 127.0.0.1:9090;
        server 127.0.0.1:9091;    
        ip_hash;   # ip哈希策略
    }
```

如果我们使用了ip地址哈希策略，对于集群中要下线的机器不能直接删除配置，而是必须用down关键字标示出来，否则会造成客户端请求无法访问固定的机器（类似memcache，若不采用哈希一致性算法，则导致缓存全部失效）
```sh
    upstream backend {   
        server 127.0.0.1:9090;
        server 127.0.0.1:9091; 
        server 127.0.0.1:9092 down; # 标示这台机器已经下线
        ip_hash;
    }
```


