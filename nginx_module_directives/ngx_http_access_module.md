###Module ngx_http_access_module


    语法:   allow address | CIDR | unix: | all;
    默认值:   —
    环境:   http, server, location, limit_except
    
该指令用来设置允许访问的网络地址；

    语法:   deny address | CIDR | unix: | all;
    默认值:   —
    环境:   http, server, location, limit_except

该指令用来设置拒绝哪些网络地址

我们来看一个例子：
    
    location / {
        deny  192.168.1.1;
        allow 192.168.1.0/24;
        allow 10.1.1.0/16;
        allow 2001:0db8::/32;
        deny  all;
    }

**上述配置的含义是**：除了允许两个ipv4网络段地址：192.168.1.0/24（不包含192.168.1.1）和10.1.1.0/16以及一个ipv6网络段地址：2001:0db8::/32，拒绝所有来自其他地址的请求
