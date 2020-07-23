import random
import json
import datetime

from base.Predis import Open_Redis
from base.cmysql import Mysql

STAR_SIGIN = {
    1 : '水瓶座碎片',
    2 : '双鱼座碎片', 
    3 : '白羊座碎片',
    4 : '金牛座碎片',
    5 : '双子座碎片',
    6 : '巨蟹座碎片',
    7 : '狮子座碎片',
    8 : '处女座碎片', 
    9 : '天秤座碎片',
    10 : '天蝎座碎片',
    11 : '射手座碎片', 
    12 : '摩羯座碎片' 
}

NUMBER_DICT = {
    1 : 'one',
    2 : 'two',
    3 : 'three',
    4 : 'four',
    5 : 'five',
    6 : 'six',
    7 : 'seven',
    8 : 'eight',
    9 : 'nine',
    10 : 'ten',
    11 : 'eleven',
    12 : 'twelve'
}

PATCH_SELL_MONEY = {
    1 : 25,
    2 : 25,
    3 : 10,
    4 : 25,
    5 : 25,
    6 : 10,
    7 : 25,
    8 : 10,
    9 : 10,
    10 : 25,
    11 : 150,
    12 : 150
}


#获得碎片
def getPatch(user_id, path_type, handle_type, consume_type, mysqld=None):
    '''
    handle_type : 
    1. 投递纸盒,
    2. 扫码进入页面,
    3. h5抽奖,
    4. 绑定手机号,
    5. 绑定校徽,
    6. 步数兑换,
    7. 每日一答,
    8. 每日签到，
    9. 小程序抽奖，
    10. 星空市场
    '''
    erro_msg = {
            'ret' : -2,
            'msg' : '获取失败'
        }
    if not isinstance(path_type, list):
        print('不是list')
        return erro_msg

    mysql = mysqld if mysqld else Mysql()
    sql = f"SELECT * FROM user_star_sign WHERE user_id = {user_id}"
    check = mysql.getOne(sql)
    if not check:
        sql = f"INSERT INTO user_star_sign SET user_id = {user_id} "
        mysql.insertOne(sql)
    #上锁
    sql = f"SELECT * FROM user_star_sign WHERE user_id = {user_id} FOR UPDATE"
    mysql.getOne(sql)
    asd = '+ 1' if consume_type == 1 else '- 1'
    for i in path_type:
        sql = f"UPDATE user_star_sign SET {NUMBER_DICT[i]} \
            = {NUMBER_DICT[i]} {asd} WHERE user_id = {user_id} "
        mysql.update(sql)
        sql = f"INSERT INTO star_sign_log SET user_id = {user_id}, \
            star_sign_id = {i}, handle_type = {handle_type}, \
            consume_type = {consume_type}"
        suc = mysql.insertOne(sql)
    print('传入mysql') if mysqld else mysql.dispose()
    if suc:
        return {
            'ret' : 0,
            'msg' : '获取成功',
            'result' : path_type
        }
    return erro_msg

#查询是否有碎片领取记录
def starSignLog(user_id, handle_type):
    mysql = Mysql()
    sql = f"SELECT * FROM star_sign_log WHERE user_id = {user_id} \
        AND handle_type = {handle_type}"
    data = mysql.getOne(sql)
    mysql.dispose()
    if data:
        return True
    return False

#抽取一片碎片
def randomPath():
    #normal
    value_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    probabilities = [0.08, 0.15, 0.15, 0.08, 0.05, 0.15, 0.05, 0.05, 0.17, 0.05, 0.01, 0.01]
    x = random.uniform(0, 1)
    cumprob = 0.0
    for item, item_pro in zip(value_list , probabilities):
        cumprob += item_pro
        if x < cumprob:
            break
    return item

def randomH5Patch():
    value_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    probabilities = [0.05, 0.05, 0.36, 0.17, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05, 0.03, 0.03]
    x = random.uniform(0, 1)
    cumprob = 0.0
    for item, item_pro in zip(value_list , probabilities):
        cumprob += item_pro
        if x < cumprob:
            break
    return item

def randomWxPatch(m=None):
    #小程序
    value_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, {'hhcoin':1}, {'hhcoin':50}, {'hhcoin':100}]
    probabilities = [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.03, 0.03, 0.26, 0.10, 0.08]
    x = random.uniform(0, 1)
    cumprob = 0.0
    for item, item_pro in zip(value_list , probabilities):
        cumprob += item_pro
        if x < cumprob:
            break
    return item

#购买市场碎片+日志
def starryMarketLog(user_id, patch_id, patch_name, hhcon, handle_type, numbers, mysql):
    '''
    handle_type 0买 1卖
    '''
    mysql = mysql
    sql = f"SELECT * FROM user_star_sign WHERE user_id = {user_id}"
    check = mysql.getOne(sql)
    if not check:
        sql = f"INSERT INTO user_star_sign SET user_id = {user_id} "
        mysql.insertOne(sql)
    handle = f'+ {numbers}' if handle_type == 1 else f'- {numbers}'
    upmarket_sql = f"UPDATE starry_market SET number = number {handle} WHERE id = {patch_id}"
    ins_sql = f"INSERT INTO starry_market_log SET user_id = {user_id}, \
        path_id = {patch_id},  hhcoin = {hhcon}, handle_type = {handle_type}"
    return upmarket_sql, ins_sql