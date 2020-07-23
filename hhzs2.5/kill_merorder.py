import time
from redis import StrictRedis
from base.cmysql import Mysql
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
    mysql = Mysql()
    if order_num[0] == 'mer_order':
        sql = f"UPDATE mer_orders SET state = 2 WHERE order_num = '{order_num[-1]}' AND state = 0"
        print(sql)
        suc = mysql.update(sql)
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if suc:
            sql = f"SELECT * FROM mer_orders WHERE order_num = '{order_num[-1]}'"
            info = mysql.getOne(sql)
            sql = f'''UPDATE userInfo SET money = money + "{info.get('balance')}", \
                hhcoin = hhcoin + "{info.get('hh_coin')}" WHERE id = "{info.get('user_id')}"'''
            mysql.update(sql)
            print(sql)
            print(f'{time}取消订单{order_num[-1]}成功')
        else:
            print(f'{time}取消订单{order_num[-1]}失败')
    else:
        pass
    mysql.dispose()
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
