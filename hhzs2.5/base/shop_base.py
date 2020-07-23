# coding=utf-8

'''
商城项目公共方法
'''

import base64
import datetime
import decimal
import json
import random
import string
import time
from hashlib import md5, sha1
from Crypto.Cipher import AES

from base.wx_config import GZH_APPID

from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse


from base.cmysql import Mysql
from base.wx_config import Mch_key, GZH_APPID



#分页
class Pagings():
    #django分页
    @staticmethod
    def paging(queryset, row, page):
        if queryset:
            # 总页数,页数信息
            paginator = Paginator(queryset, row)
            sumpage = paginator.num_pages
            try:
                data = paginator.page(page).object_list
            except:
                data = paginator.page(sumpage).object_list
            return sumpage, data
        return 1, queryset

    #mysql limit分页
    @staticmethod
    def mysqlPagings(page, row):
        new_page = (int(page)-1)*int(row)
        new_row = int(row)
        return new_page, new_row

# 格式化时间
class ComplexEncode(json.JSONEncoder):
    
    def default(self, obj):                 # pylint: disable=E0202
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        # return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.date):
            # return obj.strftime('%Y-%m-%d')
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)

#django缓存相关操作(redis)
class RedisManagers():

    def getOne(self, key, default=None, version=None, client=None):
        '''
        redis 查询操作
        :param key: 查询的键
        :param default:
        :param version:
        :param client:
        :return:
        '''
        try:
            data = cache.get(key, default=default, version=version, client=client)
            return data
        except Exception as e:
            print("缓存报错:", e)
            return False

    def setOne(self, key, value, ttl):
        '''
        redis 插入操作
        :param args:
        :param kwargs:
        :return:
        '''
        try:
            cache.set(key, value, ttl)
        except Exception as e:
            print("缓存报错:", e)

    def getMany(self, *args, **kwargs):
        try:
            return cache.get_many(*args, **kwargs)
        except Exception as e:
            print("缓存报错:", e)
            return False

    def delete(self, *args, **kwargs):
        '''
        redis 删除操作
        :param args:
        :param kwargs:
        :return:
        '''
        try:
            cache.delete(*args, **kwargs)
        except Exception as e:
            print("缓存报错:", e)

#余额盒盒币抽奖操作方法 以及日志
class Type_Log():
    #余额操作方法 以及日志
    @staticmethod
    def balance_log(user_id, handle, money, asd, order_num=False):
        '''
        asd: 加减余额,asd为0则减，为1则加
        hadle: 操作类型1订单，2抽奖，3退款 4砍价获得 5提现
        '''
        if asd == 1:
            up_sql = f"update userInfo set money=(money+{money}) where id={user_id}"
        #减少
        else:
            up_sql = f"update userInfo set money=(money-{money}) where id={user_id}"
        if order_num:
            log_sql = f"INSERT INTO balance_log SET userid='{user_id}', money='{money}', \
                handleType='{handle}', orderNum='{order_num}', consumeType='{asd}'"
        else:
        #不是订单      
            log_sql = f"INSERT INTO balance_log SET userid='{user_id}', money='{money}', \
                handleType='{handle}', consumeType='{asd}'"
        return up_sql, log_sql

    #new 盒盒币操作方法 以及日志
    @staticmethod
    def coin_handle(user_id, handle, num, asd):
        '''
        获取操作信息
        :param user_id: 用户的user_id
        :param handle: 操作类型: 0:更换学校；1:下单,2签到:,3:微信步数,4:充值赠送,
        5:废纸投递,6:抽奖奖励,7:每日一答奖励,8:排行榜，9退款, 10小游戏大乱斗， 11砍价, 
        12:一元购赠送,13:提现到余额, 14. 碎片抽奖, 15星空市场
        :param num: 要操作的hhcoin的数量
        :param asd: 加减盒盒币,asd为0则减，为1则加
        '''
        if asd == 1:
            up_sql = f"update userInfo set hhcoin=(hhcoin+{num}) where id={user_id}"
        else:
            up_sql = f"update userInfo set hhcoin=(hhcoin-{num}) where id={user_id}"
        #日志sql
        log_sql = f"INSERT INTO coin_log SET userid='{user_id}', num='{num}', handleType='{handle}', \
            consumeType='{asd}'"
        return up_sql, log_sql

    #抽奖记录
    @staticmethod
    def reward_log(user_id, prize_id, detail, prize_type, get):
        '''
        prize_type: 1.商品 2.实物 3.cdk 4.二维码 5.盒盒币 6.VIP 7.余额 8 谢谢惠顾
        get: 1已领 0未领取
        '''
        reward_sql = f"INSERT INTO reward_log SET prize_id='{prize_id}', detail='{detail}', \
            prize_type='{prize_type}', user_id='{user_id}', `get`='{get}'"
        return reward_sql

#生成图片名字
def getImgName():
    str_time = str(int(time.time()))
    num = str(random.randint(1,100))
    img_name = str_time + num + '.png'
    return img_name

# 返回当前的星期一和下个星期一的日期
def getCurrentWeek():
    monday, sunday = datetime.date.today(), datetime.date.today()
    one_day = datetime.timedelta(days=1)
    while monday.weekday() != 0:
        monday -= one_day
    while sunday.weekday() != 6:
        sunday += one_day
    return str(monday), str(sunday+datetime.timedelta(days=1))

#验证登录装饰器
def auth(func):
    '''判断是否登录装饰器'''
    def inner(request, *args, **kwargs):
        if not request.session.get("openid"):
            return HttpResponse(-10, '未登录')
        return func(request, *args, **kwargs)
    return inner

#获取订单编号
def getOrderNum(orderType : str):
    '''
    订单号生成方法
    :return:
    '''
    return str(orderType + datetime.datetime.now().strftime("%Y%m%d%H%M") + str(randomNumber()))

#返回的数据格式
def returnJson(ret : int, msg : str, result=None):
    data = {
        'ret' : ret,
        'msg' : msg
    }
    if result or isinstance(result, list) or isinstance(result, dict):
        data = {
            'ret' : ret,
            'msg' : msg,
            'result' : result
        }
    
    return callJson(data)

#Json数据转换
def callJson(data=None):
    if data:
        data = json.dumps(data, ensure_ascii=False, 
                                sort_keys=True, 
                                indent=4,
                                cls=ComplexEncode)
    return data

#生成6位随机数
def randomNumber():
    return random.randint(100000, 999999)

#-----------------------------mysql相关--------------------------------

#快速获取多条记录
def query(sql, param=None):
    mysql = Mysql()
    info = mysql.getAll(sql, param=param)
    mysql.dispose()
    return info

#快速获取一条记录
def queryOne(sql, param=None):
    mysql = Mysql()
    info = mysql.getOne(sql, param=param)
    mysql.dispose()
    return info

#错误日志
def erroLog(msg):
    if msg:
        mysql = Mysql()
        sql = "INSERT INTO erro_log SET erro_detail = %s, create_time = NOW()"
        mysql.insertOne(sql, param=[str(repr(msg))])
        mysql.dispose()
        return 1
    else:
        return 0

#-----------------------------wx相关--------------------------------

#微信sign(md5)
def getSign(ks):
    stringA = ''
    ksl = sorted(ks.keys())
    for k in ksl:
        stringA += (k + '=' + str(ks[k]) + '&')
    stringSignTemp = stringA + 'key=' + Mch_key
    sign = md5(stringSignTemp.encode('utf-8')).hexdigest().upper()
    return sign

#公众号网页签名算法(哈希)
def getShaSign(ks):
    stringA = ''
    ksl = sorted(ks.keys())
    for k in ksl:
        stringA += (k + '=' + str(ks[k]) + '&')
    stringA = stringA[0 : len(stringA) - 1 ]
    sha = sha1(stringA.encode('utf-8'))
    encrypts = sha.hexdigest()
    return encrypts

# 生成随机字符串(微信)
def getNonceStr():
    return ''.join(random.sample(string.ascii_letters+string.digits, 32))

#获取微信加密数据
class WXBizDataCrypt:
    def __init__(self, sessionKey):
        self.appId = GZH_APPID
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)

        decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)))

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]
    