###ngx_http_rewrite_module

	syntax:	rewrite regex replacement [flag];
	default:	 —
	context:	server, location, if

如果一个uri与正则regex匹配，那么它将会被替换成replacement，并且在同一个配置文件中，连续出现的多个rewrite命令会依次执行，除非遇到特殊标记（譬如：last或者break）. 另外，若replacement是以"http://"或者"https://"开头，它同样会停止向下执行rewrite命令，然后重定向客户端到新的URL（隐式重定向）  

flag参数可选值：

 * last:  
 		停止向下执行rewrite命令并且用新URI查找相应location块
 * break:
 		停止向下执行rewrite命令
 * redirect:
 		返回302状态码，重定向客户端到新的URL（显式重定向标记）
 * permanent：
 		返回301状态码，重定向客户端到新的URL（显式重定向标记）

我们来看一个例子：

```sh
	server {
    ...
    rewrite ^(/download/.*)/media/(.*)\..*$ $1/mp3/$2.mp3 last;
    rewrite ^(/download/.*)/audio/(.*)\..*$ $1/mp3/$2.ra  last;
    return  403;
    ...
}
```

如果上述rewrite指令放在"/download/"location块中（如下面所示），那么必须使用break标记，而不是last，否则nginx会循环执行10次rewrite，然后返回500响应码

```sh
	location /download/ {
	    rewrite ^(/download/.*)/media/(.*)\..*$ $1/mp3/$2.mp3 break;
	    rewrite ^(/download/.*)/audio/(.*)\..*$ $1/mp3/$2.ra  break;
	    return  403;
	}
```

当正则中包含"}"或者";"这些字符时，整个正则表达式需要用单引号或者双引号括起来（因为那个两个字符在niginx配置文件中有特殊含义，不用引号括起来，会当做语法字符解析）

```sh
	syntax:	rewrite_log on | off;
	default:	
	rewrite_log off;
	context:	http, server, location, if
```
打开或关闭重写日志，一般仅在开发环境下打开，用于调试规则

```sh
	syntax:	set variable value;
	default:	 —
	context:	server, location, if
```
设置变量，变量的值可以是字符串，其他变量或者二者的组合

```sh
	syntax:	uninitialized_variable_warn on | off;
	default:	
	uninitialized_variable_warn on;
	context:	http, server, location, if
```
对于未初始化变量是否警告（默认打开，这样对于未初始化变量会在错误日志中提示）
