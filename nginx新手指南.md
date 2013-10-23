###nginx 概述

 * nginx是一个基于事件模型并且依赖于操作系统特性的服务器（譬如，在linux平台我们可以使用epoll来提高请求处理能力）；
 
 * nginx启动时通常会创建一个master进程和多个worker进程，其中master进程主要用来读取，加载配置文件以及管理worker进程，而work进程则是用来处理客户端请求；  

 * worker进程的数目可以在配置文件中指定，建议使用机器的cpu数作为worker进程数
  
  


###nginx 启动，关闭止以及重载配置
启动nginx服务器：

    nginx     
    nginx -c nginx_conf_path

第一个命令使用默认配置文件（通常是: /etc/nginx/nginx.conf）启动nginx，而第二个命令使用自定义配置文件启动nginx  

关闭nginx服务器：

    nginx -s stop --- 暴力的关闭服务器
    nginx -s quit --- 安全的关闭服务器

上面的两个命令的区别在于，第二个命令会让nginx处理完当前正在处理的请求，然后关闭服务器

有时候nginx正在运行，然后我们因为某些问题修改了配置文件，这时候我们希望新配置立即生效该怎么办呢？ 显然我可以们先关闭然后重新启动服务器（这时候它会加载到新的配置），但这种做法太麻烦，而且会在短时间内造成服务不可用（若没有集群）  
  
nginx本身提供了一种优雅的方式，使用下列命令，可以动态加载新配置：

    nginx -s reload
    
一旦master进程收到该信号（重载），它首先检查新配置语法的正确性，然后尝试加载它；如果一切OK，master开始用新配置去创建新的worker进程，并且告诉老的worker进程：嗨，哥么，你处理完手头的事就可以闪了；worker进程收到master程发来的该消息就会处理完正在处理的请求然后退出，之后nginx就以新配置状态运行

###nginx 提供静态资源服务
web服务器的一个重要功能就是提供静态资源服务（譬如：图片和静态网页），下面我们将编写一些配置代码，使得nginx可以提供静态资源服务

第一步：在你的机器上创建/data/www和/data/images目录，然后再这两个目录中分别添加index.html和hello.jpg文件（图片名随便） 

第二步：打开配置文件（假设是nginx.conf），然后添加下面代码：

    http {
        server {
        }
    }

通常一个配置文件会包含多个server块（都内嵌在http块中），每一个server块都表示一个虚拟主机，并且这些虚拟主机有server块中的listen和server_names字段区分。一旦nginx决定使用使用哪个server块来处理请求，它将会把请求URI和server块中的location块做进一步比较  

第三步：在server块中添加location块：
    
    server {
        listen 8080;
        location / {
            root /data/www;
        }
        
        location /images/ {
            root /data;
        }
    }

若第一个location块中的"/"前缀与当前请求URI匹配（很显然匹配，任何URI都是以"/"开始），则执行location块中的命令：root；root命令用来替换根路径，也就是说你访问/index.html，在这里会被替换成/data/www/index.html  

在一个server块内可以定义多个location块，假如一个URI匹配多个location块，那么nginx将会选择那个匹配最长前缀的location块，譬如：访问/images/hello.jpg，它同时匹配两个location块（"/"和"/images/"），nginx会选择较长匹配的那个，也就是第二个location块，并且执行其中的root命令，于是请求URI被替换成：/data/images/hello.jpg

配置已经完成，赶紧试一试吧（若nginx已经在运行，可以使用nginx -s reload命令重载配置）


###nginx 代理服务器
nginx经常被用作反向代理服务器，对于一些动态请求，nginx会把它转发给那些被代理的服务器（也叫上游服务器，譬如JBOSS，Tomcat等），然后把它们处理的结果再返回给客户端；那如何配置反向代理呢？  

[反向代理设置](https://github.com/diaocow/nginx_study/blob/master/nginx%E5%8F%8D%E5%90%91%E4%BB%A3%E7%90%86%E5%92%8C%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1.md)

---
本文大部分内容来源：http://nginx.org/en/docs/beginners_guide.html
