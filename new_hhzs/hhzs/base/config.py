
#--------------------mysql--------------

# import platform
# #测试数据库
DBHOST = "129.211.136.124"
DBPORT = 3306
DBUSER = 'root'
DBPASSWD = 'hhzs999999'
DB = 'web_hhzs'

#正式数据
# DBHOST = 'cd-cdb-a9vh6zu6.sql.tencentcdb.com'
# DBPORT = 63656
# DBUSER = 'root'
# DBPASSWD = 'hhzs999999'
# DB = 'hhzs_2.0'


#数据库编码
DBCHAR = 'utf8mb4'
#连接池最小连接数
DB_MIN_CACHED = 10
#连接池最大连接数
DB_MAX_CACHED = 10
#连接池最大连接数
DB_MAX_SHARED = 20
#数据库最大连接数
DB_MAX_CONNECYIONS = 100

DB_BLOCKING = True

DB_MAX_USAGE = 0
#是否设置session
DB_SET_SESSION = None


#----------------------redis--------------------

#redis连接参数
#连接时间
SESSION_EXPIRE = 60
SESSION_TYPE = 'Redis'
#redis地址
REDIS_HOST = '129.211.136.124'
REDIS_PASSWD = ""
#redis端口
REDIS_PORT = 6379
#数据库
REDIS_DB = 0
