#utf-8
import jwt
import json
import datetime

from hhsc2019.settings import SECRET_KEY
from django.shortcuts import render
from django.views import View
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.jwt import getToken
from base.shop_base import callJson, returnJson, queryOne, returnJson

#账号登录
class Login(View):

    def __init__(self):
        self.info = {}

    def post(self, request):
        self.info["pwd"] = request.POST.get("pwd")
        self.info["mobile"] = request.POST.get("mobile")

        sql = 'select * from users where mobile=%s and password=%s'
        user_info = queryOne(sql, param=[self.info["mobile"], self.info["pwd"]])
        if not user_info:
            return HttpResponse(returnJson(-2, '登录失败'))

        payload = {'name' : user_info.get('name')}
        token = getToken(payload, 2)
        data = {
            'isAdmin' : user_info.get('isAdmin'),
            'name' : user_info.get('name'),
            'power' : user_info.get('power'),
            'token' : token
        }
        return HttpResponse(returnJson(0, '登录成功', data))

#商户登录
class Store_Login(View):
    
    def post(self, request):
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        mysql = Mysql()
        sql = "SELECT id, store_name, `name`, address \
            FROM store WHERE phone = %s AND `password`=%s"
        check = mysql.getOne(sql, param=[phone, password])
        mysql.dispose()
        if check:
            payload = {
                    'store_name' : check.get('store_name')
            }
            token = getToken(payload, 2)
            data = {'token' : token}
            return HttpResponse(callJson(0, '登录成功', data))
        return HttpResponse(callJson(-2, '登陆失败'))

#测试文件上传
class Test_Files(View):

    def post(self, request):
        files_data = request.FILES.get('file')
        if files_data != 0:
            with open('/home/ubuntu/files/'+files_data.name, 'wb') as f:
                for line in files_data.chunks():
                    f.write(line)
            f.close()
            return HttpResponse(1)
        else:
            return HttpResponse(0)