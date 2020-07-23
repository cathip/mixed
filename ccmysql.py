from DBUtils.PooledDB import PooledDB
from base import config
import pymysql
from pymysql.cursors import DictCursor

pymysql.install_as_MySQLdb()


class Smart_Mysql(object):


    #开启事务
    @staticmethod
    def getConn():
        try:
            pool = PooledDB(creator=pymysql, 
                            mincached=1, 
                            maxcached=100, 
                            host=config.DBHOST, 
                            port=config.DBPORT,
                            user=config.DBUSER, 
                            passwd=config.DBPASSWD, 
                            db=config.DB, 
                            charset=config.DBCHAR,
                            cursorclass=DictCursor)
            conn = pool.connection()
            return conn, conn.cursor()
        except Exception as e:
            print(f'-----获取数据库连接错误\n{e}')

    @staticmethod
    def execute(sql, param, cursor, action):
        result = cursor.execute(sql, param)
        if (action == "query"):
            result = cursor.fetchall()
        if (action == "insert"):
            cursor.execute('SELECT @@IDENTITY AS id')
            result = cursor.fetchall()[0]['id']
        return result

    @staticmethod
    def base(sql, param, dbCursor, action):
        try:
            if (dbCursor):
                result = Smart_Mysql.execute(sql, param, dbCursor, action)
            else:
                conn, cursor = Smart_Mysql.getConn()
                result = Smart_Mysql.execute(sql, param, cursor, action)
                conn.commit()
            return result
        except Exception as e:
            print(f'-----获取数据库连接错误\n{e}')
            return False
        finally:
            if (not dbCursor):
                cursor.close()

    @staticmethod
    def query(sql, param=None, dbCursor=None):
        return Smart_Mysql.base(sql, param, dbCursor, action="query")

    @staticmethod
    def insert(sql, param=None, dbCursor=None):
        return Smart_Mysql.base(sql, param, dbCursor, action="insert")

    @staticmethod
    def update(sql, param=None, dbCursor=None):
        return Smart_Mysql.base(sql, param, dbCursor, action="update")

    @staticmethod
    def errdispose(conn, cursor):
        try:
            conn.rollback()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f'-------------事务回滚，关闭连接出现问题{e}')

    @staticmethod
    def dispose(conn, cursor):
        try:
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f'-------------事务回滚，关闭连接出现问题{e}')
