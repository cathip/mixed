import pymysql
from pymysql.cursors import DictCursor
import random
pymysql.install_as_MySQLdb()
from DBUtils.PooledDB import PooledDB
import time


DBHOST = "129.211.136.124"
DBPORT = 3306
DBUSER = 'root'
DBPASSWD = 'hhzs999999'
DB = 'test'

#正式数据
# DBHOST = 'cd-cdb-a9vh6zu6.sql.tencentcdb.com'
# DBPORT = 63656
# DBUSER = 'root'
# DBPASSWD = 'hhzs999999'
# DB = 'hhzs2019'


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

class Mysql(object):


    def __init__(self):
        self.__pool = None
        self._conn = self.__getConn()
        self._cursor = self._conn.cursor()

    def __getConn(self):
        if self.__pool is None:
            try:
                self.__pool = PooledDB(creator=pymysql, mincached=1, maxcached=100, host=DBHOST, port=DBPORT,

                                  user=DBUSER, passwd=DBPASSWD, db=DB, charset=DBCHAR,
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

class Basedmethod(object):

    @staticmethod
    def OrderNum():
        '''
        订单号生成方法
        :return:
        '''
        seq = [chr(a) for a in range(ord('a'), ord('z') + 1)]
        return str(''.join(list(random.choices(seq, k=2))).upper()) + str(int(time.time())) + str(
            random.randint(1000, 9999))

def test():
    mysql = Mysql()
    for i in range(1,100000):
        order_num = Basedmethod.OrderNum()
        sql = "INSERT INTO orders SET orderNum = '{order_num}', createUser='907', \
            address='上海市松江区文汇路1000号 松江大学城-四期学生公寓', \
            Consignee='二郎真菌', mobile= '15635353636', orderMoney='16.00', \
            wxMoney='0.00', balance='0.00', heheCoin='47', sendTime='5-28 21:31-22:00', \
            remark='null',state='4'".format(order_num=order_num)
        print(i)
        mysql.insertOne(sql)
    mysql.dispose()
    return 1

if __name__ == "__main__":
    a = test()
    print(a)