import tornado.ioloop
import tornado.web
import tornado.httpclient
import json

import sys
from base import Smart_Mysql
import datetime


mysql = Smart_Mysql

session_id = 1

class MainCookies(tornado.web.RequestHandler):
    
    session_id = 1
    def get(self):
        global session_id
        if not self.cookies('session'):
            self.set_cookie("session", str(session_id))
            session_id += 1
            self.write('你已经获得了新的session')
        else:
            self.write('你已经有了session')

class MainHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        name = self.get_arguments('name')
        if name:
            return True
        return False

    @tornado.web.authenticated
    def get(self):
        handler_type = self.get_argument('handler_type')
        if handler_type == 'sign_in':
            user_id = self.get_argument('user_id')
            data = {}
            sql = "select id from tbActSignin where iUserId = %s AND \
                to_days(dtCreateTime)=to_days(now())"
            check = mysql.query(sql, param=[user_id])
            if check:
                data['ret'] = -2
                data['msg'] = '打卡失败：已经打卡'
            else:
                sql = "INSERT INTO tbActSignin SET iUserId = %s"
                suc = mysql.insert(sql, param=[user_id])
                if suc:
                    data['ret'] = 0
                    data['msg'] = '打卡成功'
                else:
                    data['ret'] = -2
                    data['msg'] = '打卡出现异常'
            self.write(data)
        else:
            self.write('请传入正确的操作类型')

class LoginHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('请登录')


Handlers = [
    ('/', MainHandler),
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
