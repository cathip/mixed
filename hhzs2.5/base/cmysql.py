# coding=utf-8
# ! /home/ubuntu/work01/bin/python

from hhsc2019.settings import pool

class Mysql(object):

    def __init__(self):
        self._conn = self.__getConn()
        self._cursor = self._conn.cursor()

    def __getConn(self):
        try:
            return pool.connection()
        except Exception as e:
            print('-----获取数据库连接错误')
            print(e)
            raise e

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
            raise e

    def __getInsertId(self):
        try:
            self._cursor.execute('SELECT @@IDENTITY AS id')
            result = self._cursor.fetchall()
            return result[0]['id']
        except Exception as e:
            print('------------获取影响的记录的id')
            print(e)
            raise e

    def getAll(self, sql, param=None):
        try:
            if param is None:
                count = self._cursor.execute(sql)
            else:
                count = self._cursor.execute(sql, param)

            result = []
            if count > 0:
                result = self._cursor.fetchall()
            return result

        except Exception as e:
            print('------------获取所有结果集出现问题')
            print(e)
            result = False
            raise e

    def getOne(self, sql, param=None):
        try:
            if param is None:
                count = self._cursor.execute(sql)
            else:
                count = self._cursor.execute(sql, param)
            result = {}
            if count > 0:
                result = self._cursor.fetchone()
            return result
        except Exception as e:
            print('---------------获取单条数据出现问题')
            print(e)
            raise e

    def getMany(self, sql, num, param=None):
        try:
            if param is None:
                count = self._cursor.execute(sql)
            else:
                count = self._cursor.execute(sql, param)
            
            result = []
            if count > 0:
                result = self._cursor.fetchmany(num)
            return result
        except Exception as e:
            print('--------------获取多条数据出现问题')
            print(e)
            raise e

    def insertOne(self, sql, param=None):
        try:
            if param is None:
                self._cursor.execute(sql)
            else:
                self._cursor.execute(sql, param)
            return self.__getInsertId()
        except Exception as e:
            print('-------------插入一条数据出现问题')
            print(e)
            raise e

    def insertMany(self, sql, values):
        try:
            count = self._cursor.execute(sql, values)
            return count
        except Exception as e:
            print('--------------插入多条数据出现问题')
            print(e)
            raise e

    def update(self, sql, param=None):
        try:
            return self.__query(sql, param)
        except Exception as e:
            print('--------------更新出现问题')
            print(e)
            raise e

    def delete(self, sql, param=None):
        try:
            del_id = self.__query(sql, param)
            return del_id
        except Exception as e:
            print('--------删除语句，出现问题')
            print(e)
            raise e

    def begin(self):
        try:
            self._conn.autocommit(0)
        except Exception as e:
            print('------------------开启事务，出现问题')
            print(e)
            raise e

    def end(self, option='commit'):
        try:
            if option == 'commit':
                self._conn.commit()
            else:
                self._conn.rollback()
        except Exception as e:
            print('-----------------结束事务，出现问题')
            print(e)
            raise e

    def errdispose(self):
        try:
            self.end('roollback')
            self._cursor.close()
            self._conn.close()
        except Exception as e:
            print('-------------事务回滚，关闭连接出现问题')
            print(e)
            raise e

    def dispose(self):
        try:
            self.end('commit')
            self._cursor.close()
            self._conn.close()
        except Exception as e:
            print('----------------释放资源出现问题')
            print(e)
            raise e