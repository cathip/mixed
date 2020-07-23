#!/home/ubuntu/work01/bin  python
# -*- coding: utf-8 -*-
# @Author  : baiyun
# @File    : everyWeek.py
# @Software: PyCharm
# @Time    : 2019/5/10 15:14

import pymysql
import datetime
pymysql.install_as_MySQLdb()
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

DBHOST = 'cd-cdb-a9vh6zu6.sql.tencentcdb.com'
DBPORT = 63656
DBUSER = 'root'
DBPASSWD = 'hhzs999999'
DB = 'hhzs_2.0'

# DBHOST = "129.211.136.124"
# DBPORT = 3306
# DBUSER = 'root'
# DBPASSWD = 'hhzs999999'
# DB = 'hhzs2019'

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

class Smart_Mysql(object):

    #开启事务
    @staticmethod
    def getConn():
        try:
            pool = PooledDB(creator=pymysql, 
                            mincached=1, 
                            maxcached=100, 
                            host=DBHOST, 
                            port=DBPORT,
                            user=DBUSER, 
                            passwd=DBPASSWD, 
                            db=DB, 
                            charset=DBCHAR,
                            cursorclass=DictCursor)
            conn = pool.connection()
            return conn, conn.cursor()
        except Exception as e:
            print(f'-----获取数据库连接错误\n{e}')

    #执行语句
    @staticmethod
    def execute(sql, cursor, action, param=None):
        result = cursor.execute(sql, param)
        if (action == "query"):
            result = cursor.fetchall()
        if (action == "insert"):
            cursor.execute('SELECT @@IDENTITY AS id')
            result = cursor.fetchall()[0]['id']
        return result

    #运行方法
    @staticmethod
    def base(sql, param, dbCursor, action):
        try:
            data = {}
            result = []
            if dbCursor:
                result = Smart_Mysql.execute(sql, param, dbCursor, action)
            else:
                conn, cursor = Smart_Mysql.getConn()
                result = Smart_Mysql.execute(sql, param, cursor, action)
                conn.commit()
            return result
        except Exception as e:
            data['ret'] = -2
            data['msg'] = "执行语句出错"
            data['result'] = []
            print(f'-----执行sql出现错误\n{e}')
            return data
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

def get_current_week():
        monday, sunday = datetime.date.today(), datetime.date.today()
        one_day = datetime.timedelta(days=1)
        while monday.weekday() != 0:
            monday -= one_day
        while sunday.weekday() != 6:
            sunday += one_day
        # 返回当前的星期一和星期天的日期
        return str(monday), str(sunday+datetime.timedelta(days=1))

def Lastranklist():
        start_time = '2019-11-21'
        end_time = '2019-11-25'
        '''
        每周一更新上周排名计算并保存
        :return:
        '''
        SQL1 = 'truncate table last_ranklist;'
        SQL2 = f'''INSERT INTO last_ranklist(weight, user_id, wxname, user_img, school_img, state, id) \
                SELECT \
                    t.*, @rank := @rank + 1 AS id FROM \
                (SELECT 									 \
                    SUM(d.wight) AS weight,  \
                    u.id AS user_id,  \
                    u.wxname,  \
                    u.user_img,  \
                    s.school_img, \
                    state = 1 AS state \
                FROM  \
                    deliver AS d  \
                    LEFT JOIN gzh_user AS g ON g.openid = d.openid  \
                    LEFT JOIN userInfo AS u ON u.unionId = g.unionid  \
                    LEFT JOIN school AS s ON u.school_id = s.id  \
                WHERE  \
                    d.create_time BETWEEN '{start_time}' AND '{end_time}' \
                AND u.wxname IS NOT NULL  \
                AND g.openid NOT IN ('oLKbX1JCYRryfJsXPNvl69kNTXFU', \
                        'oLKbX1BjDWpeyuVFPGzm9H7szvoo','oLKbX1CXeWasiulsOR-_CeYnlprk', \
                        'oLKbX1KuMDzJe2e46z0WyLAhkKHQ','oLKbX1O-HV9pXabfE5BWB6jsMbQY', \
                        'oLKbX1Hc8lNNZmNNQcM0WhvbvnhM','oLKbX1OJgSIZrb2Hxi2nYRnRPpTQ', \
                        'oLKbX1GgjlWc155Qk927f7hHhWv8')  \
                GROUP BY  \
                    d.openid  \
                ORDER BY  \
                    weight DESC  \
                LIMIT 0,  \
                100) AS t, (SELECT @rank := 0) AS r'''
        sql3 = "UPDATE last_ranklist SET state = 0  \
                WHERE id IN (SELECT * FROM (SELECT id FROM last_ranklist ORDER BY id LIMIT 3) AS c)"
        sql4 = "truncate table last_school_ranklist"
        sql5 = f'''INSERT INTO last_school_ranklist (weight, school_id, school_name, school_img, id) \
                    SELECT \
                        t.*, @rank := @rank + 1 AS id FROM \
                    (SELECT  \
                                            SUM(d.wight) AS all_wight,  \
                                            u.school_id,  \
                                            s.school_name,  \
                                            s.school_img  \
                                        FROM  \
                                            deliver AS d  \
                                            LEFT JOIN gzh_user AS g ON g.openid = d.openid  \
                                            LEFT JOIN userInfo AS u ON u.unionId = g.unionid  \
                                            LEFT JOIN school AS s ON u.school_id = s.id  \
                                        WHERE  \
                                            d.create_time BETWEEN '{start_time}' AND '{end_time}' \
                                        AND u.wxname IS NOT NULL  \
                                        AND u.school_id is NOT NULL  \
                                        GROUP BY  \
                                            u.school_id  \
                                        ORDER BY  \
                                            all_wight DESC 
                                        LIMIT 0,  \
                                        100) AS t, (SELECT @rank := 0) AS r'''
        mysql = Smart_Mysql()
        conn, cursor = mysql.getConn()
        mysql.execute(sql=SQL1, cursor=cursor, action="query")
        state = mysql.execute(sql=SQL2, cursor=cursor, action="query")
        mysql.execute(sql=sql3, cursor=cursor, action="query")
        mysql.execute(sql=sql4, cursor=cursor, action="query")
        mysql.execute(sql=sql5, cursor=cursor, action="query")
        mysql.dispose(conn=conn, cursor=cursor)
        return state

if __name__ == "__main__":
    try:
        print("请稍后")
        state = Lastranklist()
        print("更新排行榜成功")
    except Exception as e:
        print(e)
        print("更新排行榜失败")


