import json
from django.http import request, HttpResponse, JsonResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Pagings, Type_Log
from xml.etree.ElementTree import fromstring
import random
import datetime

#我的小树苗
class My_Sapling(View):

    def get(self, request):
        user_id = request.GET.get('user_id')
        mysql = Mysql()
        sql = "SELECT lottery_code, is_get FROM \
            oneyuanpurchase WHERE state = 1 AND user_id = %s"
        info = mysql.getAll(sql, param=[
            user_id
        ])
        mysql.dispose()
        info = info if info else []
        return HttpResponse(json.dumps(info, ensure_ascii=False, 
                                                sort_keys=True, 
                                                indent=4, 
                                                cls=ComplexEncode))

#下单
class OneYuanPurchase(View):

    def __init__(self, **kwargs):
        self.info = {}

    def post(self, request):
        try:
            return JsonResponse({
                'ret' : -2,
                'msg' : '下单失败'
            })
            self.info['user_id'] = request.POST.get('user_id')
            self.info['user_name'] = request.POST.get('user_name')
            self.info['address'] = request.POST.get('address')
            self.info['mobile'] = request.POST.get('mobile', False)
            self.info['order_num'] = Basedmethod.OrderNum()
            if not self.info['mobile']:
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '没有手机号码'
                })
            mysql = Mysql()
            sql = "INSERT INTO oneyuanpurchase SET order_num = %s, user_name = %s,\
                user_id = %s, address = %s, mobile = %s, state = 0, is_get=0"
            mysql.insertOne(sql, param=[
                self.info['order_num'],
                self.info['user_name'],
                self.info['user_id'],
                self.info['address'],
                self.info['mobile']
            ])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '下单成功 请付款',
                'wx_money' : 100,
                'order_num' : self.info['order_num']
            })
        except Exception as e:
            print(e)
            mysql.errdispose()
            return JsonResponse({
                'ret' : -2,
                'msg' : '下单失败'
            })

#回调
class OneYuanPurchase_CallBack(View):

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
            self.Info['total_fee'] = tree.find('total_fee').text  # 订单金额
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
        try:
            mysql = Mysql()
            lottery_code = self.ran(6)
            sql = "UPDATE oneyuanpurchase SET lottery_code = %s, state = 1, \
                is_get=0, wxid = %s, wx_money = %s WHERE order_num = %s"
            mysql.update(sql, param=[
                lottery_code,
                self.Info['wxid'],
                self.Info['total_fee'],
                self.Info['orderNum']
            ])
            sql = "SELECT user_id FROM oneyuanpurchase  WHERE order_num = %s"
            user = mysql.getOne(sql, param=[self.Info['orderNum']])
            up_sql, log_sql = Type_Log.coin_handle(user_id=user.get('user_id'), 
                                                    handle=12, 
                                                    num=10, 
                                                    asd=1)
            mysql.update(up_sql)
            mysql.insertOne(log_sql)
            mysql.dispose()
        except Exception as e:
            print(e)
            mysql.errdispose()

    def ran(self, n):
        ret = ""
        chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', \
                'C', 'D', 'E', 'F', 'G', 'H', 'I','J', 'K', 'L', 'M', 'N', 'O', \
                'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        win_list = [
            '7EDSYQ',
            'UMYLRL',
            '5WRS7Y',
            'DHM7FN',
            'Q4GAWY',
            'U58LXJ',
            'KNGJC8',
            'WTCXQD',
            'LV8NX5',
            '7NCWTK'
        ]
        for i in range(n):
            ret += chars[random.randint(0,34)]
        if ret in win_list:
            self.ran(n)
        else:
            return ret

#查看本期中奖名单
class Winning_list(View):

    def get(self, request):
        mysql = Mysql()
        #now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        sql = "SELECT id, winning_numbers, state FROM winning_list WHERE \
                create_time <= NOW() ORDER BY create_time"
        # sql = f"SELECT id, winning_numbers, state FROM winning_list WHERE \
        #     create_time BETWEEN '2019-11-01 20:00:00' AND '{now_time}'"
        info = mysql.getAll(sql)
        info = info if info else []
        mysql.dispose()
        return HttpResponse(json.dumps(info, ensure_ascii=False, 
                                                sort_keys=True, 
                                                indent=4, 
                                                cls=ComplexEncode))

#
class Test(View):

    def get(self, request):
        
        try:
            mysql = Mysql()
            sql = "SELECT COUNT(*) AS bl FROM bargain_log"
            bl = mysql.getOne(sql)
            sql = "SELECT COUNT(*) AS goumai FROM bargain_user WHERE state = 0"
            goumai = mysql.getOne(sql)
            sql = "SELECT COUNT(*) AS bu FROM bargain_user "
            bu = mysql.getOne(sql)
            sql = "SELECT COUNT(*) AS oneyuan FROM oneyuanpurchase"
            oneyuan = mysql.getOne(sql)
            data = {}
            for i in range(1,6):
                sql = f"SELECT \
                            t.id, \
                            group_concat(DISTINCT(de.mchid)) '常用投递机器', \
                            t.sOpenid '微信openid', \
                            t.sNickName '微信昵称', \
                            t.dtLottTime, \
                            iCount '集赞人数', \
                            iSource '领奖码' \
                        FROM \
                            ( \
                                SELECT \
                                    j.id, \
                                    j.sOpenid, \
                                    j.dtLottTime, \
                                    url_decode (j.sNickName) sNickName, \
                                    count(d.sOpenid) iCount, \
                                    CASE j.iSource \
                                WHEN 1 THEN \
                                    concat('00', j.iSource, '-松江') \
                                WHEN 2 THEN \
                                    concat('00', j.iSource, '-闵行') \
                                WHEN 3 THEN \
                                    concat('00', j.iSource, '-奉贤') \
                                WHEN 4 THEN \
                                    concat('00', j.iSource, '-临港') \
                                WHEN 5 THEN \
                                    concat('00', j.iSource, '-虹口') \
                                ELSE \
                                    j.iSource \
                                END iSource \
                                FROM \
                                    tbActDianzan d \
                                LEFT JOIN tbActJizan j ON j.sOpenid = d.sJizanOpenid \
                                WHERE j.iSource =  {i} \
                                GROUP BY \
                                    d.sJizanOpenid \
                            ) t \
                        LEFT JOIN deliver de ON t.sOpenid = de.openid \
                        WHERE \
                            t.iCount >= 30  \
                        GROUP BY \
                            t.sOpenid \
                        ORDER BY  \
                            t.iCount DESC "
                info = mysql.getAll(sql)
                if i == 1:
                    data['松江'] = len(info)
                if i == 2:
                    data['闵行'] = len(info)
                if i == 3:
                    data['奉贤'] = len(info)
                if i == 4:
                    data['临港'] = len(info)
                if i == 5:
                    data['虹口'] = len(info)
            print(data)
            mysql.dispose()
            return HttpResponse(f"一元购{oneyuan.get('oneyuan')}人购买, \
                \r发起了{bu.get('bu')}条砍价, \
                \r{bl.get('bl')}条砍价记录, \
                \r实际完成砍价支付 {goumai.get('goumai')} 人 \
                \r松江集赞满30的人数 {data.get('松江')}, \
                \r闵行集赞满30的人数 {data.get('闵行')}, \
                \r奉贤集赞满30的人数 {data.get('奉贤')}, \
                \r临港集赞满30的人数 {data.get('临港')}, \
                \r虹口集赞满30的人数 {data.get('虹口')} ")
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)
        
#一口气买三个 一元购
class ThreeOneYuan(View):

    def __init__(self, **kwargs):
        self.info = {}

    def post(self, request):
        try:
            return JsonResponse({
                'ret' : -2,
                'msg' : '下单失败'
            })
            self.info['user_id'] = request.POST.get('user_id')
            self.info['user_name'] = request.POST.get('user_name')
            self.info['address'] = request.POST.get('address')
            self.info['mobile'] = request.POST.get('mobile', False)
            self.info['order_num'] = Basedmethod.OrderNum()
            if not self.info['mobile']:
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '没有手机号码'
                })
            mysql = Mysql()
            for i in range(3):
                sql = "INSERT INTO oneyuanpurchase SET order_num = %s, user_name = %s,\
                    user_id = %s, address = %s, mobile = %s, state = 0, is_get=0"
                mysql.insertOne(sql, param=[
                    self.info['order_num'],
                    self.info['user_name'],
                    self.info['user_id'],
                    self.info['address'],
                    self.info['mobile']
                ])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '下单成功 请付款',
                'wx_money' : 300,
                'order_num' : self.info['order_num']
            })
        except Exception as e:
            print(e)
            mysql.errdispose()
            return JsonResponse({
                'ret' : -2,
                'msg' : '下单失败'
            })


class ThreeOneYuan_CallBack(View):

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
            self.Info['total_fee'] = tree.find('total_fee').text  # 订单金额
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
        try:
            mysql = Mysql()
            for i in range(3):
                lottery_code = self.ran(6)
                sql = "SELECT * from oneyuanpurchase WHERE order_num = %s AND lottery_code IS NULL limit 1"
                order_id = mysql.getOne(sql, param=[self.Info['orderNum']])
                sql = "UPDATE oneyuanpurchase SET lottery_code = %s, state = 1, \
                    is_get=0, wxid = %s, wx_money = %s WHERE id = %s"
                mysql.update(sql, param=[
                    lottery_code,
                    self.Info['wxid'],
                    self.Info['total_fee'],
                    order_id.get('id')
                ])
                sql = "SELECT user_id FROM oneyuanpurchase  WHERE order_num = %s"
                user = mysql.getOne(sql, param=[self.Info['orderNum']])
                up_sql, log_sql = Type_Log.coin_handle(user_id=user.get('user_id'), 
                                                        handle=12, 
                                                        num=10, 
                                                        asd=1)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
            mysql.dispose()
        except Exception as e:
            print(e)
            mysql.errdispose()

    def ran(self, n):
        ret = ""
        chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', \
                'C', 'D', 'E', 'F', 'G', 'H', 'I','J', 'K', 'L', 'M', 'N', 'O', \
                'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        win_list = [
            '7EDSYQ',
            'UMYLRL',
            '5WRS7Y',
            'DHM7FN',
            'Q4GAWY',
            'U58LXJ',
            'KNGJC8',
            'WTCXQD',
            'LV8NX5',
            '7NCWTK'
        ]
        for i in range(n):
            ret += chars[random.randint(0,34)]
        if ret in win_list:
            self.ran(n)
        else:
            return ret