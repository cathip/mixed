import time
from redis import StrictRedis
from base.cmysql import Mysql
from base.shop_base import Type_Log
from base.limits import hold_huigun
import datetime


REDIS_HOST = '129.211.136.124'
REDIS_PASSWD = ""
REDIS_PORT = 6379
redis = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWD, decode_responses=True)

pubsub = redis.pubsub()  
def event_handler(msg):
    #print('Handler', msg)
    #print(msg['data'])
    order_num = msg['data'].split('-')
    if order_num[0] == 'order':
        mysql = Mysql()
        sql = f"UPDATE orders SET state = 5 WHERE orderNum = '{order_num[-1]}' AND state = 0"
        print(sql)
        suc = mysql.update(sql)
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if suc:
            sql = f"SELECT * FROM orders WHERE orderNum = '{order_num[-1]}'"
            info = mysql.getOne(sql)
            sql = f'''UPDATE userInfo SET money = money + "{info.get('balance')}", \
                hhcoin = hhcoin + "{info.get('heheCoin')}" WHERE id = "{info.get('createUser')}"'''
            mysql.update(sql)

            sql = f'''SELECT product_id, p.user_goods_limit FROM ordergoods AS o \
                LEFT JOIN product AS p ON o.product_id = p.id WHERE o.order_id = "{order_num[-1]}"'''
            data = mysql.getAll(sql)
            holds = []
            for limit_numb in data:
                if limit_numb.get('user_goods_limit') != 0:
                    limit_data = {}
                    limit_data['key'] = 'product_1909_' + str(limit_numb.get('product_id'))
                    print(limit_data)
                    holds.append(limit_data)
            print(holds)
            if holds:
                huigun = hold_huigun(holds=holds, user_id=info.get('createUser'), mysql=mysql)
                print(huigun)
            else:
                mysql.dispose()
                print('没有要取消限量的商品')
            print(f'{time}取消订单{order_num[-1]}成功')
        else:
            print(f'{time}取消订单{order_num[-1]}失败')
    else:
        pass
pubsub.psubscribe(**{'__keyevent@2__:expired': event_handler})
#订阅频道
#pubsub.psubscribe('__keyevent@1__:*')


print('Starting message loop')  
while True:  
    message = pubsub.get_message()
    if message:
        print(message)
    else:
        time.sleep(0.01)