import json

from django.views import View
from django.utils.decorators import method_decorator
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.shop_base import Pagings, ComplexEncode, Type_Log, returnJson, query
# 打卡
class Click_Card(View):

    def __init__(self):
        self.info = {}

    def post(self, request, **payload):
        handle = payload.get('handle')

        self.info['user_id'] = payload.get('user_id')
        self.info['check_time'] = request.POST.get('check_time')

        if handle == 'do':
            return self.do()

        if handle == 'see':
            return self.see()

        return HttpResponse(returnJson(-2, '非法路径'))

    def do(self):
        mysql = Mysql()
        sql = "select * from click_card where \
            to_days(checkTime)=to_days(now()) AND userid=%s"
        check = mysql.getOne(sql, param=[self.info['user_id']])
        if check:
            # 已经打卡
            mysql.dispose()
            return HttpResponse(returnJson(-2, '重复打卡'))
        # 打卡
        sql = "INSERT INTO click_card SET userid = %s"
        suc = mysql.insertOne(sql, param=[self.info['user_id']])
        up_sql, log_sql = Type_Log.coin_handle(
            user_id=self.info['user_id'], handle=2, num=10, asd=1)
        mysql.update(up_sql)
        mysql.insertOne(log_sql)
        mysql.dispose()
        return HttpResponse(returnJson(0, '打卡成功'))

    def see(self):
        sql = "SELECT checkTime FROM click_card \
            WHERE userid = %s AND checkTime LIKE %s"
        info = query(sql, param=[self.info['user_id'], '%' + self.info['check_time'] + '%'])
        return  HttpResponse(returnJson(0, '打卡成功', info))
