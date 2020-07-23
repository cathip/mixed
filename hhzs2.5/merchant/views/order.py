import json
import datetime
import requests

from django.http import request, HttpResponse
from django.views import View

from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Pagings, callJson


#查看商户订单
class Sel_Orders(View):

    def get(self, request):
        mer_id = request.GET.get("mer_id")
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        handler = request.GET.get('handler')

        mysql = Mysql()
        if handler == 'online':
            sql = f"SELECT m.*, u.wxname, u.user_img FROM mer_orders as m \
                    LEFT JOIN userInfo as u ON m.user_id = u.id \
                    WHERE m.mer_id = {mer_id} AND state = 1 AND  \
                    m.create_time BETWEEN '{start_time}' AND '{end_time}'\
                    ORDER BY m.create_time DESC " 
            order_info = mysql.getAll(sql)
            if order_info:
                order_list = []
                for i in order_info:
                    data = {}
                    sql = f'''SELECT * FROM mer_ordergoods WHERE order_num="{i.get('order_num')}"'''
                    order_goods = mysql.getAll(sql)
                    data['order'] = i
                    for x in order_goods:
                        specs = x.get('mer_stockname').split('-')
                        x['stock_name'] = specs[0]
                        x['spec'] = '-'.join(specs[1:len(specs)])
                    data['goods'] = order_goods
                    order_list.append(data)
                mysql.dispose()
                return HttpResponse(callJson(order_list))
            mysql.dispose()
            return HttpResponse(0)
        if handler == 'underline':
            sql = f"SELECT m.*, u.wxname, u.user_img FROM mer_pay \
                AS m LEFT JOIN userInfo AS u ON m.user_id = u.id WHERE  \
                mer_id = {mer_id} AND state = 1 AND m.create_time BETWEEN \
                '{start_time}' AND '{end_time}' ORDER BY m.create_time  DESC"
            info = mysql.getAll(sql)
            mysql.dispose()
            if info:
                return HttpResponse(callJson(info))
            return HttpResponse(0)
        else:
            return HttpResponse(0)

#扫一扫（点击确认后）
class Scan_Qrcode(View):

    def post(self, request):
        order_num = request.POST.get('order_num')
        mer_id = request.POST.get('mer_id')
        mysql = Mysql()
        sql = f"SELECT `get`, state FROM mer_orders WHERE \
            order_num = '{order_num}' AND mer_id = '{mer_id}'"
        check_get = mysql.getOne(sql)
        data = {}
        if check_get:
            if int(check_get.get('get')) == 1:
                data['msg'] = "FAILE"
                data['info'] = "二维码已经被扫描使用"
                mysql.dispose()
                return HttpResponse(callJson(data))
            if int(check_get.get('state')) != 1:
                data['msg'] = "FAILE"
                data['info'] = "二维码未付款"
                mysql.dispose()
                return HttpResponse(callJson(data))
            if int(check_get.get('get')) == 0:
                sql = f'SELECT *, DATE_ADD(pay_time,INTERVAL 3 DAY) as c  \
                    FROM mer_orders WHERE order_num="{order_num}"'
                info = mysql.getOne(sql)
                ex_time = info.get('c')
                now_time = datetime.datetime.now()
                if ex_time >= now_time:
                    print('没过期')
                    sql = f"UPDATE mer_orders SET `get` = 1 WHERE order_num = '{order_num}'"
                    suc = mysql.update(sql)
                    if suc:
                        data['msg'] = "OK"
                        data['info'] = "扫码成功"
                        mysql.dispose()
                        return HttpResponse(callJson(data))
                if ex_time < now_time:
                    print('过期了')
                    data['msg'] = "FAILE"
                    data['info'] = "二维码过期"
                    return HttpResponse(callJson(data))
        mysql.dispose()
        data['msg'] = "FAILE"
        data['info'] = "订单号错误"
        return HttpResponse(callJson(data))

#扫一扫
class Scan_Order(View):
    
    def get(self, request):
        mer_id = request.GET.get('mer_id')
        order_num = request.GET.get('order_num')
        mysql = Mysql()
        data = {}
        sql = f"SELECT * FROM mer_orders WHERE order_num = '{order_num}' AND mer_id='{mer_id}'"
        order_info = mysql.getOne(sql)
        if order_info:
            data['order'] = order_info
            sql = f"SELECT * FROM mer_ordergoods WHERE order_num = '{order_num}'"
            goods = mysql.getAll(sql)
            mysql.dispose()
            for x in goods:
                print('mer_stockname')
                specs = x.get('mer_stockname').split('-')
                x['stockname'] = specs[0]
                x['spec'] = '-'.join(specs[1:len(specs)])
            data['goods'] = goods
            return HttpResponse(callJson(data))
        mysql.dispose()
        return HttpResponse(0)

#查看今日订单总金额 以及单数
class Order_Numbs(View):

    def get(self, request):
        mer_id = request.GET.get('mer_id')
        mysql = Mysql()
        sql = f"SELECT mer_type FROM merchant WHERE mer_id = {mer_id}"
        mer_type = mysql.getOne(sql)
        mer_type = int(mer_type.get('mer_type'))

        sql = f"SELECT SUM(wx_money+balance) as money, COUNT(*) as numbs FROM mer_orders \
            WHERE TO_DAYS(create_time) = TO_DAYS(NOW()) AND mer_id = '{mer_id}' AND state = 1 "
        mer_order = mysql.getOne(sql)
        money1 = mer_order.get('money') if mer_order.get('money') else 0
        numbs1 = mer_order.get('numbs')

        sql = f"SELECT SUM(wx_money+balance) as money, COUNT(*) as numbs FROM mer_pay \
                WHERE TO_DAYS(create_time) = TO_DAYS(NOW()) AND mer_id = '{mer_id}' AND state = 1"
        mer_pay = mysql.getOne(sql)
        money2 = mer_pay.get('money') if mer_pay.get('money') else 0
        numbs2 = mer_pay.get('numbs')

        info = mysql.getOne(sql)
        mysql.dispose()
        info = {
            'money' : money1 + money2,
            'numbs' : numbs1 + numbs2
        }
        return HttpResponse(callJson(info))
