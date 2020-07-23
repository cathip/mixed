#utf-8

import json
import html

from django.views import View
from django.http import JsonResponse, HttpResponse

from base.cmysql import Mysql
from base.shop_base import callJson


class AddAdminer(View):
    '''
    增加管理员
    '''
    def get_param(self, request):
        self.Info = {}
        self.Info['username'] = request.POST.get('username')
        self.Info['phone'] = request.POST.get('phone')
        self.Info['Pwd'] = request.POST.get('Pwd')
        self.Info['Isin'] = request.POST.get('Isin')   # 在职为1, 否则为0
        self.Info['isAdmin'] = request.POST.get('isAdmin')  # 管理员为1， 否则为0
        self.Info['private'] = request.POST.get('power')  # 页面权限


    def post(self, request):
        self.get_param(request)
        mysql = Mysql()
        sql = "insert into users(mobile, name, password, state, isAdmin, power) \
            value (%s, %s, %s, %s, %s, %s)"
        state = mysql.insertOne(sql, param=[
            self.Info['phone'],
            self.Info['username'],
            self.Info['Pwd'],
            self.Info['Isin'],
            self.Info['isAdmin'],
            self.Info['private']
        ])
        mysql.dispose()
        state = 1 if state else 0
        return JsonResponse({'state': state})

class AllAdminer(View):
    '''
    获取管理员列表
    '''
    def get(self, request):
        mysql = Mysql()
        sql = 'select * from users'
        data = mysql.getAll(sql)
        mysql.dispose()
        return JsonResponse({
            'ret' : 0,
            'msg' : '查询成功',
            'result' : data
        })

class DelAdminer(View):
    '''
    删除管理员
    '''
    def get(self, request):
        admin_id = request.GET.get('id')
        mysql = Mysql()
        sql = 'delete from users where id=%s'
        state = mysql.delete(sql, param=[
            admin_id
        ])
        mysql.dispose()
        state = 1 if state else 0
        return JsonResponse({'state': state})

class UpAdminer(View):
    '''
    账户编号
    '''
    def __init__(self):
        self.Info = {}

    def get_param(self, request):
        self.Info['id'] = request.POST.get('id')   # 管理员编号
        self.Info['username'] = request.POST.get('username')
        self.Info['phone'] = request.POST.get('phone')
        self.Info['Pwd'] = request.POST.get('Pwd')
        self.Info['Isin'] = request.POST.get('Isin')   # 在职为1, 否则为0
        self.Info['isAdmin'] = request.POST.get('isAdmin')  # 管理员为1， 否则为0
        self.Info['private'] = str(request.POST.get('power')) # 页面权限

    def post(self, request):
        self.get_param(request)
        mysql = Mysql()
        sql = "update users set mobile=%s, name=%s, password=%s, \
                state=%s, isAdmin=%s, power=%s where id=%s" 
        state = mysql.update(sql, param=[
            self.Info['phone'],
            self.Info['username'],
            self.Info['Pwd'],
            self.Info['Isin'],
            self.Info['isAdmin'],
            self.Info['private'],
            self.Info['id']
        ])
        mysql.dispose()
        return JsonResponse({'state': state})

class Get_Power(View):

    def get(self, request, **payload):
        user = request.GET.get('user')
        mysql = Mysql()
        sql = f"SELECT power FROM users WHERE mobile = '{user}'"
        check = mysql.getOne(sql)
        mysql.dispose()
        if check:
            return JsonResponse(check)
        return HttpResponse(0)