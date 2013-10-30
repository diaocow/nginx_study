##ngx_http_rewrite_module

####rewrite命令


    	语法:    rewrite regex replacement [flag];
	默认值:	 —
	环境:	server, location, if

如果一个URI与正则regex匹配，那么它将会被替换成replacement（一个新的URI）；当配置文件中连续出现多个rewrite命令，默认情况它们会被依次执行（除非遇到特殊标记，譬如：last或者break），最终生成的新URI会去重新查找对应location块（这一循环查找过程最多重复10次，否则nginx会返回500错误）；

flag参数可选值：

 * last：停止执行后续命令，并用新URI重新查找对应的location块 ； 
        
 * break：继续向下执行location块中的其他命令，但是跳过属于ngx_http_rewrite_module指令集中的命令（譬如：return， rewrite等）；  
       
 * redirect：重定向客户端到新的URI，并返回302状态码（显式重定向标记）；  
            
 * permanent：重定向客户端到新的URI，并返回301状态码（显式重定向标记）；

若replacement是以"http://"或者"https://"开头，那么它的效果等价于redirect标记（隐式重定向）；

当last或者break标记随rewrite命令出现在server块中，它们是等价的，但出现在location块中，则完全不同（如之前所述）；

当正则中包含"}"或者";"这些字符时，整个正则表达式需要用单引号或者双引号括起来（因为这两个字符在niginx配置文件中有特殊含义，不用引号括起来，会当做语法字符解析）；

下面我们看个例子，具体看下break标记和last区别：

```sh
	server {
        listen 80; 
        root /home/diaocow;         

        location /aaa  {
            rewrite ^/aaa.htm$ /bbb.htm;
            rewrite ^/bbb.htm$ /ccc.htm break;
            return 200 hello_world;  # 若break条件匹配，该命令被跳过
        }   

        location /bbb {
            rewrite ^/bbb.htm$ /ccc.htm last;
            rewrite ^(.*)$ /bbb/loop.htm ; # 若last条件匹配，该命令被跳过，否则死循环，然后500错误                                                               
        }   
        location / { 
        }   
    }   
```
我们测试不同URI，看下执行结果：
```sh
	$ curl http://127.0.0.1/aaa.htm
	I am ccc.htm
	$ curl http://127.0.0.1/aaa_other.htm
	hello_world
	$ curl http://127.0.0.1/bbb.htm
	I am ccc.htm
	$ curl http://127.0.0.1/bbb_other.htm
	<html>
	<head><title>500 Internal Server Error</title></head>
	<body bgcolor="white">
	<center><h1>500 Internal Server Error</h1></center>
	<hr><center>nginx/1.1.19</center>
	</body>
	</html>
```

####rewrite_log命令
	语法:	rewrite_log on | off;
	默认值:	rewrite_log off;
	环境:	http, server, location, if

打开或关闭重写日志，一般仅在开发环境下打开，用于调试rewrite规则（注意：重写日志是notice级别）

####set命令
	语法:	set variable value;
	默认值:	 —
	环境:	server, location, if

设置变量，变量的值可以是字符串，其他变量或者二者的组合
```sh
	server {
		listen 80;
		
		set $return_info "hello, diacow!";    # 设置return_info变量                                                                   
		location / {
		    return 200 $return_info;
		}   
	}   
	
	上述配置执行结果：
	$ curl http://127.0.0.1/
	hello, diacow!
```

####uninitialized_variable_warn命令

	语法:	uninitialized_variable_warn on | off;
	默认值:	uninitialized_variable_warn on;
	环境:	http, server, location, if

对于未初始化变量是否警告（默认打开，这样对于未初始化变量会在错误日志中提示）

---

关于rewrite命令，推荐阅读：http://eyesmore.iteye.com/blog/1142162
