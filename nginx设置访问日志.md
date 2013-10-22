###设置日志存储路径
access_log  path  format

 * path      定义服务器访问日志存放路径
 * format    定义日志格式，这是一个可选参数，默认采用combined格式

例如：

    access_log /nginx_log/access.log combined;
    
上面配置定义了：服务器访问日志保存在nginx目录中的access.log文件，并且日志格式采用combined（如果采用默认日志格式，可以忽略format参数）


###设置日志格式

nginx默认提供了一种日志格式combined：

    log_format combined '$remote_addr - $remote_user [$time_local]  '
                        '"$request" $status $body_bytes_sent '
                        '"$http_referer" "$http_user_agent"';
    

按照上述格式输出的一条日志

    127.0.0.1 - - [21/Oct/2013:15:38:02 +0800] "GET /hello.html HTTP/1.1" 304 0 "-" "Mozilla/5.0     (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/28.0.1500.52 Chrome/28.0.1500.52 Safari/537.36"
    
我们也可以定义自己的日志格式（这样可以方便我们使用一些命令（譬如awk)分析日志）:

    log_format my_log_name ...  
    
    log_format diaocow_log  '[$remote_addr]==[$remote_user]==$[time_local]=='
                            '[$request]==$[status]==[$body_bytes_sent]==
                            '[$http_referer]==[$http_user_agent]';
                        
这时候输出的日志格式将会变成

    [127.0.0.1]==[-]==[21/Oct/2013:16:57:36 +0800]==[GET /favicon.ico HTTP/1.1]==[404]==[200]==[-]==[Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/28.0.1500.52 Chrome/28.0.1500.52 Safari/537.36]

这样我们就可以使用awk命令清晰的分割出每一个字段，譬如： awk -F '=='  {print $1}


    


