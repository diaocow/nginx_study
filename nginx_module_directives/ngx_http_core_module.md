###ngx_http_core_module

    
    语法: location [ = | ~ | ~* | ^~ ] uri { ... }
    默认值:   —
    环境: server, location
    
nginx提供两种规则来进行location匹配：

 * 文本字符串（literal strings）匹配
 * 正则（regular expressions）匹配
 
若需要使用正则匹配，则必须使用下列前置运算符：

 * ~  忽略大小写的正则匹配
 * ~* 大小写敏感的正则匹配

为了确定哪个location块与当前URI匹配，nginx需要进行一系列比较： 
首先它会进行文本字符串匹配，文本字符串的匹配规则是：**最大前缀匹配**，也就是说，nginx会把所有文本字符串都与URI比较一遍，然后确定最符合条件的那个，接着执行正则匹配，正则匹配的规则是：按照正则在配置文件中出现的顺序，依次比较，并且当遇到**第一个**匹配的正则时，该正则所在location块将作为此次匹配过程的**最终结果**，否则使用之前文本字符串的匹配结果；这里有两点需要注意：

 * 正则匹配在文本字符串匹配之后进行；
 * 只有当任何一个正则都不与URI匹配时，才会使用文本字符串匹配结果作为此次匹配过程的最终结果；

在文本字符串匹配中，nginx提供了一些运算符：= 和 ^~，使得当文本字符串与URI匹配时，nginx不会继续后面的正则匹配，也就是说，如果匹配出来的结果（按照最大前缀匹配规则）使用了 = 或者 ^~ 运算符，那么nginx直接用它所在的location块作为匹配过程的最终结果

对于 = 运算符，它的匹配规则更加严格，它要求精确匹配，若某一个文本字符串与URI精确匹配（一模一样），则它一定也是最大匹配前缀，所以该规则并不和最大前缀匹配规则冲突；

在nginx的早期版本中（0.7.1 - 0.8.41），即使你没有使用这些运算符，但是如果匹配出来最大前缀与URI一模一样，那么nginx也会停止后面的正则匹配

说了这么多理论，我们来看个例子（nginx版本：1.1.19）：

```sh
    server {
        listen 80; 
        location  /test {
            echo "hello_1";
        }   
        location ^~ /test/hello {
            echo "hello_2";
        }   
        location  = /test/hello.htm {
            echo "hello_3";
        }   
        location  /test/hello_world.htm {
            echo "hello_4";
        }   
        location  ~ /test/hell.* {                                                                               
            echo "hello_5";
        }   
    }   
```
测试不同的URI
```sh
    $ curl http://127.0.0.1/test/hello.htm
    hello_3
    $ curl http://127.0.0.1/test/hellooo.htm
    hello_2
    $ curl http://127.0.0.1/test/hello_world.htm  # 在早期版本，这里可能返回hello_4
    hello_5
    $ curl http://127.0.0.1/test/helllll.htm
    hello_5
    $ curl http://127.0.0.1/test/nginx.htm
    hello_1
```

如果你能清晰的分析出执行逻辑，那么我想你对location匹配过程已经非常清楚了 ^_^
