#utf-8

import time
import json
import requests
import datetime

from django.views import View
from django.utils.decorators import method_decorator
from django.http import request, JsonResponse, HttpResponse, QueryDict

from base.cmysql import Mysql

from base.shop_base import Type_Log, erroLog, returnJson, query, queryOne


#用户类       
class User(View):

    def __init__(self):
        self.info = {}

    def post(self, request, **payload):
        
        handle = payload.get('handle')
        self.info['user_id'] = payload.get('user_id')
        self.info['img'] = request.POST.get('img')
        self.info['wxname'] = request.POST.get('wxname')
        self.info['unionid'] = request.POST.get('unionid')

        if handle == 'sel':
            return self.getData()

        if handle == 'update':
            erro_list = ['[object Object]']
            if self.info['unionid'] in erro_list or not self.info['unionid']:
                return HttpResponse(returnJson(-2, '参数错误'))
            return self.update()

        if handle == 'debug':
            err_info = request.POST.get('err_info')
            sql = 'INSERT INTO erro_log SET erro_detail = %s'
            mysql = Mysql()
            mysql.insertOne(sql, param=[err_info])
            mysql.dispose()
            return HttpResponse(returnJson(0, '记录成功'))

        return HttpResponse(returnJson(-2, '非法路径'))
            

    def getData(self):
        mysql = Mysql()
        sql = 'SELECT \
                    u.money, u.hhcoin, \
                    s.school_name, \
                    s.school_img, \
                    s.id as school_id, \
                    u.openid, \
                    u.id as user_id, \
                    u.mobile, \
                    u.wxname \
                FROM \
                    userInfo AS u \
                LEFT JOIN school AS s ON u.school_id = s.id \
                WHERE u.id = %s'
        data = mysql.getOne(sql, param=[self.info['user_id']])
        #------增加盒盒币
        sql = '''SELECT \
                    d.id as did, \
                    d.hhcoin, \
                    d.state, \
                    u.id, \
                    u.openid \
                FROM \
                    deliverCoin AS d \
                LEFT JOIN gzh_user AS g ON d.gzh_openid = g.openid \
                LEFT JOIN userInfo AS u ON u.unionId = g.unionid \
                WHERE u.unionId IS NOT NULL AND d.state = 0 AND u.openid = %s \
                GROUP BY d.id '''
        info = mysql.getAll(sql, param=[data.get('openid')])
        if info:
            for i in info:
                if i.get('hhcoin') != 0:
                    up_sql, ins_sql = Type_Log.coin_handle(
                        user_id=i.get('id'), handle=5, num=i.get('hhcoin'), asd=1)
                    up_suc = mysql.update(up_sql)
                    ins_suc = mysql.insertOne(ins_sql)
                    sql = "UPDATE deliverCoin SET state = 1 WHERE id = %s"
                    mysql.update(sql, param=[i.get('did')])
        mysql.dispose()
        return HttpResponse(returnJson(0, '查询成功', data))

    def update(self):
        mysql = Mysql()
        sql = "SELECT * FROM userInfo WHERE id = %s FOR UPDATE"
        mysql.getOne(sql, param=[self.info['user_id']])
        sql = "update userInfo set wxname=%s, user_img=%s, \
            unionId=%s where id = %s"
        mysql.update(sql, param=[
            self.info['wxname'],
            self.info['img'],
            self.info['unionid'],
            self.info['user_id']
        ])
        mysql.dispose()
        return HttpResponse(returnJson(0, '更新用户信息成功'))

#默认地址
class Default_address(View):

    def post(self, request, **payload):
        
        user_id = payload.get('user_id')
        handle = payload.get('handle')

        address_id = request.POST.get('address_id')
        

        mysql = Mysql()
        if handle == 'edit':
            sql = "UPDATE userInfo SET address_id=%s WHERE id=%s"
            mysql.update(sql, param=[address_id, user_id])
            mysql.dispose()
            return HttpResponse(returnJson(0, '更新成功'))
        if handle == 'get':
            mysql = Mysql()
            sql = "SELECT address_id from userInfo WHERE id=%s"
            info = mysql.getOne(sql, param=[user_id])
            mysql.dispose()
            info = info if info else []
            return HttpResponse(returnJson(0, '查询成功', info))
        if handle == 'del':
            mysql = Mysql()
            sql = "UPDATE userInfo SET address_id = null WHERE id=%s"
            mysql.update(sql, param=[user_id])
            mysql.dispose()
            return HttpResponse(returnJson(0, '删除成功'))
        if handle == 'default':
            pass
        else:
            return HttpResponse(returnJson(-2, '参数错误'))

#地址列表
class Address(View):

    def post(self, request, **payload):
        handle = payload.get('handle')
        user_id = payload.get('user_id')

        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        address_id = request.POST.get('address_id')
        
        
        if handle == 'add':
            mysql = Mysql()
            sql = "INSERT INTO user_address SET user_id=%s, `name`=%s, \
            phone=%s, address=%s"
            add_id = mysql.insertOne(sql, param=[
                user_id,
                name,
                phone,
                address
            ])
            add_id = {'add_id' : add_id}
            mysql.dispose()
            return HttpResponse(returnJson(0, '新增地址成功', add_id))

        if handle == 'get':
            sql = "SELECT * FROM user_address WHERE user_id=%s"
            info = query(sql, param=[user_id])
            return HttpResponse(returnJson(0, '查询成功', info))

        if handle == 'edit':
            mysql = Mysql()
            sql = "UPDATE user_address SET user_id=%s, `name`=%s, \
            phone=%s, address=%s WHERE id=%s"
            mysql.update(sql, param=[
                user_id,
                name,
                phone,
                address,
                address_id
            ])
            mysql.dispose()
            return HttpResponse(returnJson(0, '编辑地址成功'))

        if handle == 'del':
            mysql = Mysql()
            sql = "DELETE FROM user_address WHERE id=%s"
            suc = mysql.delete(sql, param=[address_id])
            mysql.dispose()
            return HttpResponse(returnJson(0, '删除成功'))
