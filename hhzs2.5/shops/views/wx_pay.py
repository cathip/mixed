import re
import os
import json
import time
import string
import random
import requests
import datetime
import xmltodict
from hashlib import md5
from xml.etree.ElementTree import fromstring

from django.views import View
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse, request

from base.cmysql import Mysql
from base.limits import hold_shikou
from base.wx_config import Mch_key, NOTIFY_URL
from base.shop_base import Type_Log, callJson, getSign, getNonceStr, erroLog

# 微信支付

class Wx_Pay(View):

    def __init__(self):
        self.info = {}

    def post(self, request, **payload):

        self.info['openid'] = payload.get('openid')  # openid  
        self.info['appid'] = request.POST.get('appid')  # 公众账号ID  
        self.info['mch_id'] = request.POST.get('mch_id')  # 商户号 
        self.info['nonce_str'] = getNonceStr()  #随机字符串
        self.info['body'] = request.POST.get('body')  # 商品描述 
        self.info['out_trade_no'] = request.POST.get('out_trade_no')  # 商户订单号  
        self.info['total_fee'] = request.POST.get('total_fee')  # 标价金额 
        self.info['spbill_create_ip'] = request.POST.get('spbill_create_ip')  # 终端IP 
        self.info['notify_url'] = f'http://{NOTIFY_URL}/shops/api/wx_callback'
        self.info['trade_type'] = 'JSAPI'  # 交易类型 
        self.info['sign_type'] = 'MD5'  #sign加密类型
        self.info['sign'] = getSign(ks=self.info)  # 签名

        print(self.info)

        response = self.wx_pay()

        pay_data = self.retmsg(response)

        if pay_data:
            pay_data['appId'] = self.info['appid']
            pay_data['signType'] = 'MD5'
            pay_data['timeStamp'] = str(int(time.time()))
            # 计算签名
            paySign = getSign(ks=pay_data)
            pay_data['paySign'] = paySign
            del pay_data['appId']
            pay_data['ret'] = 0
            pay_data['msg'] = '请求支付成功'
        else:
            pay_data = {
                'ret' : -2,
                'msg' : '请求支付失败'
            }

        return JsonResponse(pay_data)

    # 调用微信支付接口
    def wx_pay(self):
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        xml = f'''<xml>\
                <appid>{self.info['appid']}</appid> \
                <mch_id>{self.info['mch_id']}</mch_id> \
                <nonce_str>{self.info['nonce_str']}</nonce_str> \
                <body>{self.info['body']}</body> \
                <out_trade_no>{self.info['out_trade_no']}</out_trade_no> \
                <total_fee>{self.info['total_fee']}</total_fee> \
                <spbill_create_ip>{self.info['spbill_create_ip']}</spbill_create_ip> \
                <notify_url>{self.info['notify_url']}</notify_url> \
                <trade_type>{self.info['trade_type']}</trade_type> \
                <openid>{self.info['openid']}</openid> \
                <sign_type>MD5</sign_type> \
                <sign>{self.info['sign']}</sign> \
            </xml>'''
        headers = {'Content-Type': 'text/xml', 'charset': 'UTF-8'}
        response_info = requests.post(
            url, data=xml.encode(encoding='UTF-8'), headers=headers)
        response_info.encoding = 'UTF-8'
        return response_info

    # 返回值
    def retmsg(self, response):
        try:
            xmlmsg = xmltodict.parse(response.text)
            print(xmlmsg)
            if xmlmsg['xml']['return_code'] == 'SUCCESS' and xmlmsg['xml']['result_code'] == 'SUCCESS':
                msg = 1
                # 获取预支付交易会话标识
                prepay_id = xmlmsg['xml'].get('prepay_id')
                # 获取随机字符串
                nonce_str = xmlmsg['xml'].get('nonce_str')
                data = {
                    'nonceStr' : nonce_str,
                    "package" : "prepay_id=" + prepay_id,
                }
                # 如果，返回的xml中，err_code的值是NOTENOUGH， 则说明余额不足
            elif xmlmsg['xml']['err_code'] == 'NOTENOUGH':
                data = False
            #转账失败
            else:
                data = False
            return data

        except Exception as e:
            print('------------------支付接口，返回的几个参数')
            return False


# 微信回调接口

class Wx_Callback(View):

    def __init__(self):
        self.Info = {}

    def post(self, request):
        xml_data = request.body
        if xml_data:
            xmls = str(request.body, encoding='utf-8')
            tree = fromstring(xmls)
            xmlmsg = xmltodict.parse(request.body)
            print(type(xmlmsg))
            print(dict(xmlmsg))
            self.Info['appid'] = tree.find('appid').text   # appid
            self.Info['return_code'] = tree.find('return_code').text # 订单状态码
            self.Info['total_fee'] = tree.find('total_fee').text  # 订单金额
            self.Info['orderNum'] = tree.find('out_trade_no').text  # 订单编号
            self.Info['wxid'] = tree.find('transaction_id').text   # 微信支付订单号
            self.Info['openid'] = tree.find('openid').text  # openid
            # 成功信息
            if self.Info['return_code'] == 'SUCCESS':
                orderType = self.Info['orderNum'].split('-')
                orderType = orderType[0]
                if orderType == 'ShopOrder':
                    self.shopOrder()
                if orderType == 'MerOrder':
                    self.merOrder()
                if orderType == 'MerPay':
                    self.merPayOrder()
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

    def shopOrder(self):
        mysql = Mysql()
        sql = "SELECT o.product_id, o.stock_name, p.user_goods_limit FROM ordergoods \
            AS o LEFT JOIN product AS p ON o.product_id = p.id WHERE o.order_id = %s"
        info = mysql.getAll(sql, param=[self.Info['orderNum']])
        sql = "SELECT createUser FROM orders WHERE orderNum = %s"
        user_id = mysql.getOne(sql, param=[self.Info['orderNum']])
        holds = []
        for i in info:
            if i.get('user_goods_limit') != 0:
                key = 'product_1909_' + str(i.get('product_id'))
                data = {}
                data['key'] = key
                data['ext'] = str(i.get('stock_name'))
                holds.append(data)
        if holds:
            check = hold_shikou(holds=holds, user_id=user_id.get('createUser'), mysql=mysql)
            if check['ret'] == -2:
                raise Exception("实扣限量出现问题")
        mysql = Mysql()
        sql = "update orders set state = '1', wxid=%s where orderNum=%s"
        suc = mysql.update(sql, param=[self.Info['wxid'], self.Info['orderNum']])
        mysql.dispose()

    def merOrder(self):
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

    def merPayOrder(self):
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
