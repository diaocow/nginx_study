###ngx_http_rewrite_module

    语法:	rewrite regex replacement [flag];
	默认值:	 —
	环境:	server, location, if

如果一个URI与正则regex匹配，那么它将会被替换成replacement（一个新的URI）；当配置文件中连续出现多个rewrite命令，默认情况它们会被依次执行（除非遇到特殊标记，譬如：last或者break），最终生成的新URI会去重新查找对应location块（这一循环查找过程最多重复10次，否则nginx会返回500错误）；

flag参数可选值：

 * last - 停止执行后面的rewrite命令，并用新URI重新查找对应的location块
 * break - 停止执行后面的rewrite命令，顺序向下执行location块中其他命令
 * redirect - 返回302状态码，重定向客户端到新的URI（显式重定向标记）
 * permanent - 返回301状态码，重定向客户端到新的URI（显式重定向标记）

若replacement是以"http://"或者"https://"开头，那么它的效果等价于redirect标记（隐式重定向）；

当last或者break标记随rewrite命令出现在server块中，它们是等价的，但出现在location块中，则完全不同；

当正则中包含"}"或者";"这些字符时，整个正则表达式需要用单引号或者双引号括起来（因为这两个字符在niginx配置文件中有特殊含义，不用引号括起来，会当做语法字符解析）；


	语法:	rewrite_log on | off;
	默认值:	rewrite_log off;
	环境:	http, server, location, if

打开或关闭重写日志，一般仅在开发环境下打开，用于调试规则（注意：重写日志默认是notice级别）

	语法:	set variable value;
	默认值:	 —
	环境:	server, location, if

设置变量，变量的值可以是字符串，其他变量或者二者的组合

	语法:	uninitialized_variable_warn on | off;
	默认值:	uninitialized_variable_warn on;
	环境:	http, server, location, if

对于未初始化变量是否警告（默认打开，这样对于未初始化变量会在错误日志中提示）

---

关于rewrite命令，推荐阅读：http://eyesmore.iteye.com/blog/1142162
