import requests
import random
import string
import xmltodict
import json
from hashlib import md5

from django.views import View
from django.utils.decorators import method_decorator
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.shop_base import Type_Log, getOrderNum, getSign, getNonceStr, callJson, query, returnJson


class BalanceToWx(View):

    def __init__(self):
        self.info = {}
    
    def post(self, request, **payload):
        try:
            self.info['user_id'] = payload.get('user_id')
            self.info['openid'] = payload.get('openid')  # 用户openid 

            self.info['spbill_create_ip'] = '132.232.119.99'  # 终端IP 1
            self.info['amount'] = int(request.POST.get('amount')) #金额单位分

            self.info['mch_appid'] = 'wx940c713eac9f7aca'  # 商户账号appid
            self.info['mchid'] = '1531704091'  # 商户号
            self.info['desc'] = '用户提现' #企业付款备注
            self.info['check_name'] = "NO_CHECK" #校验用户姓名选项 NO_CHECK：不校验真实姓名 FORCE_CHECK：强校验真实姓名

            self.info['partner_trade_no'] = getOrderNum('ToWx') #商户订单号      
            self.info['nonce_str'] = getNonceStr() #随机字符串
            self.sigin = getSign(ks=self.info)

            if self.info['amount'] < 2000:
                return JsonResponse({
                    'ret' : -2,
                    'msg' : "提现金额过低 要求大于20"
                })

            mysql = Mysql()
            userinfo = self.check_userinfo(mysql=mysql)
            if userinfo.get('money') < 20:
                mysql.dispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : "余额不足, 小于20"
                })

            check = self.check_cashout(mysql=mysql)
            if check:
                mysql.errdispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : "当日提现次数已经到达上限"
                })
            
            up_sql, log_sql = Type_Log.balance_log(user_id=self.info['user_id'], 
                                money=self.info['amount']*0.01,
                                handle=5,
                                asd=0)
            mysql.update(up_sql)
            mysql.insertOne(log_sql)
            sql = "INSERT INTO balance_towx SET order_num=%s, user_id=%s, \
                balance=%s, wx_money=%s, state=2"
            cash_id = mysql.insertOne(sql, param=[
                                    self.info['partner_trade_no'],
                                    self.info['user_id'],
                                    self.info['amount']*0.01,
                                    self.info['amount']
            ])
            mysql.dispose()
            response = self.request_wx()
            mysql = Mysql()
            state = self.retmsg(response, mysql=mysql, cash_id=cash_id)
            mysql.dispose()
            msg = '提现成功' if state else '提现失败'
            ret = 0 if msg == '提现成功' else -2
            return JsonResponse({
                    'ret' : ret,
                    'msg' : msg
                })
            
        except Exception as e:
            print(e)
            mysql.errdispose()
            return JsonResponse({
                    'ret' : -2,
                    'msg' : "提现出现问题"
                })

    def request_wx(self):
        url = "https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers"
        xml = f"<xml> \
                <mch_appid>{self.info['mch_appid']}</mch_appid> \
                <mchid>{self.info['mchid']}</mchid> \
                <nonce_str>{self.info['nonce_str']}</nonce_str> \
                <partner_trade_no>{self.info['partner_trade_no']}</partner_trade_no> \
                <openid>{self.info['openid']}</openid> \
                <check_name>{self.info['check_name']}</check_name> \
                <amount>{self.info['amount']}</amount> \
                <desc>{self.info['desc']}</desc> \
                <spbill_create_ip>{self.info['spbill_create_ip']}</spbill_create_ip> \
                <sign>{self.sigin}</sign> \
                </xml>"
        print('发送的数据')
        print(xml)
        headers = {'Content-Type': 'text/xml', 'charset': 'UTF-8'}
        crt = '/crt/...'
        response_info = requests.post(
                                        url, 
                                        headers=headers,
                                        data=xml.encode(encoding='UTF-8'),
                                        cert=('/home/ubuntu/hhsc2019/shops/views/crt/apiclient_cert.pem', 
                                        '/home/ubuntu/hhsc2019/shops/views/crt/apiclient_key.pem')
                                    )
        response_info.encoding = 'UTF-8'
        return response_info

    #校验当天是否有提现
    def check_cashout(self, mysql):
        mysql = mysql
        sql = "SELECT id FROM balance_towx WHERE user_id = %s AND \
            create_time > DATE_FORMAT(NOW(), %s)"
        check = mysql.getOne(sql, param=[self.info['user_id'], '%Y-%m-%d'])
        if check:
            return check
        else:
            return False

    #查询用户信息
    def check_userinfo(self, mysql):
        mysql = mysql
        sql = "SELECT * FROM userInfo WHERE id = %s FOR UPDATE"
        user_info = mysql.getOne(sql, param=[self.info['user_id']])
        return user_info

    #处理返回值
    def retmsg(self, response, mysql, cash_id):
        mysql = mysql
        xmlmsg = xmltodict.parse(response.text)
        print(xmlmsg)
        xmlmsg = xmlmsg['xml']
        state = 0
        if xmlmsg['return_code'] == 'SUCCESS':
            if xmlmsg['result_code'] == 'SUCCESS':
                state = 1
            if xmlmsg['result_code'] == 'FAIL':
                state = 2
            sql = '''UPDATE balance_towx SET wxid=%s, end_time=%s, \
                    state=%s WHERE id=%s'''     
            mysql.update(sql, param=[
                xmlmsg['payment_no'],
                xmlmsg['payment_time'],
                state,
                cash_id
            ])
        else:
            sql = "UPDATE balance_towx SET state=0,\
                    end_time=NOW() WHERE id=%s"
            mysql.update(sql, param=[
                cash_id
            ])
        return state

class CashOut(View):

    def __init__(self):
        self.info = {}

    def post(self, request, **payload):

        handle = payload.get('handle')
        self.info['user_id'] = payload.get('user_id')
        self.info['hhcoin'] = int(request.POST.get('hhcoin'))

        if handle == 'toBalance':
            return self.toBalance()

        if handle == 'log':
            return self.log()

        def toBalance(self):
            mysql = Mysql()
            sql = "SELECT * FROM userInfo WHERE id = %s FOR UPDATE"
            user_info = mysql.getOne(sql, param=[self.info['user_id']])
            user_hhcoin = user_info.get('hhcoin')

            if int(self.info['hhcoin']) > user_hhcoin or int(self.info['hhcoin']) <= 0:
                mysql.dispose()
                return HttpResponse(returnJson(-2, '传入金额出现问题'))

            up_sql, log_sql =  Type_Log.coin_handle(user_id=self.info['user_id'], 
                handle=13, num=self.info['hhcoin'], asd=0)

            mysql.update(up_sql)
            mysql.insertOne(log_sql)

            up_sql, log_sql = Type_Log.balance_log(user_id=self.info['user_id'],
                handle=13, money=self.info['hhcoin'], asd=1)

            mysql.update(up_sql)
            mysql.insertOne(log_sql)
            mysql.dispose()
            return HttpResponse(returnJson(0, '转换成功'))

        def log(self):
            sql = "SELECT * FROM balance_towx WHERE user_id = %s ORDER BY create_time DESC"
            info = query(sql, param=[self.info['user_id']])
            return HttpResponse(returnJson(0, '查询成功', info))