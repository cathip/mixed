import tornado.ioloop
import tornado.web
import tornado.httpclient
import json
import time
import sys

from handler_sql import Answer, Signin
from base.shop_base import callJson

#from new_hhzs.hhzs.base.shop_base import callJson

def checkLogin():
    return  1

#每日一答
class AnswerHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        #判断登录态
        user_id = checkLogin()
        if user_id:
            return True
        return False

    @tornado.web.authenticated
    def get(self):
        try:
            #-----------------参数--------------------
            info = '参数错误'
            handler_type = self.get_argument('handler_type')
            chose_id = self.get_argument('chose_id', None)
            user_id = self.get_argument('user_id')
            #----------------------------------------
            if handler_type == 'question':
                info = Answer(user_id=user_id).get_answer()
            if handler_type == 'answer':
                info = Answer(user_id=user_id).daily_answer(chose_id=chose_id)
            self.write(callJson(info))
        except Exception as e:
            self.write(callJson(data={
                "ret": -2,
                "msg": "操作失败",
                "err": f'{e}'
            }))

#打卡签到
class SigninHandler(tornado.web.RequestHandler):
    pass

class LoginHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('请登录')

Handlers = [
    ('/answer', AnswerHandler),
    ('/signin', SigninHandler),
    ('/login', LoginHandler),
]


def main():
    app = tornado.web.Application(Handlers, login_url='/login', 
                                            debug=True, 
                                            cookie_secret="SECRET_DONT_LEAK")
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()