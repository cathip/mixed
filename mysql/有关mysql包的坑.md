# 有关mysql的坑
## 问题：centos pymysql安装失败 
- yum install mariadb-server mariadb
- yum install mysql-devel
- pip install mysqlclient

---

## 问题：ubuntu18.0 下mysql 安装后远程连不上

- 解决： 查看用户的权限，
- select User, Host, plugin from user;
- 是否是mysql_native_password，
- 如果不是，则将auth_sock改为mysql_native_password。
- 然后 flush privileges使更改生效，然后退出Mysql重新进入。

---

## 问题：mysql groupby用不了
- 解决方法：
-       select @@global.sql_mode;
-       set @@global.sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,
        NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,
        NO_ENGINE_SUBSTITUTION';
-       set global sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,
        NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,
        NO_ENGINE_SUBSTITUTION';
-       select @@sql_mode;
-       set sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,
        NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,
        NO_ENGINE_SUBSTITUTION';

## 问题： mysql存储emoji失败
- 字段字符集排序规则改为 utf8mb4_unicode_ci
- 前端encodeURIComponent转码存储 前端decodeURIComponent解码