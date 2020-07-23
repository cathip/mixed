#关于对店铺的操作
import datetime
import json
import requests
from django.http import request, JsonResponse, HttpResponse
from base import wx_config
from django.views import View
from base.cmysql import Mysql
from base.shop_base import Pagings, callJson, query, returnJson


#增加店铺
class AddStore(View):

    def post(self, request):
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        store_name = request.POST.get('store_name')
        password = request.POST.get('password')
        mysql = Mysql()
        sql = f"INSERT INTO store SET `name` = '{name}', phone = '{phone}', \
            address = '{address}', `password` = '{password}', store_name = '{store_name}'"
        suc = mysql.insertOne(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#删除店铺
class DelStore(View):

    def post(self, request):
        store_id = request.POST.get('store_id')
        mysql = Mysql()
        sql = f"DELETE FROM store WHERE id = '{store_id}'"
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0) 

#查询店铺
class SelStore(View):

    def get(self, request):
        name = request.GET.get('store_name')
        row = request.GET.get('row')
        page = request.GET.get('page')
        sql = f"SELECT s.*, \
                    sum( \
                        CASE \
                        WHEN p.upper_shelf IS NULL THEN \
                            0 \
                        ELSE \
                            p.upper_shelf \
                        END \
                    ) iRackNum, \
                    count(p.id) iTotalNum \
                FROM \
                    store AS s \
                LEFT JOIN product AS p ON s.id = p.store_id \
                WHERE s.store_name LIKE '%{name}%' \
                GROUP BY s.id"
        info = query(sql)
        if info['result']:
            sum_page, new_info = Pagings.paging(info['result'], row=row, page=page)
            data = {}
            data['sum_page'] = sum_page
            data['info'] = new_info
            info['result'] = data
        return HttpResponse(callJson(data=info))

#编辑店铺
class EditStore(View):

    def post(self, request):
        store_id = request.POST.get('store_id')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        store_name = request.POST.get('store_name')
        password = request.POST.get('password')
        mysql = Mysql()
        sql = f"UPDATE store SET `name` = '{name}', phone = '{phone}', \
            store_name = '{store_name}', `password` = '{password}', address =' {address}' WHERE id = '{store_id}'"
        suc = mysql.update(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#查看店铺里的商品
class StoreProduct(View):

    def get(self, request):
        store_id = request.GET.get('store_id')
        sql = "SELECT * FROM product WHERE store_id = %s"
        info = query(sql, param=[store_id])
        return HttpResponse(returnJson(0, '查询成功', info))