import json
from django.http import request, HttpResponse, JsonResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Pagings, Type_Log
from xml.etree.ElementTree import fromstring
import random
import time
import datetime

#获取砍价商品列表
class Bargain_Product(View):

    def get(self, request):
        mysql = Mysql()
        user_id = request.GET.get('user_id')
        # sql = "SELECT \
        #             b.id AS bp_id, \
        #             b.lowest_price, \
        #             b.need_hhcoin, \
        #             b.category, \
        #             p.productName, \
        #             p.productImg, \
        #             cast(s.price * 100 AS SIGNED) AS price, \
        #             s.stock_detail, \
        #             CASE \
        #         WHEN bu.user_id IS NULL THEN \
        #             'NO' \
        #         ELSE \
        #             'YES' \
        #         END have_in_hand \
        #         FROM \
        #             bargain_product AS b \
        #         LEFT JOIN product AS p ON b.product_id = p.id \
        #         LEFT JOIN stock AS s ON b.stock_id = s.id \
        #         LEFT JOIN bargain_user bu ON b.id = bu.bp_id \
        #         AND bu.user_id = %s "
        sql = "SELECT \
                    b.id AS bp_id, \
                    b.lowest_price, \
                    b.need_hhcoin, \
                    b.category, \
                    p.productName, \
                    p.productImg, \
                    cast(s.price * 100 AS SIGNED) AS price, \
                    s.stock_detail, \
                    CASE \
                WHEN bu.state IN (1, 2) THEN \
                    'YES' \
                ELSE \
                    'NO' \
                END have_in_hand \
                FROM \
                    bargain_product AS b \
                LEFT JOIN product AS p ON b.product_id = p.id \
                LEFT JOIN stock AS s ON b.stock_id = s.id \
                LEFT JOIN ( \
                    SELECT \
                        * \
                    FROM \
                        ( \
                            SELECT \
                                * \
                            FROM \
                                bargain_user \
                            WHERE \
                                user_id = %s    \
                            ORDER BY \
                                id DESC \
                            LIMIT 10000 \
                        ) AS t \
                    GROUP BY \
                        t.user_id, \
                        t.bp_id \
                ) AS bu ON b.id = bu.bp_id \
                WHERE b.state = 1 \
                GROUP BY \
                    b.id \
                ORDER BY \
                    bu.id DESC" 
        data = mysql.getAll(sql, param=[user_id])
        mysql.dispose()
        if data:
            return HttpResponse(json.dumps(data, 
                                            ensure_ascii=False, 
                                            sort_keys=True, 
                                            indent=4, 
                                            cls=ComplexEncode))
        else:
            return HttpResponse(0)

#砍他(查看详情)~
class Bargain_Product_Detail(View):

    def get(self, request):
        bp_id = request.GET.get('bp_id')
        user_id = request.GET.get('user_id')
        bu_id = request.GET.get('bu_id', False)
        try:
            mysql = Mysql()
            sql = "SELECT \
                        bp.need_hhcoin, \
                        p.productName, \
                        cast(s.price * 100 as SIGNED) AS price, \
                        s.stock_detail, \
                        s.new_img \
                    FROM \
                        bargain_product AS bp \
                    LEFT JOIN product AS p ON bp.product_id = p.id \
                    LEFT JOIN stock AS s ON bp.stock_id = s.id \
                    WHERE bp.id = %s"
            suc = mysql.getOne(sql, param=[bp_id])
            if not suc:
                mysql.dispose()
                return HttpResponse('id不存在')
            sql = "SELECT b.*, u.wxname, u.user_img FROM bargain_user AS b \
                    LEFT JOIN userInfo AS u ON b.user_id = u.id \
                    WHERE b.user_id = %s AND b.bp_id = %s AND (state = 1 or state = 2)"
            check = mysql.getOne(sql, param=[user_id, bp_id])
            data = {}
            if check:
                sql = "SELECT \
                            b.*, u.wxname, \
                            u.user_img \
                        FROM \
                            bargain_log AS b \
                        LEFT JOIN userInfo AS u ON b.user_id = u.id \
                        WHERE \
                            b.bu_id = %s ORDER BY b.create_time DESC"
                bargain_log = mysql.getAll(sql, param=[check.get('id')])
                bargain_log = bargain_log if bargain_log else []
                data['product'] = suc
                data['nowcut_price'] = check.get('nowcut_price')
                data['present_price'] = check.get('present_price')
                data['user_img'] = check.get('user_img')
                data['user_name'] = check.get('wxname')
                data['bargain_log'] = bargain_log
                data['bu_id'] = check.get('id')
                data['msg'] = "正在砍价中" if int(check.get('state')) == 1 else "待支付中"
            else:
                data['product'] = suc
                data['nowcut_price'] = 0
                data['present_price'] = int(suc.get('price'))
                data['bargain_log'] = []
                data['msg'] = "未有砍价记录"
            mysql.dispose()
            return HttpResponse(json.dumps(data, 
                                            ensure_ascii=False, 
                                            sort_keys=True, 
                                            indent=4, 
                                            cls=ComplexEncode))
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#发起砍价
class Start_Bargain(View):

    def post(self, request):
        bp_id = request.POST.get('bp_id')
        user_id = request.POST.get('user_id')
        link = request.POST.get('link')
        try:
            mysql = Mysql()
            sql = "SELECT * FROM bargain_user WHERE user_id = %s \
                AND bp_id = %s AND (state = 1 OR state = 2) FOR UPDATE"
            check = mysql.getOne(sql, param=[user_id, bp_id])
            if check:
                msg = '该订单正在砍价中' if int(check.get('state')) == 1 else '有待支付订单'
                mysql.dispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : msg
                })
            sql = "SELECT bp.*, s.price FROM bargain_product AS bp \
                        LEFT JOIN stock AS s ON bp.stock_id = s.id WHERE bp.id = %s"
            bp_info = mysql.getOne(sql, param=[bp_id])
            sql = "INSERT INTO bargain_user SET user_id = %s, \
                            bp_id = %s, nowcut_price = 0, present_price = %s, \
                            bargain_link=%s, state = 1"
            bu_id = mysql.insertOne(sql, param=[user_id, 
                                                bp_id, 
                                                int(bp_info.get('price') * 100),
                                                link])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '发起砍价成功',
                'bu_id' : bu_id
            })
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#砍价            
class Bargain(View):

    def post(self, request):
        user_id = request.POST.get('user_id')
        bu_id = request.POST.get('bu_id')
        try:
            mysql = Mysql()
            sql = "SELECT * FROM bargain_user WHERE id = %s AND state = 1 FOR UPDATE"
            check = mysql.getOne(sql, param=[bu_id])
            # print('用户', user_id, datetime.datetime.now())
            # time.sleep(3)
            # print('用户', user_id, datetime.datetime.now())
            if not check:
                mysql.dispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '不存在该砍价'
                })
            if int(check.get('user_id')) == int(user_id):
                mysql.dispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '自己发起的砍价活动不能砍价'
                })
            # sql = "SELECT * FROM(SELECT COUNT(*) AS c FROM bargain_log \
            #     WHERE bu_id = %s AND user_id = %s) as bl WHERE c >= 3"
            sql = "SELECT * FROM bargain_log WHERE \
                    bu_id = %s AND user_id = %s"
            ck_bl = mysql.getOne(sql, param=[bu_id, user_id])
            if ck_bl:
                mysql.dispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '该商品个人砍价次数达到上限'
                })
            sql = "SELECT * FROM (SELECT \
                        COUNT(*) AS c  \
                    FROM \
                        bargain_log \
                    WHERE \
                        user_id = %s \
                    AND to_days(create_time) = to_days(now())) AS numbs WHERE c > 4"
            ck_bl = mysql.getOne(sql, param=[user_id])
            if ck_bl:
                mysql.dispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '一天最多砍五个商品'
                })
            #查询必要数据
            sql = "SELECT lowest_price, need_hhcoin, original_price FROM \
                    bargain_product WHERE id = %s"
            bp_info = mysql.getOne(sql, param=[check.get('bp_id')])
            #最低价钱
            lowest_price = int(bp_info.get('lowest_price'))
            #每刀所需盒盒币
            need_hhcoin = int(bp_info.get('need_hhcoin'))
            #查询盒盒币是否够
            sql = "SELECT hhcoin FROM userInfo WHERE id = %s FOR UPDATE"
            hhcoin = mysql.getOne(sql, param=[user_id])
            hhcoin = hhcoin.get('hhcoin')
            if hhcoin < need_hhcoin:
                mysql.errdispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '盒盒币不足'
                })
            #是否第一次砍价
            sql = "SELECT id FROM bargain_log WHERE bu_id = %s"
            first = mysql.getOne(sql=sql, param=[bu_id])
            print(190)
            print(first)
            is_first = False if first else True
            #原价
            original_price = int(bp_info.get('original_price'))
            #现价
            present_price = int(check.get('present_price'))
            #剩余可砍价
            print(present_price - lowest_price)
            #五毛直接砍掉
            if present_price - lowest_price < 50:
                cut_price = present_price - lowest_price
            #砍掉的价钱和增加的价钱
            else:
                cut_price = self.bargain(bg_price = 
                                                present_price - lowest_price,
                                                first=is_first)
            #加钱
            add_price = self.rand_pick()
            #砍掉后的价钱
            real_price = present_price - cut_price
            print('砍掉后的价钱')
            print(real_price)
            print('增加的价钱')
            print(add_price)
            #如果砍超
            # if lowest_price > real_price:
            #     print("砍过头了", cut_price)
            #     cut_price = present_price - lowest_price
            #     real_price = lowest_price
            #     mysql.errdispose()
            #     return HttpResponse("砍过头了")
            #砍价日志
            sql = "INSERT INTO bargain_log SET bu_id = %s, user_id = %s, \
                bargain_money = %s , obtain_money = %s, consume_hhcoin = %s, \
                current_price = %s"
            mysql.insertOne(sql, param=[
                bu_id,
                user_id,
                cut_price,
                add_price,
                need_hhcoin,
                real_price
            ])
            sql = "UPDATE bargain_user SET  nowcut_price = nowcut_price + %s, \
                    present_price = %s WHERE id = %s"
            mysql.update(sql, param=[
                cut_price,
                real_price,
                bu_id
            ])
            #日志
            #增加余额
            up_sql, log_sql = Type_Log.balance_log( user_id=user_id, 
                                                    handle=4, 
                                                    money=add_price * 0.01, 
                                                    asd=1)
            mysql.update(up_sql)
            mysql.insertOne(log_sql)
            #减少盒盒币
            up_sql, log_sql = Type_Log.coin_handle( user_id=user_id, 
                                                    handle=11, 
                                                    num=need_hhcoin,
                                                    asd=0)
            mysql.update(up_sql)
            mysql.insertOne(log_sql)
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : "砍价成功",
                'add_price' : add_price,
                'cut_price' : cut_price,
                'now_price' : real_price,
                'nowcut_price' : original_price - real_price
            })
        except Exception as e:
            print(e)
            mysql.errdispose()
            return JsonResponse({
                    'ret' : -2,
                    'msg' : '网络繁忙'
                })

    #砍价 
    def bargain(self, bg_price, first=False):
        #bg_price(最低和原价差价)
        #第一次砍价
        #[0.5, 500]
        if first:
            discount = round(random.uniform(0.2, 0.5), 2)
            bg_price = int(bg_price * discount)
        else:
            discount = round(random.uniform(0.06, 0.1), 2)
            bg_price = int(bg_price * discount)
        print('这刀砍了')
        print(bg_price)
        return bg_price

    #增加的余额
    def rand_pick(self):
        # value_list = [1, 880, 160, 180, 260, 280, 360, 380, 460, 480, 580]
        # probabilities = [0.1, 0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05]
        value_list = [10, 50, 60, 80]
        probabilities = [0.3, 0.5, 0.1, 0.1]
        x = random.uniform(0, 1)
        cumprob = 0.0
        for item, item_pro in zip(value_list , probabilities):
            print(item)
            print(item_pro)
            cumprob += item_pro
            if x < cumprob:
                break
        return item

#下单
class Place_Anorder(View):

    def __init__(self):
        self.info = {}

    def post(self, request):
        self.info['user_id'] = request.POST.get('user_id')
        self.info['bu_id'] = request.POST.get('bu_id', '')
        self.info['address'] = request.POST.get('address')  #收货地址
        self.info['phone'] = request.POST.get('phone')  #手机号码
        self.info['Consignee'] = request.POST.get('consignee')  #收货人
        self.info['order_num'] = self.info['bu_id'] + 'kanjia' + Basedmethod.OrderNum()
        self.info['remark'] = '砍价下单'    #备注
        print(self.info)
        return JsonResponse({
                'ret' : -2,
                'msg' : '下单失败'
            })
        try:
            mysql = Mysql()
            sql = "SELECT * FROM bargain_user WHERE id = %s AND state = 1 FOR UPDATE"
            bu_info = mysql.getOne(sql, param=[self.info['bu_id']])
            if not bu_info:
                mysql.dispose()
                return JsonResponse({
                    'ret' : -3,
                    'msg' : '订单号异常 请重新发起砍价'
                })
            if int(bu_info.get('user_id')) != int(self.info['user_id']):
                mysql.dispose()
                return HttpResponse('用户id出现错误')
            sql = "SELECT * FROM bargain_product WHERE id = %s "
            bp_info = mysql.getOne(sql, param=[bu_info.get('bp_id')])
            sql = "SELECT * FROM stock WHERE id = %s"
            stock_info = mysql.getOne(sql, param=[bp_info.get('stock_id')])
            #下单
            sql = "INSERT INTO orders SET orderNum=%s, orderMoney=%s, wxMoney=%s, \
                    createUser=%s, address=%s, Consignee=%s, \
                    mobile=%s, remark=%s, state=0"
            order_id = mysql.insertOne(sql, param=[
                                            self.info['order_num'],
                                            bu_info.get('present_price') * 0.01,
                                            bu_info.get('present_price') * 0.01,
                                            self.info['user_id'],
                                            self.info['address'],
                                            self.info['Consignee'],
                                            self.info['phone'],
                                            self.info['remark']
            ])
            sql = "INSERT INTO ordergoods SET \
                                            order_id=%s, \
                                            stock_id=%s, \
                                            num=1, \
                                            money=%s,\
                                            stock_hhcoin=%s, \
                                            stock_img=%s, \
                                            product_id=%s, \
                                            stock_detail=%s, \
                                            stock_name=%s "
            og_id = mysql.insertOne(sql, param=[
                                            self.info['order_num'],
                                            stock_info.get('id'),
                                            stock_info.get('price'),
                                            stock_info.get('hehecoin'),
                                            stock_info.get('img'),
                                            stock_info.get('product_id'),
                                            stock_info.get('stock_detail'),
                                            stock_info.get('stock_name')
            ])
            sql = "UPDATE bargain_user SET state = 2, order_num = %s WHERE id = %s"
            mysql.update(sql, param=[self.info['order_num'],
                                    self.info['bu_id']])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'wxmoney': bu_info.get('present_price') * 0.01,
                'msg': '下单成功 订单状态已改变 请付款',
                'order_num' : self.info['order_num']
            })
        except Exception as e:
            print(e)
            mysql.errdispose()
            return JsonResponse({
                'ret' : -2,
                'msg' : '下单失败'
            })

#微信回调
class Wx_CallBack(View):

    def __init__(self):
        self.Info = {}

    def post(self, request):
        xml_data = request.body
        if xml_data:
            xmls = str(request.body, encoding='utf-8')
            tree = fromstring(xmls)
            print("xmls:", xmls) 
            self.Info['appid'] = tree.find('appid').text   # appid
            self.Info['return_code'] = tree.find('return_code').text # 订单状态码
            self.Info['total_fee'] = float(float(tree.find('total_fee').text) * 0.01)  # 订单金额
            self.Info['orderNum'] = tree.find('out_trade_no').text  # 订单编号
            self.Info['wxid'] =tree.find('transaction_id').text   # 微信支付订单号
            self.Info['openid'] = tree.find('openid').text  # openid
            # 成功信息
            if self.Info['return_code'] == 'SUCCESS':
                self.save_data()  # 更新订单信息
                if self.Info.get('appid') != 'wx940c713eac9f7aca':
                    print('**********************小程序appid不匹配**********************************')
                if not self.Info.get('orderNum'):
                    print('**********************小程序out_trade_no不匹配***************************')
                success = '''
                        <xml>
                          <return_code><![CDATA[SUCCESS]]></return_code>
                          <return_msg><![CDATA[OK]]></return_msg>
                        </xml>
                        '''
                return HttpResponse(success)
        #错误信息
        failed = '''<xml>
                    <return_code><![CDATA[FAIL]]></return_code>
                    <return_msg><![CDATA[404]]></return_msg>
                    </xml>'''
        return HttpResponse(failed)

    def save_data(self):
        mysql = Mysql()
        try:
            order_num = self.Info['orderNum']
            wxid = self.Info['wxid']
            sql = f'''update orders set state = 1, wxid="{wxid}, payTime = NOW()" \
                where orderNum="{order_num}"'''
            mysql.update(sql)
            bu_id = order_num[0 : order_num.find('kanjia')]
            print(bu_id)
            sql = f"UPDATE bargain_user SET state = 0 WHERE id = {bu_id}"
            mysql.update(sql)
            mysql.dispose()
        except Exception as e:
            print(e)
            mysql.errdispose()

#查看订单
class Sel_BgOrder(View):

    def get(self, request):
        user_id = request.GET.get('user_id')
        mysql = Mysql()
        sql = f"SELECT \
                    o.orderNum, \
                    o.state, \
                    o.orderMoney, \
                    o.createTime, \
                    og.stock_name, \
                    og.stock_detail \
                FROM \
                    orders AS o \
                LEFT JOIN ordergoods AS og \
                ON o.orderNum = og.order_id \
                WHERE \
                    createUser = '{user_id}' \
                AND orderNum LIKE '%kanjia%'"
        data = mysql.getAll(sql)
        mysql.dispose()
        if data:
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(data)
        else:
            return HttpResponse(0)

#取消订单继续砍价 
class Close_Bargain(View): 

    def post(self, request):
        try:
            bu_id = request.POST.get('bu_id')
            mysql = Mysql()
            sql = "SELECT * FROM bargain_user WHERE id = %s AND order_num IS NOT NULL"
            bu_info = mysql.getOne(sql, param=[bu_id])
            if bu_info:
                order_num = bu_info.get('order_num')
                sql = "SELECT * FROM orders WHERE orderNum = %s AND state = 0"
                order_info = mysql.getOne(sql, param=[order_num])
                if order_info:
                    sql = "DELETE FROM orders WHERE orderNum = %s"
                    mysql.delete(sql, param=[order_num])
                    sql = "UPDATE bargain_user SET state = 1, order_num = NULL WHERE id = %s"
                    mysql.update(sql, param=[bu_id])
                    mysql.dispose()
                    return HttpResponse(1)
        except Exception as e:
            print(e)
            return HttpResponse(0)
