import os
import time
import json
import datetime

import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
from tornado.options import define, options
from tornado.websocket import WebSocketHandler

from cmysql import Mysql
from base import ComplexEncode
from tornado.web import RequestHandler



class Orders(RequestHandler):

    # mysql = Mysql()
    # sql = "SELECT * FROM orders ORDER BY createTime DESC LIMIT 15"
    # info = mysql.getAll(sql)
    # mysql.dispose()
    # if len(self.data_list) == 0:
    #     self.data_list.append(info)
    # if self.data_list[0] != info:
    #     self.data_list[0] = info
    #     data = {}
    #     data['state'] = 1
    #     data['info'] = self.data_list[0]
    #     data = json.dumps(data, ensure_ascii=False, \
    #                 sort_keys=True, indent=4, cls=ComplexEncode)
    #     self.write_message(data)
    # else:
    #     self.data_list[0] = info
    #     data = {}
    #     data['state'] = 0
    #     data['info'] = self.data_list[0]
    #     data = json.dumps(data, ensure_ascii=False, \
    #                 sort_keys=True, indent=4, cls=ComplexEncode)
    pass

class IndexHandler(RequestHandler):

    def get(self):
        self.render("index.html")

class ChatHandler(WebSocketHandler):

    data_list = []
    check = 1

    def open(self):
        print("建立连接", self.request.remote_ip)
        # while self.check != 0:
        #         time.sleep(3)
        #         mysql = Mysql()
        #         sql = "SELECT * FROM orders ORDER BY createTime DESC LIMIT 15"
        #         info = mysql.getAll(sql)
        #         mysql.dispose()
        #         if len(self.data_list) == 0:
        #             self.data_list.append(info)
        #         if self.data_list[0] != info:
        #             self.data_list[0] = info
        #             data = {}
        #             data['state'] = 1
        #             data['info'] = self.data_list[0]
        #             data = json.dumps(data, ensure_ascii=False, \
        #                         sort_keys=True, indent=4, cls=ComplexEncode)
        #             self.write_message(data)
        #         else:
        #             self.data_list[0] = info
        #             data = {}
        #             data['state'] = 0
        #             data['info'] = self.data_list[0]
        #             data = json.dumps(data, ensure_ascii=False, \
        #                         sort_keys=True, indent=4, cls=ComplexEncode)
        #             print('111')
        #             self.write_message(data)

    def on_close(self):
        self.check = 0
        print("关闭连接2", self.request.remote_ip)

    def check_origin(self, origin):
        return True

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        [
            (r'/', IndexHandler),
            (r'/all_orders', ChatHandler),
        ],
        static_path = os.path.join(os.path.dirname(__file__), "static"),
        template_path = os.path.join(os.path.dirname(__file__), "template"),
        debug = True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port=8000, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()