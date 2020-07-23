import json
import math

from django.views import View
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.shop_base import Pagings, ComplexEncode, query,  callJson, erroLog


'''
有关商品（商品列表）的一切操作
添加不用（添加是随着上架库存一起的） 
'''

#添加商品
class Add_Product(View):

    def __init__(self):
        self.info = {}

    def post(self, request):
        try:
            self.info['store_id'] = request.POST.get('store_id')
            self.info['type_id'] = request.POST.get('type_id')
            self.info['product_name'] = request.POST.get('product_name')
            self.info['user_goods_limit'] = request.POST.get('user_goods_limit')
            self.info['product_img'] = request.POST.get('product_img') #列表取第一张 多张逗号分隔
            self.info['hhcoin'] = request.POST.get('hhcoin')
            self.info['price'] = request.POST.get('price')
            self.info['remark'] = request.POST.get('remark')
            self.info['notes'] = request.POST.get('notes')
            mysql = Mysql()
            sql = "INSERT INTO product SET productTypeId=%s, productName=%s, \
                    user_goods_limit=%s, productImg=%s, upper_shelf=0, \
                    hehecoin=%s, minPrice=%s, maxPrice=%s, label=0, \
                    remark=%s, store_id=%s, notes=%s"
            mysql.insertOne(sql, param=[
                self.info['type_id'],
                self.info['product_name'],
                self.info['user_goods_limit'],
                self.info['product_img'],
                self.info['hhcoin'],
                self.info['price'],
                self.info['price'],
                self.info['remark'],
                self.info['store_id'],
                self.info['notes']
            ])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '添加商品成功'
            })
        except Exception as e:
            print(e)
            mysql.errdispose()
            erroLog(e)
            return JsonResponse({
                'ret' : -2,
                'msg' : '添加商品失败'
            })

#删除商品
class Del_Product(View):
    
    def post(self, request):
        try:
            product_id = request.POST.get('product_id')
            mysql = Mysql()
            sql = "SELECT * FROM product WHERE id = %s AND upper_shelf=1"
            check = mysql.getOne(sql, param=[product_id])
            if check:
                mysql.dispose()
                return JsonResponse({
                    'ret' :-2,
                    'msg' : '删除失败 商品上架中'
                })
            sql = "UPDATE product SET state = 0 WHERE id = %s"
            mysql.update(sql, param=[product_id])
            sql = "UPDATE stock SET state = 0 WHERE product_id = %s"
            mysql.update(sql, param=[product_id])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '删除成功'
            })
        except Exception as e:
            print(e)
            mysql.errdispose()
            erroLog(e)
            return JsonResponse({
                'ret' : -2,
                'msg' : '删除失败'
            })

#编辑商品
class Edit_Product(View):

    def __init__(self):
        self.info = {}

    def post(self, request):
        try:
            self.info['product_id'] = request.POST.get('product_id')
            self.info['productTypeId'] = request.POST.get('type_id')
            self.info['productName'] = request.POST.get('product_name')
            self.info['productImg'] = request.POST.get('product_img')
            self.info['hehecoin'] = request.POST.get('hhcoin')
            self.info['price'] = request.POST.get('price')
            self.info['remark'] = request.POST.get('remark')
            self.info['notes'] = request.POST.get('notes')
            self.info['user_goods_limit'] = request.POST.get('user_goods_limit') #个人总限量
            mysql = Mysql()
            sql = "UPDATE product SET productTypeId=%s, productName=%s,\
                productImg=%s, hehecoin=%s, minPrice=%s, user_goods_limit=%s,\
                maxPrice=%s, remark=%s, notes=%s WHERE id=%s"
            mysql.update(sql, param=[
                self.info['productTypeId'],
                self.info['productName'],
                self.info['productImg'],
                self.info['hehecoin'],
                self.info['price'],
                self.info['user_goods_limit'],
                self.info['price'],
                self.info['remark'],
                self.info['notes'],
                self.info['product_id']
               
            ])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '编辑商品成功'
            })
        except Exception as e:
            print(e)
            mysql.errdispose()
            erroLog(e)
            return JsonResponse({
                'ret' : -2,
                'msg' : '编辑商品失败'
            })

#商品列表
class Sel_Product(View):

    def get(self, request):
        page = request.GET.get('page')
        row = request.GET.get('row')
        store_id = request.GET.get('store_id', False)  #店铺id
        product_name = request.GET.get('product_name', '') #名字 不传返全部
        upper_shelf = request.GET.get('upper_shelf', False) #1上架 0下架, 不传就全部
        
        sql = f"SELECT \
                    p.id, \
                    p.store_id, \
                    p.productName, \
                    p.productImg, \
                    p.hehecoin, \
                    p.minPrice AS price, \
                    p.user_goods_limit, \
                    p.remark, \
                    p.label, \
                    p.notes, \
                    upper_shelf, \
                    s.store_name, \
                    p.productTypeId AS ziji_id, \
                    pc.`name` AS ziji_name, \
                    pc.parentId AS fuji_id, \
                    pc1.`name` AS fuji_name \
                FROM \
                    product p \
                LEFT JOIN proclass pc ON p.productTypeId = pc.id \
                LEFT JOIN proclass pc1 ON pc.parentId = pc1.id \
                LEFT JOIN store s ON p.store_id = s.id \
                WHERE \
                    p.productName LIKE '%{product_name}%' \
                    AND p.state = 1 "

        if upper_shelf:
            sql = sql + f"AND p.upper_shelf = {upper_shelf} "
        if store_id:
            sql = sql + f"AND p.store_id = {store_id} "
        sql = sql + 'ORDER BY p.create_time DESC'
        info = query(sql)

        if info['result']:
            sum_page, new_info = Pagings.paging(info['result'], row=row, page=page)
            data = {}
            data['sum_page'] = sum_page
            data['info'] = new_info
            info['result'] = data
        return HttpResponse(callJson(data=info))
        
#查找商品对应的库存商品
class Product_Stock(View):
    
    def get(self, request):
        product_id = int(request.GET.get('product_id'))
        mysql = Mysql()
        sql = "SELECT * FROM stock WHERE product_id = %s AND state = 1"
        info = mysql.getAll(sql, param=[product_id])
        mysql.dispose()
        if info:
            return HttpResponse(callJson(info))
        return HttpResponse(0)

#设置热门商品
class Set_HotPorduct(View):

    def post(self, request):
        product_id = request.POST.get('product_id')
        mysql = Mysql()
        try:
            sql = "UPDATE product SET label='1' WHERE id=%s"
            mysql.update(sql, param=[product_id])
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#删除热门商品
class Del_HotPorduct(View):

    def post(self, request):
        product_id = request.POST.get('product_id')
        mysql = Mysql()
        try:
            sql = "UPDATE product SET label='0' WHERE id=%s"
            mysql.update(sql, param=[product_id])
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)
