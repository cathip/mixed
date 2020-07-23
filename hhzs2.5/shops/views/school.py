from django.views import View
from django.http import request, HttpResponse

from base.cmysql import Mysql
from base.shop_base import Type_Log, query, returnJson


class School(View):

    def __init__(self):
        self.info = {}

    def post(self, request, **payload):
        handle = payload.get('handle')

        self.info['user_id'] = payload.get('user_id')
        self.info['school_id'] = request.POST.get('school_id')
        self.info['school_name'] = request.POST.get('school_name')

        if handle == 'see':
            sql = "SELECT * FROM school WHERE school_name LIKE %s"
            self.info['school_name'] = '%' + self.info['school_name'] + '%'
            info = query(sql, param=[self.info['school_name']])
            return HttpResponse(returnJson(0, '查询成功', info))

        if handle == 'update':
            mysql = Mysql()
            sql = "SELECT hhcoin, school_id FROM userInfo WHERE id = %s FOR UPDATE"
            info = mysql.getOne(sql, param=[self.info['user_id']])
            #已经绑定有 扣除盒盒币
            if info.get('school_id'):
                if int(info.get('hhcoin')) >= 1000:
                    up_sql, log_sql = Type_Log.coin_handle(user_id=self.info['user_id'], 
                                                            handle=0, 
                                                            num=1000, 
                                                            asd=0)
                    mysql.update(up_sql)
                    mysql.insertOne(log_sql)
                    sql = "UPDATE userInfo SET school_id = %s WHERE id = %s"
                    mysql.update(sql, param=[self.info['shcool_id'], self.info['user_id']])
                    mysql.dispose()
                    return HttpResponse(returnJson(0, '绑定成功'))
                #盒盒币不足 返回2
                else:
                    return HttpResponse(returnJson(-2, '盒盒币不足'))
            #首次绑定
            else:
                sql = "UPDATE userInfo SET school_id = %s WHERE id = %s"
                suc = mysql.update(sql, param=[
                    self.info['school_id'], 
                    self.info['user_id']
                ])
                mysql.dispose()
                return HttpResponse(returnJson(0, '绑定成功'))

        return HttpResponse(returnJson(-2, '非法路径'))