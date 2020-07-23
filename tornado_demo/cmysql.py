# coding=utf-8
# ! /home/ubuntu/work01/bin/python
import pymysql
from pymysql.cursors import DictCursor

pymysql.install_as_MySQLdb()
import config
from DBUtils.PooledDB import PooledDB


class Mysql(object):


    def __init__(self):
        self.__pool = None
        self._conn = self.__getConn()
        self._cursor = self._conn.cursor()

    def __getConn(self):
        if self.__pool is None:
            try:
                self.__pool = PooledDB(creator=pymysql, mincached=1, maxcached=100, host=config.DBHOST, port=config.DBPORT,
                                  user=config.DBUSER, passwd=config.DBPASSWD, db=config.DB, charset=config.DBCHAR,
                                  cursorclass=DictCursor)
                return self.__pool.connection()
            except Exception as e:
                print('-----获取数据库连接错误')
                print(e)

    def getAll(self, sql, param=None):
        try:
            if param is None:
                count = self._cursor.execute(sql)
            else:
                count = self._cursor.execute(sql, param)

            if count > 0:
                result = self._cursor.fetchall()
            else:
                result = None
        except Exception as e:
            print('------------获取所有结果集出现问题')
            print(e)
            result = False
        return result

    def getOne(self, sql, param=None):
        try:
            if param is None:
                count = self._cursor.execute(sql)
            else:
                count = self._cursor.execute(sql, param)

            if count > 0:
                result = self._cursor.fetchone()
            else:
                result = False
            return result
        except Exception as e:
            print('---------------获取单条数据出现问题')
            print(e)

    def getMany(self, sql, num, param=None):
        try:
            if param is None:
                count = self._cursor.execute(sql)
            else:
                count = self._cursor.execute(sql, param)

            if count > 0:
                result = self._cursor.fetchmany(num)
            else:
                result = False
            return result
        except Exception as e:
            print('--------------获取多条数据出现问题')
            print(e)

    def __getInsertId(self):
        try:
            self._cursor.execute('SELECT @@IDENTITY AS id')
            result = self._cursor.fetchall()
            return result[0]['id']
            # return result
        except Exception as e:
            print('------------获取影响的记录的id')
            print(e)

    def insertOne(self, sql):
        try:
            self._cursor.execute(sql)
            return self.__getInsertId()
        except Exception as e:
            print('-------------插入一条数据出现问题')
            print(e)
            return False

    def insertMany(self, sql, values):
        try:
            count = self._cursor.execute(sql, values)
            return count
        except Exception as e:
            print('--------------插入多条数据出现问题')
            print(e)

    def update(self, sql, param=None):
        try:
            return self.__query(sql, param)
        except Exception as e:
            print('--------------更新出现问题')
            print(e)
            return False

    def __query(self, sql, param=None):
        try:
            if param is None:
                count = self._cursor.execute(sql)
            else:
                count = self._cursor.execute(sql, param)
            return count
        except Exception as e:
            print('-------------获取影响的id，出现问题')
            print(e)

    def delete(self, sql, param=None):
        try:
            id = self.__query(sql, param)
            return id
        except Exception as e:
            print('--------删除语句，出现问题')
            print(e)

    def begin(self):
        try:
            self._conn.autocommit(1)
        except Exception as e:
            print('------------------开启事务，出现问题')
            print(e)

    def end(self, option='commit'):
        try:
            if option == 'commit':
                self._conn.commit()
            else:
                self._conn.rollback()
        except Exception as e:
            print('-----------------结束事务，出现问题')
            print(e)

    def errdispose(self, isEnd=1):
        try:
            if isEnd == 1:
                self.end('roollback')
            self._cursor.close()
            self._conn.close()
        except Exception as e:
            print('-------------事务回滚，关闭连接出现问题')
            print(e)

    def dispose(self, isEnd=1):
        try:
            if isEnd == 1:
                self.end('commit')
            else:
                self.end('roolback')
            self._cursor.close()
            self._conn.close()
        except Exception as e:
            print('----------------释放资源出现问题')
            print(e)

    def isexist(self, sql, param=None):
        try:
            if param is None:
                result = self._cursor.execute(sql)
            else:
                result = self._cursor.execute(sql, param)
            return result
        except Exception as e:
            print('--------------判断记录是否存在出现问题')
            print(e)
            return 0

