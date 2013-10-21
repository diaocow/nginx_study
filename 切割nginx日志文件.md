### 切割nginx日志文件

nginx默认把日志都输出都到一个文件中，随着网站访问量不断增加，日志文件不断膨胀，这样会导致日后非常难定位某天某段时间日志并对其进行分析，因此我们需要这么一个脚本，它完成下面几件事情：

 * 按天分割日志；
 * 用当前日期重命名日志文件；  
 * 通知nginx重新生成一份新的日志文件；
 
脚本内容如下：

```sh
    #!/bin/bash
    #
    ########################################
    #
    # 每天00：00定时备份nginx日志文件
    #
    ########################################
    
    # nginx日志存放目录（这个变量需要自定义配置）
    NGINX_LOG_PATH="/home/diaocow/nginx_log"
    
    # 分割后的日志存放目录：.../${log_year}/${log_month}
    NGINX_BACK_LOG_PATH=${NGINX_LOG_PATH}/$(date -d "yesterday" +%Y)/$(date -d "yesterday" +%m)
    
    # 分割后的日志文件名
    NGINX_BACK_LOG_NAME=$(date -d "yesterday" +%Y%m%d)_access.log
    
    # 1. 创建目标目录
    mkdir -p ${NGINX_BACK_LOG_PATH} 
    
    # 2. 重命名老的日志文件
    mv ${NGINX_LOG_PATH}/access.log ${NGINX_BACK_LOG_PATH}/${NGINX_BACK_LOG_NAME} 
    
    # 3. 通知nginx重新打开一个新的日志文件
    nginx -s reopen   # 该命令等价于：kill -USR1 `cat .../nginx.pid`
```

最后我们只要使用crontab命令定时（每天凌晨00:00）执行这个脚本即可，脚本执行效果如下:

>.  
>├── 2013  
>│   └── 10  
>│       └── 20131020_access.log  
>├── access.log  


关于crontab命令可以参看我之前总结的一篇文章：http://diaocow.iteye.com/admin/blogs/1620541

----

本文内容参考张宴《实战Nginx》3.3.3节


