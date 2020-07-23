import json
from django.http import request, HttpResponse, QueryDict, JsonResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import Pagings, ComplexEncode
import re

#添加库存商品
class Add_Stock(View):
    
    def post(self, request):
        store_id = request.POST.get('store_id')
        stock_json = json.loads(request.POST.get('stock_json'))
        # [{
        #     'stock_name' : stock_name,
        #     'price' : price,
        #     'buying_price' : buying_price,
        #     'hehecoin' : hehecoin,
        #     'img' : img,
        #     'stock_guige': stock_guige,
        #     'product_id' : 22,
        #     'store_id' : 33
        # }]
        print(stock_json)
        try:
            mysql = Mysql()
            # sql = "INSERT INTO stock SET stock_name=%s , price=%s, \
            #     hehecoin=%s, img=%s, upper_shelf=0, store_id=%s, \
            #     stock_detail=%s, buying_price=%s, product_id=%s"
            # stock_id = mysql.insertOne(sql, param=[
            #     stock_json.get('stock_name'),
            #     stock_json.get('price'),
            #     stock_json.get('hehecoin'),
            #     stock_json.get('img'),
            #     stock_json.get('store_id'),
            #     stock_json.get('stock_guige'),
            #     stock_json.get('buying_price'),
            #     stock_json.get('product_id')
            # ])
            sql = "INSERT INTO stock SET stock_name=%s , price=0, \
                hehecoin=0, upper_shelf=0, store_id=%s, \
                stock_detail=%s, buying_price=0, product_id=%s"
            stock_id = mysql.insertOne(sql, param=[
                stock_json.get('stock_name'),
                stock_json.get('store_id'),
                stock_json.get('stock_guige'),
                stock_json.get('product_id')
            ])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '新增库存成功',
                'stock_id' : stock_id
            })
        except Exception as e:
            print('----------插入库存商品出现错误-------------')
            mysql.errdispose()
            return JsonResponse({
                'ret' : -2,
                'msg' : '新增库存失败'
            })        

#编辑库存商品
class Edit_Stock(View):
    
    def post(self, request):
        try:
            stock_json = json.loads(request.POST.get('stock_json'))
        
            mysql = Mysql()
            sql = "UPDATE stock SET  price=%s, \
                    hehecoin=%s, img=%s, upper_shelf=1,\
                    stock_detail=%s, buying_price=%s WHERE id=%s"
            suc = mysql.update(sql, [
                stock_json.get('price'),
                stock_json.get('hehecoin'),
                stock_json.get('img'), #首张图片（关系到购物车）
                stock_json.get('stock_guige'),
                stock_json.get('buying_price'),
                stock_json.get('stock_id')
            ])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '编辑库存成功'
            })
            
        except Exception as e:
            print(e)
            mysql.errdispose()
            return JsonResponse({
                'ret' : -2,
                'msg' : '编辑库存失败'
            })  

#删除库存商品
class Del_Stock(View):

    def post(self, request):
        stock_id = request.POST.get('stock_id')
        try:
            mysql = Mysql()
            sql = "UPDATE stock SET state = 0 WHERE id = %s"
            mysql.update(sql, param=[stock_id])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '删除成功'
            })
        except Exception as e:
            print(e)
            mysql.errdispose()
            return JsonResponse({
                'ret' : -2,
                'msg' : '删除失败'
            })

#上架商品
class Upper_Shelf(View):
    
    def post(self, request):
        try:   
            product_id = request.POST.get('product_id')
            mysql = Mysql()
            sql = "SELECT * FROM stock WHERE product_id = %s  AND state = 1"
            stock_info = mysql.getAll(sql, param=[product_id])
            if not stock_info:
                mysql.dispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '没有库存不能上架'
                })
            sql = "UPDATE product SET upper_shelf = 1 WHERE id = %s"
            mysql.update(sql, param=[product_id])
            sql = "UPDATE stock SET upper_shelf = 1 WHERE product_id = %s"
            mysql.update(sql, param=[product_id])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '上架成功'
            })
        except Exception as e:
            print(e)
            mysql.errdispose()
            return JsonResponse({
                    'ret' : -2,
                    'msg' : '上架出现错误'
                })

#下架商品
class Lower_Shelf(View):
    
    def post(self, request):
        
        try:
            mysql = Mysql()
            product_id = request.POST.get('product_id')
            sql = "UPDATE product SET upper_shelf = 0 WHERE id = %s"
            mysql.update(sql, param=[product_id])
            sql = "UPDATE stock SET upper_shelf = 0 WHERE product_id = %s"
            mysql.update(sql, param=[product_id])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '下架成功'
            })
        except Exception as e:
            mysql.errdispose()
            print(e)
            return JsonResponse({
                    'ret' : -2,
                    'msg' : '下架失败'
                })

#下架库存
class Lower_Stock(View):

    def post(self, request):
        try:
            stock_id = request.POST.get('stock_id')
            mysql = Mysql()
            sql = "UPDATE stock SET upper_shelf = 0 WHERE id = %s"
            mysql.update(sql, param=[stock_id])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '更新成功'
            })
        except Exception as e:
            print(e)
            mysql.errdispose()
            return JsonResponse({
                'ret' : -2,
                'msg' : '更新失败'
            })

#测试
class Test(View):
    
    #更新商家字段
    def get(self, request):
        try:
            mysql = Mysql()
            sql = "SELECT product_id, store_id FROM stock \
                WHERE product_id IS NOT NULL GROUP BY product_id "
            store_info = mysql.getAll(sql)
            for i in store_info:
                sql = "UPDATE product SET store_id=%s WHERE id=%s"
                mysql.update(sql, param=[
                    i.get('store_id'),
                    i.get('product_id')
                ])
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            mysql.errdispose()
            return HttpResponse(0)

    #更新商品图片
    def post(self, request):
        try:
            mysql = Mysql()
            sql = "SELECT product_id, new_img FROM stock \
                WHERE product_id IS NOT NULL GROUP BY product_id "
            store_info = mysql.getAll(sql)
            for i in store_info:
                sql = "UPDATE product SET productImg=%s WHERE id=%s"
                mysql.update(sql, param=[
                    i.get('new_img'),
                    i.get('product_id')
                ])
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            mysql.errdispose()
            return HttpResponse(0)