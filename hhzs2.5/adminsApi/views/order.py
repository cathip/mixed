import json
from django.http import request, HttpResponse, JsonResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import Type_Log, ComplexEncode, Pagings, getOrderNum

#查看订单列表
class Sel_Orders(View):
    
    def get(self, request):
        store_id = request.GET.get('store_id')
        order_num = request.GET.get('order_num') #订单编号
        order_state = request.GET.get('order_state') #订单状态0待付款1代发货2待收货3售后4已完成5取消6抽奖
        row = request.GET.get('row')
        page = request.GET.get('page')
        print(request.GET)
        mysql = Mysql()
        sql = "SELECT orders.*, userInfo.wxname, store.store_name FROM orders \
                LEFT JOIN userInfo ON orders.createUser = userInfo.id \
                LEFT JOIN store ON store.id = orders.store_id \
                ORDER BY createTime DESC"
        if order_num:
            sql = f"SELECT orders.*, userInfo.wxname, store.store_name FROM orders \
                LEFT JOIN userInfo ON orders.createUser = userInfo.id \
                LEFT JOIN store ON store.id = orders.store_id \
                WHERE orders.orderNum = '{order_num}' \
                ORDER BY createTime DESC"
        if order_state:
            sql = f"SELECT orders.*, userInfo.wxname, store.store_name FROM orders \
                LEFT JOIN userInfo ON orders.createUser = userInfo.id \
                LEFT JOIN store ON store.id = orders.store_id \
                WHERE orders.state = '{order_state}' \
                ORDER BY createTime DESC"
        if store_id:
            sql = f"SELECT orders.*, userInfo.wxname, store.store_name FROM orders \
                LEFT JOIN userInfo ON orders.createUser = userInfo.id \
                LEFT JOIN store ON store.id = orders.store_id \
                WHERE orders.store_id = '{store_id}' \
                ORDER BY createTime DESC"
        if store_id and order_state:
            sql = f"SELECT orders.*, userInfo.wxname, store.store_name FROM orders \
                LEFT JOIN userInfo ON orders.createUser = userInfo.id \
                LEFT JOIN store ON store.id = orders.store_id \
                WHERE orders.store_id = '{store_id}' AND orders.state = '{order_state}' \
                ORDER BY createTime DESC"
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            sumpage, info = Pagings.paging(info, row=row, page=page)
            data = {}
            data['sumpage'] = sumpage
            data['info'] = info
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(data)
        return HttpResponse(0)

#查看订单详情
class Sel_Order_Detail(View):

    def get(self, request):
        order_num = request.GET.get('order_num') #订单编号
        mysql = Mysql()
        sql = f"SELECT * FROM ordergoods WHERE order_id = '{order_num}'"
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            info = json.dumps(info, ensure_ascii=True, sort_keys=False, indent=4)
            return HttpResponse(info)
        else:
            return HttpResponse(0)

#发货
class Deliver_goods(View):

    def post(self, request):
        order_num = request.POST.get('order_num') #订单编号
        express_num = request.POST.get('express_num') # 快递单号
        mysql = Mysql()
        sql = f"UPDATE orders SET state = '2', express_num = '{express_num}' WHERE state = '1' \
            AND orderNum = '{order_num}'"
        print(sql)
        try:
            mysql.update(sql)
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#取消订单 订单状态0待付款1代发货2待收货3售后4已完成5取消6抽奖7删除
class Cancel_Order(View):
    
    def post(self, request):
        order_num = request.POST.get('order_num')
        mysql = Mysql()
        sql = f"UPDATE orders SET state = '5' WHERE orderNum = '{order_num}'"
        try:
            mysql.update(sql)
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)
            
#删除订单
class Del_Order(View):
    
    def post(self, request):
        order_num = request.POST.get('order_num')
        mysql = Mysql()
        sql = f"UPDATE orders SET state = '7' WHERE orderNum = '{order_num}'"
        try:
            mysql.update(sql)
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#查看售后订单
class As_Order(View):

    def get(self, request):
        order_num = request.GET.get('order_num')
        mysql = Mysql()
        sql = f"SELECT * FROM as_orders WHERE order_id = '{order_num}'"
        info = mysql.getOne(sql)
        mysql.dispose()
        if info:
            info = json.dumps(info, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(info)
        return HttpResponse(0)

#处理售后订单
class Up_As_Order(View):

    def post(self, request):
        order_num = request.POST.get('order_num')
        remark = request.POST.get('remark')
        user_id = request.POST.get('user_id')
        refundMoney = float(request.POST.get('refundMoney')) 
        refundHHcoin = int(request.POST.get('refundHHcoin'))
        hand_type = int(request.POST.get('hand_type'))  #1 退款 2 换货 3 拒绝
        #------------------------------------------------------
        new_order_num = getOrderNum('ShopOrder')
        address = request.POST.get('address')
        Consignee = request.POST.get('Consignee')  #收货人
        mobile = request.POST.get('mobile')
        sendTime = request.POST.get('sendTime')   #送货时间
        remark = f"售后订单: {order_num} 变更为 {new_order_num}，已经重新发货"
        stock_list = json.loads(request.POST.get('stock_list')) 
        #[{'stock_id':1, 'num':2}, {'stock_id':1, 'num':2}]
        #退款 盒盒币余额都退
        #---------------------------------------
        mysql = Mysql()
        try:
            if hand_type == 1:
                #退余额
                up_sql, log_sql = Type_Log.balance_log(user_id=user_id, handle=3, money=refundMoney, asd=1)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
                #退盒盒币
                up_sql, log_sql = Type_Log.coin_handle(user_id=user_id, handle=9, num=refundHHcoin, asd=1)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
                #更新售后订单表
                sql = f"UPDATE as_orders SET  isCheck = '1', remark = '已成功退款', \
                    refundMoney = '{refundMoney}', refundHHcoin = '{refundHHcoin}', \
                    Audit_time = Now(), refund_time=NOW() WHERE orderNum = '{order_num}'"
                mysql.update(sql)
                sql = f"UPDATE orders SET state = '4' WHERE orderNum = '{order_num}'"
                mysql.update(sql)
                mysql.dispose()
                return HttpResponse(1)
            if hand_type == 2:
                sql = f'''INSERT INTO orders SET orderNum="{new_order_num}", \
                    createUser="{user_id}", address="{address}",\
                    Consignee="{Consignee}", mobile="{mobile}", \
                    sendTime="{sendTime}", remark="{remark}", \
                    state=1, freight="0"'''
                mysql.insertOne(sql)
                #插入到订单商品表
                for i in stock_list:
                    #i.get('stock_id') 下单的库存id
                    #i.get('stock_id') 下单的库存数量
                    sql = f"SELECT stock_name, img, price, hehecoin, \
                        stock_detail FROM stock WHERE id = {i.get('stock_id')}"
                    stock_info = mysql.getOne(sql)
                    price += float(stock_info.get('price')) * int(i.get('num'))
                    hhcoin += int(stock_info.get('hehecoin')) * int(i.get('num'))
                    sql = f'''INSERT INTO ordergoods SET \
                        order_id="{new_order_num}", \
                        stock_id="{i.get('stock_id')}", \
                        num="{i.get('num')}", \
                        money="{stock_info.get('price')}",\
                        stock_hhcoin="{stock_info.get('hehecoin')}", \
                        stock_img="{stock_info.get('img')}", \
                        stock_detail="{stock_info.get('stock_detail')}", \
                        stock_name="{stock_info.get('stock_name')}"'''
                    mysql.insertOne(sql)
                #更新售后订单表
                sql = f"UPDATE as_orders SET  isCheck = '1', remark = '{remark}', \
                    refundMoney = '0', refundHHcoin = '0', \
                    Audit_time = Now(), refund_time=NOW() WHERE orderNum = '{order_num}'"
                mysql.update(sql)
                sql = f"UPDATE orders SET state = '4' WHERE orderNum = '{order_num}'"
                mysql.update(sql)
                mysql.dispose()
                return HttpResponse(1)
            if hand_type == 3:
                #审核不通过
                sql = f"UPDATE as_orders SET  isCheck = '2', remark = '{remark}', \
                    Audit_time = Now() WHERE orderNum = '{order_num}'"
                mysql.update(sql)
                sql = f"UPDATE orders SET state = '4' WHERE orderNum = '{order_num}'"
                mysql.update(sql)
                mysql.dispose()
                return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)


#自营商家查看流水
class Order_Flow(View):

    def get(self, request):
        store_id = request.GET.get('store_id')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        row = request.GET.get('row')
        page = request.GET.get('page')
        mysql = Mysql()
        sql = f'''SELECT \
                    COUNT(*) AS numbs, \
                    SUM(orderMoney) AS sum_money \
                FROM \
                    orders \
                WHERE \
                    store_id = "{store_id}" \
                AND state = 4 \
                AND createTime BETWEEN "{start_time}" \
                AND "{end_time}"''' 
        month_info = mysql.getOne(sql)
        sql = f'''SELECT \
                    COUNT(*) AS numbs, \
                    DATE_FORMAT(createTime, "%Y-%m-%d") AS creata_time, \
                    SUM(orderMoney) AS sum_money \
                FROM \
                    orders \
                WHERE \
                    store_id = "{store_id}" \
                AND state = 4 \
                AND createTime BETWEEN "{start_time}" \
                AND "{end_time}" \
                GROUP BY \
                    DATE_FORMAT(createTime, "%Y-%m-%d")'''
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            sum_page, info = Pagings.paging(info, row=row, page=page)
            data = {}
            data['sum_page'] = sum_page
            data['month_info'] = month_info
            data['info'] = info
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(data)
        return HttpResponse(0)

#查看商家流水
class Sel_Store_Turnover(View):

    def get(self, request):
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        row = request.GET.get('row')
        page = request.GET.get('page')
        mysql = Mysql()
        sql = f"SELECT \
                    COUNT(*) AS numbs, \
                    s.store_name, \
                    sum(o.orderMoney) AS sum_money \
                FROM  orders AS o ON  \
                LEFT JOIN store AS s ON o.store_id = s.id \
                WHERE o.state = 4  AND \
                o.createTime BETWEEN '{start_time}' AND '{end_time}' GROUP BY s.id "
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            sum_page, info = Pagings.paging(info, row=row, page=page)
            data = {}
            data['sum_page'] = sum_page
            data['info'] = info
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(data)
        return HttpResponse(0)