import tornado.ioloop
import tornado.web
import tornado.websocket
import json

from cmysql import Mysql
from base import ComplexEncode
from tornado.options import define ,options, \
                        parse_command_line

clients = dict()

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")

class MyWebSocketHandler(tornado.websocket.WebSocketHandler):
    
    def open(self, *args):
        self.id = self.get_argument('id') 
        self.stream.set_nodelay(True)
        clients[self.id] = {
            "id": self.id,
            "object": self
        }
        print(f"Client {self.request.remote_ip} is open")

    def on_message(self, message):
        print("Client %s received a messge :%s" \
            % (self.id, message))

    def on_close(self):
        if self.id in clients:
            del clients[self.id]
            print("Client %s is closed" % (self.id))

    def check_origin(self, origin):
        return True

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/webscoket', MyWebSocketHandler)
])

import threading
import time
import datetime
import asyncio

def sendTime():
    asyncio.set_event_loop(asyncio.new_event_loop())
    data_list = []
    while True:
        mysql = Mysql()
        sql = "SELECT orders.*, userInfo.wxname FROM orders \
            LEFT JOIN userInfo ON orders.createUser = userInfo.id \
            WHERE state = 1 \
            ORDER BY createTime DESC LIMIT 15"
        info = mysql.getAll(sql)
        sql = "SELECT COUNT(id) as numbs FROM orders"
        numbs = mysql.getOne(sql)
        mysql.dispose()
        data = {}
        data['numbs'] = numbs.get('numbs')
        data['info'] = info
        if len(data_list) == 0:
            data_list.append(data)
        if data_list[0] == data:
            x = '0'
        else:
            x = '1'
            data_list[0] = data
        for key in clients.keys():
            new_data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            print(f'发送数据给{key}')
            clients[key]["object"].write_message(new_data)
            clients[key]["object"].write_message(x)
        time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=sendTime).start()
    parse_command_line()
    app.listen(port=8000, address="0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()