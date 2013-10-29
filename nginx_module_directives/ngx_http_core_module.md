###ngx_http_core_module

    
    语法: location [ = | ~ | ~* | ^~ ] uri { ... }
    默认值:   —
    环境: server, location
    
nginx提供两种规则来进行URI匹配：

 * 文本字符串（literal strings）匹配
 * 正则（regular expressions）匹配
 
若需要使用正则匹配，则必须使用下列前置运算符：

 * ~  忽略大小写的正则匹配
 * ~* 大小敏感的正则匹配

为了确定哪个location块与当前URI匹配，nginx需要进行一系列比较；首先进行文本字符串匹配，文本字符串匹配规则是：最大前缀匹配，也就是说，nginx会把所有文本符串都匹配一遍，来确定最符合条件的那个location块，接着执行正则匹配，nginx会按照正则在配置文件中出现的顺序，依次比较，并且当遇到**第一个**匹配的正则时，该location块将作为此次匹配过程的**最终结果**，否则使用之前文本字符串的匹配结果；这里需要注意的两点是：

 * 正则匹配在文本字符串匹配之后进行；
 * 只有当没有一个正则与URI匹配时，才会使用文本字符串匹配结果作为此次匹配过程的最终结果；

在文本字符串匹配中，nginx提供了一些运算符，使得当文本字符串与URI匹配时，nginx不会继续后面的正则匹配：

 * = ： 要求精确匹配
 * ^~  

也就说，若匹配出来的**最大匹配前缀**所在的location块，使用了= 或者 ^~运算符，那么nginx直接用该location块作为匹配过程的最终结果（在早期版本：0.7.1 to 0.8.41，即使你没有使用这些运算符，但是匹配出来最大前缀与URI一模一样，那么nginx也会停止后面的正则匹配）

说了这么多理论，我们看个例子，加强理解：

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
测试这段配置（nginx版本：1.1.19）：

```sh
    diaocow@diaocow-pc:~$ curl http://127.0.0.1/test/hello.htm
    hello_3
    diaocow@diaocow-pc:~$ curl http://127.0.0.1/test/hellooo.htm
    hello_2
    diaocow@diaocow-pc:~$ curl http://127.0.0.1/test/hello_world.htm
    hello_5
    diaocow@diaocow-pc:~$ curl http://127.0.0.1/test/helllll.htm
    hello_5
    diaocow@diaocow-pc:~$ curl http://127.0.0.1/test/nginx.htm
    hello_1

```
