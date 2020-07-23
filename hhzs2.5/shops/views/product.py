from django.views import View
from django.http import request, HttpResponse

from base.cmysql import Mysql
from base.config import BOOK_ID
from base.shop_base import Pagings, query, returnJson


#商品类
class Product(View):
    
    def post(self, request, **payload):
        handle = payload.get('handle')

        #最新上架
        if handle == "newShop":
            sql = "SELECT id, productName, productImg, hehecoin, minPrice, maxPrice, label \
             FROM product WHERE upper_shelf = 1 ORDER BY create_time DESC LIMIT 0,6"
            return HttpResponse(returnJson(0, '查询成功', query(sql)))

        #热门推荐
        if handle == "hotShop":
            sql = "SELECT id, productName, productImg, hehecoin, minPrice, maxPrice, label \
            FROM product WHERE label = 1 AND upper_shelf = 1"
            return HttpResponse(returnJson(0, '查询成功', query(sql)))

        #搜索商品
        if handle == "selShop":
            stock_name = request.GET.get('pro_name')
            sql = "SELECT * FROM product WHERE upper_shelf = 1 \
                AND state = 1 AND productName LIKE %s"
            return HttpResponse(returnJson(0, '查询成功', query(sql, params=[
                '%' + stock_name + '%'])))

        #搜索书籍
        if handle == "selBook":
            book_name = request.POST.get('book_name')
            mysql = Mysql()
            sql = "SELECT id FROM proclass WHERE parentId = %s"
            pro_class = mysql.getAll(sql, param=[BOOK_ID])

            type_str = ''
            type_str = ",".join([str(i.get('id')) for i in pro_class])
            
            sql = "SELECT * FROM product WHERE productTypeId IN (%s) AND \
                productName LIKE %s AND upper_shelf = 1 AND state = 1"
            data = mysql.getAll(sql, param=[
                type_str,
                '%' + book_name + '%'
            ])
            mysql.dispose()
            return HttpResponse(returnJson(0, '查询成功', query(sql, params=[
                type_str,
                '%' + book_name + '%'
            ])))
        
        #获取商品分类
        if handle == "shopClass":
            parent_id = request.POST.get('parent_id')
            sql = "SELECT * FROM proclass WHERE parentId = %s AND state = 1"
            return HttpResponse(returnJson(0, '查询成功', query(sql, param=[
                parent_id
            ])))

        #商品列表
        if handle == "shopList":
            pro_type = request.POST.get('pro_type')
            sql = "SELECT * FROM product WHERE productTypeId \
                = %s AND upper_shelf = 1"
            return HttpResponse(returnJson(0, '查询成功', query(sql, param=[
                pro_type
            ])))

        #商品详情（从商品列表点击跳到库存商品）
        if handle == "shopDetail":
            pro_id = request.POST.get('pro_id')
            user_id = payload.get('user_id')
            #user_id = request.session.get('user_id') 
            info = {}
            mysql = Mysql()
            sql = "SELECT p.*,t.* FROM product p LEFT JOIN tbHold t ON \
                    CONCAT('product_1909_',p.id)=t.sHoldKey AND t.iUserId = %s \
                    WHERE p.id = %s AND p.upper_shelf = 1"
            info["product"] = mysql.getOne(sql, param=[user_id, pro_id])
            sql = "SELECT s.*, p.remark FROM stock s \
                    LEFT JOIN product p ON s.product_id = p.id \
                    WHERE \
                        s.product_id = %s \
                    AND s.upper_shelf = 1 \
                    AND s.state = 1 \
                    AND p.upper_shelf = 1"
            info["stock"] = mysql.getAll(sql, param=[pro_id])
            mysql.dispose()
            return HttpResponse(returnJson(0, '查询成功', info))
        else:
            return HttpResponse(returnJson(-2, '非法路径' ))

        

