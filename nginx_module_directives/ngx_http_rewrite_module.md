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
	...
	<head><title>500 Internal Server Error</title></head>
	... 省略
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

####return命令

    语法:   return code [text];
            return code URL;
            return URL;
	默认值:	 —
	环境:	server, location, if

return 命令用来停止后续指令的处理，并使用code作为响应码返回客户端，其中: return code [text] 允许使用一段文本作为响应体返回（如之前例子中所示），特别要注意的是，若你明确希望返回一段文本内容给客户端，那code不能是301， 302，303和307，否则nginx会尝试把这段文本当做一个URI进行重定向；而 return code URL 则用来实现重定向功能（注意这里的code必须为：301，302，303和307中的一种），而且若URL不是以：http://...开头（即可能只是一个URI），则nginx会智能补全URL（使用当前请求协议，主机名以及端口）；最后一种形式：return URL同样可以实现重定向功能，但nginx默认返回302响应码（注意，这里的URL必须是完整格式，nginx不会做智能补全，而是报语法错误：invalid return code）

关于return命令，请看[if命令](https://github.com/diaocow/nginx_study/blob/master/nginx_module_directives/ngx_http_rewrite_module.md#if%E5%91%BD%E4%BB%A4)中的例子

####if命令

    语法:   if (condition) { ... }
    默认值:	 —
	环境:	server, location

该命令类似一般编程语言中的if语句，也就是说，如果condtion条件为真，那么nginx会执行位于if块中的指令；

if中的condition条件可以是以下几种形式：

 * 变量：如果变量的值一个空串或者为"0"，那么为false，否则为true;
 * 比较表达式：使用 = 或者 != 进行字符串比较；
 * 正则表达式：使用 ~ (!~) 或者 ~* (!~*) 进行正则匹配，其中~* 表示忽略大小写的正则匹配；
 * 检测文件是否存在： -f 或者 !-f
 * 检测目录是否存在： -d 或者 !-d
 * ...

我们来看个例子：
```sh
	server {
		listen 80;
		location / {
		    if ($request_uri = "/hello.htm") {
		        set $return_info "hello, world!";                                                                
		    }
		    if ($request_uri = "/per_redirect.htm") {
		        return 301 /redirect_hello.htm;
		    }
		    if ($request_uri ~ \.(gif|jpg)$) {
		        set $return_info "Oh, sorry, I don't serve pictures'";
		    }
		    return 200 $return_info;
		}
		location ~ redirect_hello {
		    return 200  'Oh, You redirect here!';
		}
	}
	
	执行结果：
	
	$ curl http://127.0.0.1/hello.htm
	hello, world!
	$ curl http://127.0.0.1/hello.jpg
	Oh, sorry, I don't serve pictures
	$ curl http://127.0.0.1/per_redirect.htm
	....
	<head><title>301 Moved Permanently</title></head>
	# ... 若在浏览器中访问http://127.0.0.1/per_redirect.htm，这时候会显示重定向内容：Oh, You redirect here!
```
另外，nginx不推荐使用if指令（[ifIsEvil](http://wiki.nginx.org/IfIsEvil)），应当优先选择使用tryfiles命令来替代if；

---

关于rewrite命令，推荐阅读：http://eyesmore.iteye.com/blog/1142162
