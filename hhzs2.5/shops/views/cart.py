import json

from django.views import View
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.shop_base import returnJson, erroLog, query


class Cart(View):

    def __init__(self):
        self.info = {}

    def post(self, request, **payload):

        handle = payload.get('handle')

        self.info['user_id']  = payload.get('user_id')
        self.info['stock_id'] = request.POST.get('stock_id')
        self.info['num'] = request.POST.get('num')
        self.info['store_id'] = request.POST.get('store_id')
        self.info['cart_id'] = request.POST.get('cart_id')

        if handle == 'see':
            return self.see()

        if handle == 'edit':
            return self.edit()

        if handle == 'add':
            return self.add()

        if handle == 'del':
            return self.del_()

        return HttpResponse(returnJson(-2, '非法路径'))

    def see(self):
        sql = "SELECT \
                c.id as cart_id, \
                c.num, \
                c.store_id, \
                s.id, \
                s.stock_name, \
                s.img, \
                s.product_id, \
                s.stock_detail, \
                s.upper_shelf, \
                s.price, \
                s.hehecoin, \
                p.user_goods_limit, \
                s.stock_num \
            FROM \
                cart AS c \
            LEFT JOIN stock AS s ON c.stock_id = s.id \
            LEFT JOIN product AS p ON s.product_id = p.id \
            WHERE \
                c.userid = %s \
            ORDER BY \
                c.handletime DESC"
        info = query(sql, param=[self.info['user_id']])
        return HttpResponse(returnJson(0, '查询成功', info))

    def edit(self):
        if not isinstance(self.info['num'], int) or int(self.info['num']) <= 0:
            return HttpResponse(returnJson(-2, '商品数量出现错误'))
        mysql = Mysql()
        #新增数量判断
        sql = "SELECT \
                    h.iNumUsed + h.iNumFreeze AS limits, \
                    p.id AS pid, \
                    s.id AS sid,  \
                    p.user_goods_limit, \
                    h.iNumTotal \
                FROM \
                    stock AS s \
                    LEFT JOIN product AS p ON s.product_id = p.id \
                    LEFT JOIN tbHold AS  h ON h.sHoldKey = CONCAT('product_1909_', p.id) \
                WHERE s.id = %s"
        product_id = mysql.getOne(sql, param=[self.info['stock_id']])
        if not product_id:
            mysql.dispose()
            return HttpResponse(returnJson(-2, "库存编号错误"))

        if int(product_id.get('user_goods_limit')) > 0:
            limits = int(product_id.get('limits')) + num if product_id.get('limits') else num
            if limits > int(product_id.get('user_goods_limit')):
                mysql.dispose()
                return HttpResponse(returnJson(-2, "超出限量限制"))

        sql = "UPDATE cart SET num = %s WHERE userid = %s AND \
            stock_id = %s AND store_id = %s"
        suc = mysql.update(sql, param=[
            self.info['num'],
            self.info['user_id'],
            self.info['stock_id'],
            self.info['store_id']
        ])
        mysql.dispose()
        return HttpResponse(returnJson(0, "修改数量成功"))

    def add(self):
        if int(self.info['num']) <= 0:
            return HttpResponse(returnJson(-2, '数量出现错误'))

        mysql = Mysql()
        sql = "SELECT id, num FROM cart WHERE userid=%s AND stock_id=%s AND store_id = %s"
        data = mysql.getOne(sql, param=[
            self.info['user_id'], 
            self.info['stock_id'], 
            self.info['store_id']
        ])
        #新增数量判断
        sql = "SELECT \
                    h.iNumUsed + h.iNumFreeze AS limits, \
                    p.id AS pid, \
                    s.id AS sid,  \
                    p.user_goods_limit, \
                    h.iNumTotal \
                FROM \
                    stock AS s \
                    LEFT JOIN product AS p ON s.product_id = p.id \
                    LEFT JOIN tbHold AS  h ON h.sHoldKey = CONCAT('product_1909_', p.id) AND h.iUserId=%s \
                WHERE s.id = %s"
        product_id = mysql.getOne(sql, param=[
            self.info['user_id'], 
            self.info['stock_id']
        ])

        if not product_id:
            return HttpResponse(returnJson(-2, "库存编号错误"))

        if product_id.get('limits'):
            limits = int(product_id.get('limits')) + self.info['num']  \
                if product_id.get('iNumTotal') else self.info['num']

            limits += int(info.get('num')) if data else 0
            if limits > int(product_id.get('user_goods_limit')):
                return HttpResponse(returnJson(-2, '超出限量限制'))

        #加入购物车
        if data:
            sql = "UPDATE cart SET num = num + %s WHERE userid=%s \
                AND stock_id=%s AND store_id = %s"
            mysql.update(sql, param=[
                self.info['num'],
                self.info['user_id'],
                self.info['stock_id'],
                self.info['store_id']
            ])
        else:                                                         
            sql =  "INSERT INTO cart SET userid = %s, stock_id = %s, \
                num = %s, store_id = %s"
            mysql.insertOne(sql, param=[
                self.info['user_id'],
                self.info['stock_id'],
                self.info['num'],
                self.info['store_id']
            ])
        mysql.dispose()

        return HttpResponse(returnJson(0, "加入购物车成功"))

    def del_(self):
        self.info['cart_id'] = json.loads(self.info['cart_id'])
        if not isinstance(self.info['cart_id'], list):
            return HttpResponse(returnJson(-2, '参数错误'))
        mysql = Mysql()
        for i in self.info['cart_id']:
            sql = "DELETE FROM cart WHERE id = %s"
            mysql.delete(sql, param=[i])
        mysql.dispose()
        return HttpResponse(returnJson(0, '删除成功'))
