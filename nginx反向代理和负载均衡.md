###反向代理

在生产环境中，我们通常使用nginx处理静态资源（譬如，图片或者静态网页），而对于一些动态请求，会让nginx把它转发给其他服务器处理（譬如Jboss，Tomcat等），并将它们的处理结果返回给客户端，这样nginx就充当了**反向代理**的角色， 那具体如何配置呢？

第一步：用python写一个简单的服务器程序（暂且称它为tiny_server），然后监听在9090端口，启动命令：

```sh
	python tiny_server 127.0.0.1 9090 "Hello, Nginx!"  # ip port msg
```

第二步：设置nginx反向代理，把所有请求都转发给tiny_server（可以利用正则只转发部分请求）

```sh	
	server {
		listen 80;

		location / {
			proxy_pass http://127.0.0.1:9090;	# 关键字 proxy_pass
		}
	}
```

第三步：启动tiny_server、nginx并访问：http://localhost/



###负载均衡

随着网站的访问量增加，一台机器可能无法支撑，这个时候我们可以配备一个集群来提供服务，并且使用nginx来提供负载均衡（即，当nginx接受到一个到动态请求，然后按照一定策略（譬如：轮询或者随机）从集群中选出一台机器处理请求）；那如何配置负载均衡呢？

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
	upstream bcakend {   
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
	python tiny_server 127.0.0.1 9090 "hello, i am 9090"
	python tiny_server 127.0.0.1 9091 "hello, i am 9091"
	
	# 重载配置
	sudo nginx -s reload
	
	# 访问目标url
```
