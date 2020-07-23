import json

from django.views import View
from django.core.cache import cache
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.Predis import Open_Redis
from base.limits import hold_yukou, hold_shikou, hold_huigun
from base.shop_base import Pagings, callJson, Type_Log, getOrderNum, returnJson, query


class Orders(View):

    def __init__(self):
        self.info = {}
        # if 有参数 assert 判断参数值

    def post(self, request, **payload):

        handle = payload.get('handle')
        self.info['order_num'] = request.POST.get('order_num')
        self.info['row'] = request.POST.get('row')
        self.info['page'] = request.POST.get('page')
        self.info['order_type'] = request.POST.get('order_type')

        self.info['as_type'] = request.POST.get('as_type')  # 退货0，换货1
        self.info['order_state'] = request.POST.get('order_state') #订单状态
        self.info['why'] = request.POST.get('why')  #补充说明

        #下单
        self.info['user_id'] = payload.get('user_id')  #用户id
        self.info['sendTime'] = request.POST.get('send_time')    #送货时间
        self.info['address'] = request.POST.get('address')  #收货地址
        self.info['phone'] = request.POST.get('phone')  #手机号码
        self.info['remark'] = request.POST.get('remark')    #备注
        self.info['Consignee'] = request.POST.get('consignee')  #收货人
        self.info['order_num'] = getOrderNum('ShopOrder')  #订单编号
        self.info['freight'] = request.POST.get('freight') #运费状态，为0则运费为3，否则运费为0
        self.info['stock_list'] = request.POST.get('stock_list')
        #库存列表 传列表套对象[{stock_id:1,num:1, store_id:1},{stock_id:1,num:1, store_id:1}]
        
        cache_name = 'order-' + self.info['order_num']

        if handle == 'confirm':
            mysql = Mysql()
            sql = 'UPDATE orders SET state = %s WHERE orderNum = %s'
            mysql.update(sql, param=[4, self.info['order_num']])
            mysql.dispose()
            return HttpResponse(returnJson(0, '确认成功'))

        if handle == 'allOrders':
            page, row = Pagings.mysqlPagings(self.info['page'], self.info['row'])
            sql = "SELECT orderNum, balance, wxMoney, state \
                FROM orders WHERE createUser = %s \
                ORDER BY createTime DESC limit %s, %s"
            info = query(sql, param=[self.info['user_id'], page, row])
            data = self.orderDeatil(info)
            return HttpResponse(returnJson(0, '查询成功', data))
        
        if handle == 'typeOrder':
            page, row = Pagings.mysqlPagings(self.info['page'], self.info['row'])
            sql = "SELECT orderNum, orderMoney, heheCoin, \
                wxMoney, balance, state FROM orders \
                WHERE createUser = %s AND state = %s \
                ORDER BY createTime DESC limit %s, %s"
            info = query(sql, param=[self.info['user_id'], self.info['order_type'], page, row])
            data = self.orderDeatil(info)
            return HttpResponse(returnJson(0, '查询成功', data))

        if handle == 'cancel':
            return self.cancel()

        if handle == 'placeOrder':
            self.info['stock_list'] = json.loads(request.POST.get('stock_list')) 
            return self.placeOrder()

        if handle == 'cancelAsOrder':
            mysql = Mysql()
            sql = "SELECT order_state FROM as_orders WHERE order_id = %s"
            state = mysql.getOne(sql, param=[self.info['order_num']])
            sql = "UPDATE orders SET state = %s WHERE orderNum = %s"
            mysql.update(sql, param=[state.get('order_state'), self.info['order_num']])
            sql = "DELETE FROM as_orders WHERE order_id = %s"
            mysql.delete(sql, param=[self.info['order_num']])
            mysql.dispose()
            return HttpResponse(returnJson(0, '取消售后订单成功'))

        if handle == 'selAsOrder':
            sql = "SELECT * FROM as_orders WHERE order_id=%s"
            info = query(sql, param=[self.info['order_num']])
            return HttpResponse(returnJson(0, '查询成功', info))

        if handle == 'upAsOrder':
            mysql = Mysql()
            sql = 'UPDATE orders SET state="3" WHERE orderNum = %s'
            mysql.update(sql, param=[self.info['order_num']])
            sql = "insert into as_orders SET order_id=%s, type=%s, \
                why=%s, isCheck=0, create_time=NOW(), order_state=%s"
            mysql.insertOne(sql, param=[
                self.info['order_num'], 
                self.info['as_type'], 
                self.info['way'], 
                self.info['order_state']])
            mysql.dispose()
            return HttpResponse(returnJson(0, '提交售后成功'))

        return HttpResponse(returnJson(-2, '非法路径'))

    def placeOrder(self):
        cache_name = getOrderNum('ShopOrder')
            #----------------------2019-09-16限量----------------------
        mysql = Mysql()
        holds = []
        for i in self.info['stock_list']:
            stock_num = int(i.get('num'))
            if not isinstance(stock_num, int) or stock_num <= 0:
                mysql.dispose()
                return HttpResponse(returnJson(-2, '商品数量出现错误'))
            sql = "SELECT product_id, stock_name FROM stock WHERE id = %s"
            stock_info = mysql.getOne(sql, param=[i.get('stock_id')])
            sql = "SELECT user_goods_limit FROM product WHERE id = %s"
            limit_numb = mysql.getOne(sql, param=[stock_info.get('product_id')])
            if limit_numb.get('user_goods_limit') != 0:
                limit_data = {}
                limit_data['key'] = 'product_1909_' + str(stock_info.get('product_id'))
                limit_data['use'] = stock_num
                limit_data['total'] = limit_numb.get('user_goods_limit')
                limit_data['ext'] = stock_info.get('stock_name')
                holds.append(limit_data)
        if holds:
            check_limit = hold_yukou(holds=holds, 
                                    mysql=mysql, 
                                    user_id=self.info['user_id'], 
                                    source='商城购买')
            if check_limit['ret'] == -2:
                return JsonResponse(check_limit)

        #----------------------插入到订单表----------------------
        print('插入订单表')
        mysql = Mysql()
        sql = "INSERT INTO orders SET orderNum=%s, store_id=%s, \
                createUser=%s, address=%s,Consignee=%s, mobile=%s, \
                sendTime=%s, remark=%s, state=0, freight=%s"
        order_id = mysql.insertOne(sql, param=[
            self.info['order_num'],
            self.info['stock_list'][0].get('store_id'),
            self.info['user_id'],
            self.info['address'],
            self.info['Consignee'],
            self.info['phone'],
            self.info['sendTime'],
            self.info['remark'],
            int(self.info['freight'])
        ])
        price = 0
        hhcoin = 0
        #插入到订单商品表
        for i in self.info['stock_list']:
            stock_num = int(i.get('num'))
            sql = "SELECT stock_name, img, price, hehecoin, store_id,\
                stock_detail, product_id FROM stock WHERE id = %s"
            stock_info = mysql.getOne(sql, param=[i.get('stock_id')])

            price += int(stock_info.get('price')) * stock_num
            hhcoin += int(stock_info.get('hehecoin')) * stock_num

            sql = "INSERT INTO ordergoods SET order_id=%s, \
                stock_id=%s, num=%s, money=%s, stock_hhcoin=%s, \
                stock_img=%s, product_id=%s, stock_detail=%s, \
                stock_name=%s, store_id=%s"
            mysql.insertOne(sql, param=[
                self.info['order_num'],
                i.get('stock_id'),
                stock_num,
                stock_info.get('price'),
                stock_info.get('hehecoin'),
                stock_info.get('img'),
                stock_info.get('product_id'),
                stock_info.get('stock_detail'),
                stock_info.get('stock_name'),
                stock_info.get('store_id')
            ])
        # ----------------------余额支付----------------------
        user_info = mysql.getOne("SELECT money, hhcoin \
            FROM userInfo WHERE id = %s", param=[self.info['user_id']])
        user_price = int(user_info.get('money'))
        user_hhcoin = int(user_info.get('hhcoin'))
        #初始化参数
        real_coin = 0   #实际要扣除的盒盒币
        real_balance = 0    #实际要支付的盒盒余额
        real_wxprice = 0    #额外需要微信支付价格
        #抵扣盒盒币
        real_coin = hhcoin if user_hhcoin >= hhcoin else user_hhcoin
        if real_coin > 0:
            # 扣盒盒币
            up_sql, log_sql = Type_Log.coin_handle(user_id=self.info['user_id'], 
                                                    handle=1, num=real_coin, asd=0)
            mysql.update(up_sql)
            mysql.update(log_sql)
        real_wxprice = price - real_coin
        #抵扣余额
        real_balance = real_wxprice if user_price >= real_wxprice else user_price

        if real_balance > 0:
            #扣余额
            up_sql, log_sql = Type_Log.balance_log(user_id=self.info['user_id'],
                                                    handle=1, money=real_balance, asd=0, 
                                                    order_num=self.info['order_num'])
            mysql.update(up_sql)
            mysql.update(log_sql)
        mysql.dispose()
        #(实际需要支付的微信价钱)
        real_wxprice = real_wxprice - real_balance
        #微信支付尾款（是否需要微信支付）
        data = {}
        data['order_num'] = self.info['order_num']
        data['balance'] = real_balance
        data['hhcoin'] = real_coin
        state = 1 if real_wxprice == 0 else 0 #订单状态 0未付款 1代发货
        if state == 1:
            #微信不需要再付钱
            data['msg'] = 'OK'
            #实扣限量
            if holds:
                shikou_data = hold_shikou(holds=holds, user_id=self.info['user_id'])
                if shikou_data['ret'] == -2:
                    return JsonResponse(shikou_data)
        else:
            #需要微信支付尾款
            data['msg'] = 'FAIL'
            data['res_price'] = real_wxprice
            data['erro_info'] = '已扣除盒盒币，请微信支付尾款！'
            #挂起待支付订单
            open_redis = Open_Redis().getConn(2)
            cache = json.dumps(callJson(data))
            open_redis.set(cache_name, cache, ex=900)

        mysql = Mysql()
        sql = "UPDATE orders SET orderMoney=%s, wxMoney=%s, \
                balance=%s, heheCoin=%s, state=%s WHERE id=%s"
        mysql.update(sql, param=[price, real_wxprice, real_balance, 
            real_coin, state, order_id])
        mysql.dispose()
        return HttpResponse(callJson(data))

    def cancel(self):
        data = {}
        mysql = Mysql()
        sql = "SELECT o.createUser, o.state, o.wxMoney, o.balance, \
                o.heheCoin,p.id product_id,p.user_goods_limit FROM orders o \
                LEFT JOIN ordergoods og on o.orderNum=og.order_id \
                LEFT JOIN product p on og.product_id=p.id \
                WHERE orderNum =%s AND (o.state = 1 OR o.state = 0)"
        info = mysql.getAll(sql, param=[self.info['order_num']])
        if not info:
            return HttpResponse(returnJson(-2, '订单号不存在'))

        sum_balance = int(info[0].get('balance'))
        sum_hhcoin = int(info[0].get('heheCoin'))
        #已付款限量不回滚
        state = '未定义'
        if int(info[0].get('state')) == 1:
            state = '已付款订单'
            sum_balance += int(info[0].get('wxMoney'))
        #待支付限量回滚
        holds=[]
        if int(info[0].get('state')) == 0:
            state = '未付款订单'
            for limit_numb in info:
                if limit_numb.get('user_goods_limit') != 0:
                    limit_data = {}
                    limit_data['key'] = 'product_1909_' + str(limit_numb.get('product_id'))
                    holds.append(limit_data)
        if holds:
            #此处关闭了数据库连接
            check_limit = hold_huigun(holds=holds, 
                                    mysql=mysql, 
                                    user_id=info[0].get('createUser')
                                    )
            if check_limit['ret'] == -2:
                return JsonResponse(check_limit)

        mysql = Mysql()
        if sum_balance != 0:
            #退余额
            up_sql, log_sql = Type_Log.balance_log(
                user_id=info[0].get('createUser'), 
                handle=3, 
                money=sum_balance, 
                asd=1, 
                order_num=self.info['order_num']
                )
            mysql.update(up_sql)
            mysql.insertOne(log_sql)
        if sum_hhcoin != 0:
            #退盒盒币
            up_sql, log_sql = Type_Log.coin_handle(
                user_id=info[0].get('createUser'), 
                handle=9, 
                num=sum_hhcoin, 
                asd=1)
            mysql.update(up_sql)
            mysql.getOne(log_sql)
        #改状态
        sql = "UPDATE orders SET state = '5' WHERE orderNum = %s"
        check = mysql.update(sql, param=[self.info['order_num']])
        if check:
            mysql.dispose()
            return HttpResponse(returnJson(0, f'{state}取消订单成功'))
        mysql.errdispose()
        return HttpResponse(returnJson(-2, f'{state}取消订单失败'))

    def orderDeatil(self, orders):
        mysql = Mysql()
        if orders:
            data_list = []
            for i in orders:
                sql = "SELECT stock.id as stock_id, stock.stock_name, \
                    stock.img, stock.hehecoin, stock.price, ordergoods.num, \
                    stock.stock_detail, ordergoods.product_id \
                    FROM ordergoods LEFT JOIN stock \
                    ON ordergoods.stock_id = stock.id \
                    WHERE ordergoods.order_id=%s"
                stock_info = mysql.getAll(sql, param=[i.get('orderNum')])
                data = {}
                data['orderinfo'] = i
                data['shopinfo'] = stock_info
                data_list.append(data)
            mysql.dispose()
            return data_list
        mysql.dispose()
        return orders
    