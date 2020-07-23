import json
import math
from xml.etree.ElementTree import fromstring

from django.views import View
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.Predis import Open_Redis
from base.shop_base import ComplexEncode, Type_Log, Pagings, callJson, erroLog



# 查看商户
class Sel_Merchant(View):

    def get(self, request, **payload):
        self.params = {}
        self.params['mer_name'] = request.GET.get('mer_name')
        self.params['mer_id'] = request.GET.get('mer_id')
        self.params['mer_type'] = request.GET.get('mer_type')
        mysql = Mysql()
        if self.params['mer_id']:
            sql = f"SELECT * FROM merchant WHERE mer_id={self.params['mer_id']}"
        else:
            sql = "SELECT * FROM merchant WHERE mer_name LIKE '%{mer_name}%' \
                AND mer_type LIKE '%{mer_type}%' ORDER BY mer_hot DESC".format(mer_name=self.params['mer_name'],
                                                                               mer_type=self.params['mer_type'])
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            return HttpResponse(callJson(info))
        return HttpResponse(0)

# 查看商户的商品
class Sel_MerProduct(View):

    def get(self, request, **payload):
        self.params = {}
        self.params['mer_id'] = request.GET.get('mer_id')
        mysql = Mysql()
        sql = "SELECT * FROM mer_product WHERE mer_id = %s"
        info = mysql.getAll(sql, param=[self.params['mer_id']])
        mysql.dispose()
        if info:
            return HttpResponse(callJson(info))
        return HttpResponse(0)

class Sel_MerProducts(View):
    
    def get(self, request, **payload):
        mer_id = request.GET.get('mer_id') # list
        mer_id = json.loads(mer_id)
        mysql = Mysql()
        data = {}
        for i in mer_id:
            sql = "SELECT * FROM mer_product WHERE mer_id = %s"
            product = mysql.getAll(sql, param=i)
            product = product if product else []
            data[i] = product
        mysql.dispose()
        return HttpResponse(callJson(data))

# 点击商品选择规格价钱（查看库存）
class Sel_MerStock(View):

    def get(self, request, **payload):
        self.params = {}
        self.params['product_id'] = request.GET.get('product_id')
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
            return HttpResponse(callJson(data))
        mysql.dispose()
        return HttpResponse(0)

# 查看用户订单
class Sel_MerOrder(View):

    def get(self, request, **payload):
        self.params = {}
        self.params['user_id'] = payload.get('user_id')
        mysql = Mysql()
        sql = "SELECT mer_orders.*, merchant.mer_name FROM mer_orders \
                LEFT JOIN merchant ON mer_orders.mer_id = merchant.mer_id \
                WHERE mer_orders.user_id = %s ORDER BY create_time DESC"
        order_info = mysql.getAll(sql, param=[self.params['user_id']])
        if order_info:
            order_list = []
            for i in order_info:
                data = {}
                data['orders'] = i
                sql = "SELECT * FROM mer_ordergoods WHERE order_num = %s"
                order_goods = mysql.getAll(sql, param=[i.get('order_num')])
                data['order_goods'] = order_goods
                order_list.append(data)
            mysql.dispose()
            return HttpResponse(callJson(order_list))
        mysql.dispose()
        return HttpResponse(0)

# 商户版微信回调
class Mer_Wx_Callback(View):

    def __init__(self):
        self.Info = {}

    def post(self, request):
        xml_data = request.body
        if xml_data:
            xmls = str(request.body, encoding='utf-8')
            tree = fromstring(xmls)
            print("xmls:", xmls)
            appid = tree.find('appid').text  # appid
            self.Info['appid'] = appid
            return_code = tree.find('return_code').text  # 订单状态码
            self.Info['return_code'] = return_code
            total_fee = tree.find('total_fee').text  # 订单金额
            self.Info['total_fee'] = float(float(total_fee) * 0.01)
            orderNum = tree.find('out_trade_no').text  # 订单编号
            self.Info['orderNum'] = orderNum
            wxid = tree.find('transaction_id').text  # 微信支付订单号
            self.Info['wxid'] = wxid
            order_openid = tree.find('openid').text  # openid
            self.Info['openid'] = order_openid
            if return_code == 'SUCCESS':
                self.save_data()  # 更新订单信息
                success = '''
                        <xml>
                          <return_code><![CDATA[SUCCESS]]></return_code>
                          <return_msg><![CDATA[OK]]></return_msg>
                        </xml>
                        '''
                return HttpResponse(success)
        failed = '''<xml>
                        <return_code><![CDATA[FAIL]]></return_code>
                        <return_msg><![CDATA[404]]></return_msg>
                        </xml>'''
        return HttpResponse(failed)

    def save_data(self):
        try:
            mysql = Mysql()
            # 获取userid
            sql = "UPDATE mer_orders SET wxid = %s, state = '1', \
                wx_money = %s, pay_time = NOW() WHERE order_num = %s "
            state = mysql.update(sql, param=[
                self.Info['wxid'],
                self.Info['total_fee'],
                self.Info['orderNum']
            ])
            mysql.dispose()
        except Exception as e:
            erroLog(e)
            print(e)

# 商户版支付
class Mer_Pay(View):

    def post(self, request, **payload):
        self.params = {}
        self.params['user_id'] = payload.get('user_id')
        self.params['sales'] = float(request.POST.get('sales')) / 100
        self.params['sum_money'] = request.POST.get('sum_money')
        self.params['mer_id'] = request.POST.get('mer_id')
        self.params['order_num'] = Basedmethod.OrderNum()
        print(self.params)
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
        pay_time = 'NOW()' if state == 1 else 'NULL'
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
                balance=%s, hhcoin=%s, state=%s, pay_time=%s WHERE id=%s"
        mysql.update(sql, param=[
            self.params['sum_money'],
            real_balance,
            real_coin,
            state,
            pay_time,
            order_id
        ]) 
        mysql.dispose()
        data = callJson(data)
        return HttpResponse(data)

# 商户支付系统回调
class MerPay_CallBack(View):

    def __init__(self):
        self.Info = {}

    def post(self, request):
        xml_data = request.body
        if xml_data:
            xmls = str(request.body, encoding='utf-8')
            tree = fromstring(xmls)
            print("xmls:", xmls)  # appid
            self.Info['appid'] = tree.find('appid').text # 订单状态码
            self.Info['return_code'] = tree.find('return_code').text  # 订单金额
            self.Info['total_fee'] = tree.find('total_fee').text # 订单编号
            self.Info['orderNum'] = tree.find('out_trade_no').text # 微信支付订单号
            self.Info['wxid'] = tree.find('transaction_id').text
            order_openid = tree.find('openid').text  # openid
            self.Info['openid'] = order_openid
            if self.Info['return_code'] == 'SUCCESS':
                self.save_data()  # 更新订单信息
                # 成功信息
                success = '''
                        <xml>
                          <return_code><![CDATA[SUCCESS]]></return_code>
                          <return_msg><![CDATA[OK]]></return_msg>
                        </xml>
                        '''
                return HttpResponse(success)
        failed = '''<xml>
                        <return_code><![CDATA[FAIL]]></return_code>
                        <return_msg><![CDATA[404]]></return_msg>
                        </xml>'''
        return HttpResponse(failed)

    def save_data(self):
        try:
            mysql = Mysql()
            # 更新订单
            sql = "UPDATE mer_pay SET wxid = %s, wx_money = %s, \
                state = 1, pay_time=NOW() WHERE order_num = %s"
            state = mysql.update(sql, param=[
                self.Info['wxid'],
                self.Info['total_fee'],
                self.Info['orderNum']
            ])
            mysql.update(sql)
            mysql.dispose()
        except Exception as e:
            erroLog(e)
            print(e)
            
# 商户版支付订单
class MerPay_Order(View):

    def get(self, request, **payload):
        user_id = payload.get('user_id')
        row = request.GET.get('row')
        page = request.GET.get('page')
        mysql = Mysql()
        page, row = Pagings.mysqlPagings(page=page, row=row)
        sql = f"SELECT mp.order_num, mp.order_money, mp.wx_money, mp.balance, \
                mp.hhcoin, mp.state, mp.create_time, mr.mer_name FROM mer_pay \
                AS mp LEFT JOIN merchant AS mr ON mp.mer_id = mr.mer_id WHERE \
                mr.mer_id IS NOT NULL AND mp.user_id = {user_id} limit {page}, {row}"
        info = mysql.getAll(sql)
        if info:
            # 总页数
            sql = f"SELECT ceil(COUNT(mp.id) / 5) AS sum_page \
                FROM mer_pay AS mp WHERE mp.user_id = {user_id} "
            sum_page = mysql.getOne(sql)
            # 总金额
            sql = f"SELECT sum(wx_money+balance+0.1*hhcoin) AS sum_money \
                FROM mer_pay WHERE user_id = {user_id}"
            sum_money = mysql.getOne(sql)
            # 本月订单数
            sql = f"SELECT COUNT(*) AS month_orders FROM mer_pay \
                WHERE DATE_FORMAT( create_time, '%Y%m' ) = \
                DATE_FORMAT( CURDATE( ) , '%Y%m' ) AND user_id = {user_id}"
            month_orders = mysql.getOne(sql)
            # 总订单数
            sql = f"SELECT COUNT(id) AS sum_order FROM mer_pay WHERE user_id = {user_id}"
            sum_order = mysql.getOne(sql)
            # 本月金额
            sql = f"SELECT SUM(wx_money+balance) AS month_money \
                FROM mer_pay WHERE DATE_FORMAT( create_time, '%Y%m' ) \
                = DATE_FORMAT( CURDATE( ) , '%Y%m' ) AND user_id = {user_id}"
            month_money = mysql.getOne(sql)
            data = {}
            data['sum_page'] = sum_page.get('sum_page')
            data['sum_money'] = sum_money.get('sum_money')
            data['month_orders'] = month_orders.get('month_orders')
            data['sum_order'] = sum_order.get('sum_order')
            data['month_money'] = month_money.get('month_money')
            data['info'] = info
            mysql.dispose()
            return HttpResponse(callJson(data))
        mysql.dispose()
        return HttpResponse(0)

# 增加热度
class Add_Hot(View):

    def post(self, request, **payload):
        user_id = payload.get('user_id')
        hot_numbs = int(request.POST.get('hot_numbs'))
        mer_id = request.POST.get('mer_id')
        
        if hot_numbs > 5 or hot_numbs < 1:
            return HttpResponse(0)
            
        mysql = Mysql()
        sql = "SELECT id FROM mer_hots WHERE mer_id = %s AND user_id = %s"
        check = mysql.getOne(sql, param=[mer_id, user_id])
        if check:
            mysql.dispose()
            return HttpResponse(2)

        sql = "INSERT INTO mer_hots SET mer_id = %s, user_id = %s, hots = %s"
        ins_suc = mysql.insertOne(sql, param=[mer_id, user_id, hot_numbs])
        sql = "UPDATE merchant SET mer_hot = mer_hot + %s, \
            mer_hot_numbs = mer_hot_numbs + 1 WHERE mer_id = %s"
        up_suc = mysql.update(sql, param=[hot_numbs, mer_id])
        if up_suc and ins_suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

# 有关商家购物车
class Mer_Cart(View):

    def post(self, request, **payload):
        user_id = payload.get('user_id')
        cart_info = request.POST.get('cart_info')
        #[{stock_name, stock_id, numbs, detail, mer_id}]
        cache_name = str(user_id) + 'mercart'
        open_redis = Open_Redis().getConn(1)
        suc = open_redis.set(cache_name, cart_info, ex=9000)
        if suc:
            return HttpResponse(1)
        else:
            return HttpResponse(0)

    def get(self, request, **payload):
        user_id = payload.get('user_id')
        cache_name = str(user_id) + 'mercart'
        open_redis = Open_Redis().getConn(1)
        info = open_redis.get(cache_name)
        if info:
            return HttpResponse(info)
        open_redis.delete(cache_name)
        return HttpResponse(0)

#商户商城下单
class Mplace_Anorder(View):

    def post(self, request, **payload):
        self.params = {}
        self.params['user_id'] = payload.get('user_id')
        
        self.params['order_num'] = Basedmethod.OrderNum()
        self.params['mer_id'] = request.POST.get('mer_id')
        #self.params['address'] = request.POST.get('address')
        self.params['phone'] = request.POST.get('phone')
        self.params['name'] = request.POST.get('name')
        self.params['stock_list'] = json.loads(request.POST.get('stock_list'))
        #[{'stockid':1, 'product_img':sss,'stocknum':33}, {'stockid':1, 'stocknum':33}]
        print(self.params)
        cache_name = 'mer_order-' + self.params['order_num']
        mysql = Mysql()
        if not self.params['name']:
            return HttpResponse(3)
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
        data = callJson(data)
        return HttpResponse(data)
        
#查看三个热门店铺
class Sel_Hots_Merchant(View):

    def get(self, request, **payload):
        mysql = Mysql()
        info = mysql.getAll(sql="SELECT * FROM merchant ORDER BY mer_hot DESC LIMIT 3")
        mysql.dispose()
        return HttpResponse(callJson(info))

#随机换一批
class Sel_Rand_Merchant(View):

    def get(self, request, **payload):
        mysql = Mysql()
        info = mysql.getAll(sql="SELECT * FROM merchant ORDER BY RAND() LIMIT 3") 
        mysql.dispose()
        return HttpResponse(callJson(info))