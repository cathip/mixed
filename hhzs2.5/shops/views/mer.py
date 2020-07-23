import json
import math
from xml.etree.ElementTree import fromstring

from django.views import View
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.Predis import Open_Redis
from base.shop_base import getOrderNum, Type_Log, Pagings, returnJson, query, erroLog, queryOne, callJson

class Merchant(View):

    def __init__(self):
        self.params = {}

    def post(self, request, **payload):
        handle = payload.get('handle')
        #参数
        self.params['user_id'] = payload.get('user_id')
        self.params['mer_id'] = request.POST.get('mer_id')
        self.params['mer_type'] = request.POST.get('mer_type')
        self.params['product_id'] = request.POST.get('product_id')
        self.params['cart_info'] = request.POST.get('cart_info')
        self.params['page'] = request.POST.get('page')
        self.params['row'] = request.POST.get('row')
        #pay
        self.params['sum_money'] = request.POST.get('sum_money')
        #order
        self.params['phone'] = request.POST.get('phone')
        self.params['name'] = request.POST.get('name')
        
        if handle == 'selMerList':
            return self.selMerList()

        if handle == 'selHotMer':
            return self.selHotMer()

        if handle == 'selRandMer':
            return self.selRandMer()

        if handle == 'selProduct':
            return self.selProduct()

        if handle == 'selProducts':
            return self.selProducts()

        if handle == 'selProductDetail':
            return self.selProductDetail()

        if handle == 'addMerHot':
            return self.addMerHot()

        if handle == 'merCart':
            state = payload.get('state')
            return self.merCart(state)

        if handle == 'payOrder':
            return self.payOrder()
        
        if handle == 'merPay':
            return self.merPay()

        return HttpResponse(returnJson(-2, '非法路径'))

    def selMerList(self):
        sql = "SELECT * FROM merchant WHERE \
            mer_type = %s ORDER BY mer_hot DESC"
        info = query(sql, param=[self.params['mer_type']])
        return HttpResponse(returnJson(0, '查询成功', info))

    def selHotMer(self):
        info = query("SELECT * FROM merchant ORDER BY mer_hot DESC LIMIT 3")
        return HttpResponse(returnJson(0, '查询成功', info))

    def selRandMer(self):
        info = query("SELECT * FROM merchant ORDER BY RAND() LIMIT 3")
        return HttpResponse(returnJson(0, '查询成功', info))

    def selProduct(self):
        mysql = Mysql()
        sql = "SELECT * FROM mer_product WHERE mer_id = %s limit %s, %s"
        page, row = Pagings.mysqlPagings(self.params['page'], self.params['row'])
        product = mysql.getAll(sql, param=[
            self.params['mer_id'],
            page,
            row
        ])
        for i in product:
            sql = "SELECT * FROM mer_stock WHERE product_id = %s"
            stock = mysql.getAll(sql, param=[i.get('product_id')])
            if stock:
                i['stock'] = stock
                sql = "SELECT spec_id, spec_name FROM mer_spec WHERE product_id = %s"
                spec_name = mysql.getAll(sql, param=[i.get('product_id')])
                spec_info = []
                if stock[0].get('stock_specs'):
                    for x in spec_name:
                        spec_deatil_dic = {}
                        spec_deatil_dic['spec'] = x
                        sql = "SELECT spec_detail_id, detail_name FROM mer_specdetail \
                            WHERE spec_id = %s"
                        spec_detail = mysql.getAll(sql, param=[x.get('spec_id')])
                        spec_deatil_dic['spec_detail'] = spec_detail
                        spec_info.append(spec_deatil_dic)
                    i['spec_info'] = spec_info
        mysql.dispose()
        return HttpResponse(returnJson(0, '查询成功', product))

    def selProducts(self):
        return HttpResponse(-2, '维护中')

    def selProductDetail(self):
        data = {}
        mysql = Mysql()
        sql = "SELECT * FROM mer_stock WHERE product_id = %s"
        stock = mysql.getAll(sql, param=[self.params['product_id']])
        if stock:
            data['stock'] = stock
            sql = "SELECT spec_id, spec_name FROM mer_spec WHERE product_id = %s"
            spec_name = mysql.getAll(sql, param=[self.params['product_id']])
            spec_info = []
            if stock[0].get('stock_specs'):
                for i in spec_name:
                    spec_deatil_dic = {}
                    spec_deatil_dic['spec'] = i
                    sql = "SELECT spec_detail_id, detail_name FROM mer_specdetail \
                        WHERE spec_id = %s"
                    spec_detail = mysql.getAll(sql, param=[i.get('spec_id')])
                    spec_deatil_dic['spec_detail'] = spec_detail
                    spec_info.append(spec_deatil_dic)
                data['spec_info'] = spec_info
        mysql.dispose()
        return HttpResponse(returnJson(0, '查询成功', data))

    def addMerHot(self):
        self.params['hot_numbs'] = int(request.POST.get('hot_numbs'))
        if self.params['hot_numbs'] > 5 or self.params['hot_numbs'] < 1:
            return HttpResponse(returnJson(-2, '增加热度失败'))
            
        mysql = Mysql()
        sql = "SELECT id FROM mer_hots WHERE mer_id = %s AND user_id = %s"
        check = mysql.getOne(sql, param=[
            self.params['mer_id'], 
            self.params['user_id']
        ])
        if check:
            mysql.dispose()
            return HttpResponse(returnJson(-2, '已增加过热度，不能重复'))

        sql = "INSERT INTO mer_hots SET mer_id = %s, user_id = %s, hots = %s"
        ins_suc = mysql.insertOne(sql, param=[
            self.params['mer_id'], 
            self.params['user_id'], 
            self.params['hot_numbs']
        ])
        sql = "UPDATE merchant SET mer_hot = mer_hot + %s, \
            mer_hot_numbs = mer_hot_numbs + 1 WHERE mer_id = %s"
        up_suc = mysql.update(sql, param=[
            self.params['hot_numbs'], 
            self.params['mer_id']
        ])
        mysql.dispose()
        return HttpResponse(returnJson(0, '增加热度成功'))

    def merCart(self, state):
        cache_name = str(self.params['user_id']) + 'mercart'
        if state == 'edit':
            open_redis = Open_Redis().getConn(1)
            open_redis.set(cache_name, self.params['cart_info'], ex=9000)
            return HttpResponse(returnJson(0, '操作成功'))
        if state == 'get':
            open_redis = Open_Redis().getConn(1)
            info = open_redis.get(cache_name)
            info = json.loads(info) if info else []
            return HttpResponse(returnJson(0, '查询成功', info))
        return HttpResponse(returnJson(-2, '非法路径'))

    def payOrder(self):
        
        self.params['order_num'] = getOrderNum('MerOrder-')
        self.params['stock_list'] = json.loads(request.POST.get('stock_list'))
        #[{'stockid':1, 'product_img':sss,'stocknum':33}, {'stockid':1, 'stocknum':33}]
        print(self.params)
        cache_name = 'mer_order-' + self.params['order_num']
        mysql = Mysql()
        # -------------------先做限量判定 如果 超过 返回2-------------------
        for x in self.params['stock_list']:
            sql = "SELECT min_buy, max_buy FROM mer_stock WHERE stock_id = %s"
            check = mysql.getOne(sql, param=[x.get('stockid')])
            min_buy = int(check.get('min_buy'))
            max_buy = int(check.get('max_buy'))
            stock_num = int(x.get('stocknum'))
            if (min_buy > stock_num or max_buy < stock_num) and min_buy != 0 and max_buy != 0:
                mysql.dispose()
                return HttpResponse(2)
        # -------------------插入到订单表-----------------
        sql = "INSERT INTO mer_orders SET order_num=%s, \
            mer_id=%s, user_id=%s, `name`=%s, phone=%s"
        order_id = mysql.insertOne(sql, param=[
            self.params['order_num'],
            self.params['mer_id'],
            self.params['user_id'],
            self.params['name'],
            self.params['phone']
        ])
        price_list = []
        hhcoin_list = []
        for i in self.params['stock_list']:
            sql = "SELECT price, hhcoin, stock_name FROM mer_stock WHERE \
                stock_id = %s"
            stock_info = mysql.getOne(sql, param=[i.get('stockid')])
            price_list.append(
                int(stock_info.get('price'))
                * int(i.get('stocknum')))
            hhcoin_list.append(
                int(stock_info.get('hhcoin'))
                * int(i.get('stocknum')))
            sql = "INSERT INTO mer_ordergoods SET order_num=%s, \
                mer_stockid=%s, mer_stockprice=%s, mer_stockhhcoin=%s, \
                mer_stockname=%s, mer_stocknum=%s, mer_product_img=%s "
            mysql.insertOne(sql=sql, param=[
                self.params['order_num'], 
                i.get('stockid'), 
                stock_info.get('price'),
                stock_info.get('hhcoin'),
                stock_info.get('stock_name'),
                i.get('stocknum'),
                i.get('product_img')
            ])
        # 一个盒盒币0.1元
        price = sum(price_list)
        hhcoin = sum(hhcoin_list)
        # ----------------------余额支付----------------------
        user_info = mysql.getOne("SELECT money, hhcoin \
            FROM userInfo WHERE id = %s", param=[self.params['user_id']])
        user_price = int(user_info.get('money'))
        user_hhcoin = int(user_info.get('hhcoin'))
        #--------------------初始化参数-----------------
        real_coin = 0   #实际要扣除的盒盒币
        real_balance = 0    #实际要支付的盒盒余额
        real_wxprice = 0    #额外需要微信支付价格
        #-------------抵扣盒盒币--------------------
        real_coin = hhcoin if user_hhcoin >= hhcoin else user_hhcoin
        if real_coin > 0:
            # 扣盒盒币
            up_sql, log_sql = Type_Log.coin_handle(user_id=self.params['user_id'], 
                                                    handle=1, num=real_coin, asd=0)
            mysql.update(up_sql)
            mysql.update(log_sql)
        real_wxprice = price - real_coin
        #-----------抵扣余额---------------
        real_balance = real_wxprice if user_price >= real_wxprice else user_price
        if real_balance>0:
            #扣余额
            up_sql, log_sql = Type_Log.balance_log(user_id=self.params['user_id'],
                                                    handle=1, money=real_balance, asd=0, 
                                                    order_num=self.params['order_num'])
            mysql.update(up_sql)
            mysql.update(log_sql)
        #(实际需要支付的微信价钱)
        real_wxprice = real_wxprice - real_balance
        #---------微信支付尾款（是否需要微信支付）-------
        data = {}
        data['order_num'] = self.params['order_num']
        data['balance'] = real_balance
        data['hhcoin'] = real_coin
        state = 1 if real_wxprice == 0 else 0 #订单状态 0未付款 1代发货
        pay_time = 'NOW()' if state == 1 else 'NULL'
        if state == 1:
            #微信不需要再付钱
            data['msg'] = 'OK'
        else:
            #需要微信支付尾款
            data['msg'] = 'FAIL'
            data['res_price'] = real_wxprice
            data['erro_info'] = '已扣除盒盒币，请微信支付尾款！'
            open_redis = Open_Redis().getConn(2)
            cache = callJson(data)
            open_redis.set(cache_name, cache, ex=900)
        sql = "UPDATE mer_orders SET order_money=%s, wx_money='0', \
                balance=%s, hh_coin=%s, state=%s, `get`=0, \
                pay_time=%s WHERE order_id=%s"
        mysql.update(sql, param=[
            real_balance + real_wxprice,
            real_balance,
            real_coin,
            state,
            pay_time,
            order_id
        ]) 
        mysql.dispose()
        return HttpResponse(callJson(data))

    def merPay(self):
        self.params['order_num'] = getOrderNum('MerPay-')
        self.params['sales'] = float(request.POST.get('sales')) / 100
        cache_name = 'mer_pay-' + self.params['order_num']

        if not self.params['mer_id'] or not self.params['user_id']:
            return HttpResponse(0)
        if self.params['sum_money'] <= 0:
            return HttpResponse(0)

        mysql = Mysql()
        hhcoin = int(self.params['sum_money'] - (self.params['sum_money'] * self.params['sales']))
        if hhcoin < 1:
            hhcoin = 0
        price = self.params['sum_money']
        # ---------------------插入订单表---------------------
        sql = "INSERT INTO mer_pay SET mer_id = %s, user_id = %s,\
                order_num = %s, order_money = %s, state = 0"
        order_id = mysql.insertOne(sql, param=[
            self.params['mer_id'],
            self.params['user_id'],
            self.params['order_num'],
            price
        ])
        # ----------------------余额支付----------------------
        user_info = mysql.getOne("SELECT money, hhcoin \
            FROM userInfo WHERE id = %s", param=[self.params['user_id']])
        user_price = int(user_info.get('money'))
        user_hhcoin = int(user_info.get('hhcoin'))
        #--------------------初始化参数-----------------
        real_coin = 0   #实际要扣除的盒盒币
        real_balance = 0    #实际要支付的盒盒余额
        real_wxprice = 0    #额外需要微信支付价格
        #-------------抵扣盒盒币--------------------
        real_coin = hhcoin if user_hhcoin >= hhcoin else user_hhcoin
        if real_coin > 0:
            # 扣盒盒币
            up_sql, log_sql = Type_Log.coin_handle(user_id=self.params['user_id'], 
                                                    handle=1, num=real_coin, asd=0)
            mysql.update(up_sql)
            mysql.update(log_sql)
        real_wxprice = price - real_coin
        #-----------抵扣余额---------------
        real_balance = real_wxprice if user_price >= real_wxprice else user_price
        if real_balance > 0:
            #扣余额
            up_sql, log_sql = Type_Log.balance_log(user_id=self.params['user_id'],
                                                    handle=1, money=real_balance, asd=0, 
                                                    order_num=self.params['order_num'])
            mysql.update(up_sql)
            mysql.update(log_sql)
        #(实际需要支付的微信价钱)
        real_wxprice = real_wxprice - real_balance
        #---------微信支付尾款（是否需要微信支付）-------
        data = {}
        data['order_num'] = self.params['order_num']
        data['balance'] = real_balance
        data['hhcoin'] = real_coin
        state = 1 if real_wxprice == 0 else 0 #订单状态 0未付款 1代发货
        if state==1:
            #微信不需要再付钱
            data['msg'] = 'OK'
        else:
            #需要微信支付尾款
            data['msg'] = 'FAIL'
            data['res_price'] = real_wxprice
            data['erro_info'] = '已扣除盒盒币，请微信支付尾款！'
            # 挂起待支付订单
            t = Open_Redis(2)
            open_redis = t.getConn()
            cache = callJson(data)
            open_redis.set(cache_name, cache, ex=900)
        sql = "UPDATE mer_pay SET order_money=%s, wx_money='0', \
                balance=%s, hhcoin=%s, state=%s WHERE id=%s"
        mysql.update(sql, param=[
            self.params['sum_money'],
            real_balance,
            real_coin,
            state,
            order_id
        ]) 
        mysql.dispose()
        return HttpResponse(callJson(data))

    