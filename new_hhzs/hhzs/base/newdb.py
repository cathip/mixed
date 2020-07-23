import pymysql
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

pymysql.install_as_MySQLdb()

import json

from base import config
from base.shop_base import callJson

import datetime

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

class Smart_Mysql(object):

    #开启事务
    @staticmethod
    def getConn():
        try:
            conn = pool.connection()
            return conn, conn.cursor()
        except Exception as e:
            print(f'-----获取数据库连接错误\n{e}')

    #执行语句
    @staticmethod
    def execute(sql, param, cursor, action):
        result = cursor.execute(sql, param)
        if (action == "query"):
            result = cursor.fetchall()
        if (action == "insert"):
            cursor.execute('SELECT @@IDENTITY AS id')
            result = cursor.fetchall()[0]['id']
        if (action == "update"):
            pass
        return result

    #运行方法
    @staticmethod
    def base(sql, param, dbCursor, action):
        try:
            result = []
            if dbCursor:
                result = Smart_Mysql.execute(sql, param, dbCursor, action)
            else:
                conn, cursor = Smart_Mysql.getConn()
                result = Smart_Mysql.execute(sql, param, cursor, action)
                conn.commit()
            return result
        except Exception as e:
            print(f'----执行sql出现错误\n{e}')
            cursor.close()
            raise e
        finally:
            if (not dbCursor):
                cursor.close()

    #查
    @staticmethod
    def query(sql, param=None, dbCursor=None):
        return Smart_Mysql.base(sql, param, dbCursor, action="query")

    #插入
    @staticmethod
    def insert(sql, param=None, dbCursor=None):
        return Smart_Mysql.base(sql, param, dbCursor, action="insert")

    #更新
    @staticmethod
    def update(sql, param=None, dbCursor=None):
        return Smart_Mysql.base(sql, param, dbCursor, action="update")

    #回滚
    @staticmethod
    def errdispose(conn, cursor):
        try:
            conn.rollback()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f'-------------事务回滚，关闭连接出现问题{e}')

    #提交
    @staticmethod
    def dispose(conn, cursor):
        try:
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f'-------------事务回滚，关闭连接出现问题{e}')