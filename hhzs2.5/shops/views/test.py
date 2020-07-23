import json
import math
from uuid import uuid4
from random import randint

from django.views import View
from django.core.cache import cache
from django.http import request, HttpResponse, JsonResponse, QueryDict

from base.jwt import getToken
from base.cmysql import Mysql
from base.Predis import Open_Redis
from base.qcloudsms import sendSms, pullSms
from base.shop_base import ComplexEncode, Type_Log, Pagings, erroLog, returnJson


class Test_Login(View):

    def post(self, request):
        try:
            phone = request.POST.get('phone')
            code = request.POST.get('code')
            conn = Open_Redis().getConn(7)
            if conn.exists(phone):
                cache = conn.get(phone)
                if cache.decode('utf-8') != code:
                    return HttpResponse(returnJson(-2, '验证码失效'))
                token = getToken({'user_id' : 907}, 24)
                token = {'token' : token}
                return HttpResponse(returnJson(0, '登录成功', result=token))
            return HttpResponse(returnJson(-1, '不存在验证码请重新发送'))
        except Exception as e:
            erroLog(e)
            return HttpResponse(returnJson(-2, '网络错误'))

class GetCode(View):

    def post(self, request):
        try:
            phone = request.POST.get('phone')
            print(phone)
            if not phone:
                print(phone)
                return HttpResponse(returnJson(-2, '手机号码错误'))
            conn = Open_Redis().getConn(7)
            cache = conn.exists(phone)
            if conn.exists(phone):
                return HttpResponse(returnJson(-1, '已有验证码 请勿重新发送'))
            code = sendSms(phone)
            if code:
                code = {'code' : code}
                return HttpResponse(returnJson(0, '成功', code))
            return HttpResponse(returnJson(-2, '验证码发送失败'))
        except Exception as e:
            erroLog(e)
            return HttpResponse(returnJson(-2, '网络繁忙'))

class GetToken(View):

    def get(self, request):
        token = getToken({'user_id' : 149}, 24)
        return JsonResponse({'token' : token})

#测试
class Test_Sql(View):

    def post(self, request):
        user_id = request.POST.get('user_id')
        mysql = Mysql()
        sql = f"SELECT * FROM userInfo WHERE id = '{user_id}'"
        print(sql)
       # info = mysql.getAll(sql)
        info = mysql.getOne(sql)
        mysql.dispose()
        return JsonResponse(info)

#SESSION
class Test_Session(View):

    def post(self, request):
        open_id = request.POST.get('openid')
        request.session['open_id'] = open_id
        data = {}
        data['status'] = 100
        data['msg'] = "保存成功"
        return JsonResponse(data)

    def get(self, request):
        if request.session.get('open_id'):
            return HttpResponse('OK')
        return HttpResponse("FAIL")

#加热度
class Test_Hots(View):

    def get(self, request):
        mysql = Mysql()
        sql = "SELECT * FROM courses  WHERE  co_tutiondate >= now()  \
            ORDER BY co_tutiondate asc, co_starttime asc"
        info = mysql.getAll(sql)
        print(info)
        mysql.dispose()
        return HttpResponse(1)

#测试事务
# class Test_Affair(View):
#     def get(self, request):
#         sql = "INSERT INTO `users` (`mobile`, `name`, `password`, `state`, \
#           `isAdmin`, `power`) VALUES ('112', '5', '5', '5', '5', '5')"
#         #sql = "SELECT * FROM `users`"
#         conn, cursor = Smart_Mysql.getConn()
#         suc = Smart_Mysql.insert(sql)
#         Smart_Mysql.dispose(conn=conn, cursor=cursor)
#         #Smart_Mysql.errdispose(conn=conn, cursor=cursor)
#         if suc:
#             return HttpResponse(suc)
#         return HttpResponse(0)