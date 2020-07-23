import json
import math
from django.http import request, HttpResponse, JsonResponse, QueryDict
from django.views import View
from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Type_Log, Pagings
from random import randint
from uuid import uuid4
from django.core.cache import cache


class Turntable(View):

    def post(self, request):
        user_id = request.POST.get('user_id')
        if not user_id:
            return HttpResponse('user_id获取失败')
        print('id：'+user_id+'用户抽奖')
        data = self.turntable_prize(user_id=user_id)
        if data:
            print(data)
            #全部被抽完
            if data == 2:
                return HttpResponse(2)
            #个人被抽完
            if data == 3:
                return HttpResponse(3)
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)
            return HttpResponse(data)
        return HttpResponse(0)

    #根据号数做逻辑操作
    def turntable_prize(self, user_id):
        turntable_id = self.turntable()
        mysql = Mysql()
        sql = "SELECT prize.id, prize_type, prize_detail FROM probability as p \
                LEFT JOIN prize ON p.prize_id = prize.id WHERE p.id = {turntable}".format(turntable=turntable_id)
        info = mysql.getOne(sql)
        data = {}
        data['turntable_id'] = turntable_id
        data['prize_id'] = info.get('id')
        data['prize_type'] = info.get('prize_type')
        data['prize_detail'] = info.get('prize_detail')
        #查询限量总数
        sql = "SELECT all_limit, one_limit FROM prize WHERE id = '{prize_id}'".format(prize_id=data['prize_id'])
        #奖品限量字典
        limit_num = mysql.getOne(sql)
        all_limit_num = int(limit_num.get('all_limit'))
        one_limit_num = int(limit_num.get('one_limit'))
        sql = "SELECT COUNT(id) as count FROM reward_log WHERE prize_id = '{prize_id}'".format(prize_id=data['prize_id'])
        #全部已抽中奖品总数
        all_num = mysql.getOne(sql)
        sql = "SELECT COUNT(id) as count FROM reward_log WHERE prize_id = '{prize_id}' \
            AND user_id = '{user_id}'".format(prize_id=data['prize_id'], user_id=user_id)
        #个人抽中奖品总数
        one_num = mysql.getOne(sql)
        if all_num:
            all_num = all_num.get('count')
            if all_num >= all_limit_num and all_limit_num != 0:
                print('总数被抽完')
                #商品已被抽完
                #mysql.dispose()
                #return 2
                data['prize_type'] == 8
            else:
                pass
        if one_num:
            one_num = one_num.get('count')
            if one_num >= one_limit_num and one_limit_num != 0:
                #个人中奖次数已达上限
                print('个人次数抽完')
                #mysql.dispose()
                #return 3
                data['prize_type'] == 8
            else:
                pass
        #还有剩余总数 继续抽奖
        try:
            #自营类商品
            if int(data['prize_type']) == 1:
                print('自营商品')
                #查询商品相关信息
                sql = "SELECT prize_stock.stock_numb, stock.id, stock.stock_name \
                    FROM prize_stock LEFT JOIN stock ON prize_stock.stock_id = stock.id \
                    WHERE prize_stock.prize_id={prize_id}".format(prize_id=data['prize_id'])
                stock_info = mysql.getOne(sql)
                data['stock_numb'] = int(stock_info.get('stock_numb'))
                data['stock_id'] = stock_info.get('id')
                data['stock_name'] = stock_info.get('stock_name') + data['prize_detail'] + str(data['stock_numb']) + '份'
                #查询以中总量
                # sql = "SELECT COUNT(id) as count FROM reward_log WHERE prize_id = '{prize_id}'".format(prize_id=data['prize_id'])
                # real_numb = mysql.getOne(sql)
                # real_numb = int(real_numb.get('count'))
                # #如果超过限量返回谢谢惠顾
                # if real_numb >= data['stock_numb']:
                #     data['prize_type'] = 8
                #     int(data['prize_type']) == 8
                # #没超过 让他中奖
                # else:
                re_log = Type_Log.reward_log(user_id=user_id, prize_id=data['prize_id'], detail=data['stock_name'], prize_type=1, get=0)
                re_id = mysql.insertOne(re_log)
                data['re_id'] = re_id
                mysql.dispose()
                return data
            #外部类商品
            if int(data['prize_type']) == 2:
                print('外部商品')
                re_log = Type_Log.reward_log(user_id=user_id, prize_id=data['prize_id'], detail=data['prize_detail'], prize_type=2, get=0)
                re_id = mysql.insertOne(re_log)
                data['re_id'] = re_id
                mysql.dispose()
                return data
            #卷码类型
            if int(data['prize_type']) == 3:
                sql = "SELECT * FROM prize_coupon WHERE prize_id = '{prize_id}' \
                    AND `get` = '0' ORDER BY id".format(prize_id=info.get('id'))
                coupon = mysql.getOne(sql)
                print('卷码')
                if coupon:
                    print('还有卷码')
                    coupon_detail = coupon.get('coupon')
                    sql = "UPDATE prize_coupon SET `get` = 1 WHERE id = '{coupon_id}'".format(coupon_id=coupon.get('id'))
                    mysql.update(sql)
                    detail = data['prize_detail'] + "：" + coupon_detail
                    data['prize_detail'] = detail
                    re_log = Type_Log.reward_log(user_id=user_id, prize_id=data['prize_id'], detail=detail, prize_type=3, get=1)
                    mysql.insertOne(re_log)
                    mysql.dispose()
                    return data
                else:
                    print('卷码不够')
                    # sql = "SELECT probability.id, probability.prize_id FROM probability LEFT JOIN prize \
                    #     ON prize.id = probability.prize_id WHERE prize.prize_type =8"
                    # probability_info = mysql.getOne(sql)
                    # data['turntable_id'] = probability_info.get('id')
                    # data['prize_id'] = probability_info.get('prize_id')
                    # data['prize_type'] = 9
                    # data['prize_detail'] = '谢谢惠顾'
                    # data['warning_info'] = '其实我是优惠卷 但是我没有了'
                    data['prize_type'] = 8
                    print(data['prize_type'])
            #二维码类型
            if int(data['prize_type']) == 4:
                print('测试二维码')
                re_log = Type_Log.reward_log(user_id=user_id, prize_id=data['prize_id'], detail=data['prize_detail'], prize_type=4, get=1)
                mysql.insertOne(re_log)
                mysql.dispose()
                new_data = data
                return new_data
            #盒盒币
            if int(data['prize_type']) == 5:
                print('盒盒币')
                sql = "SELECT num FROM prize_phv WHERE prize_id = {prize_id}".format(prize_id=data['prize_id'])
                num = mysql.getOne(sql)
                num = int(num.get('num'))
                up_sql, log_sql = Type_Log.coin_handle(user_id=user_id, handle=6, num=num, asd=1)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
                re_log = Type_Log.reward_log(user_id=user_id, prize_id=data['prize_id'], detail=data['prize_detail'], prize_type=5, get=1)
                mysql.insertOne(re_log)
                mysql.dispose()
                return data
            #账号vip
            if int(data['prize_type']) == 6:
                print('账号vip')
                sql = "SELECT num FROM prize_phv WHERE prize_id = {prize_id}".format(prize_id=info.get('id'))
                vip_time = mysql.getOne(sql)
                vip_time = int(vip_time.get('num'))
                sql = "UPDATE userInfo SET vipEndTime = DATE_ADD(vipEndTime,INTERVAL {vip_time} MONTH) \
                    WHERE id = '{user_id}'".format(vip_time=vip_time, user_id=user_id)
                mysql.update(sql)
                re_log = Type_Log.reward_log(user_id=user_id, prize_id=data['prize_id'], detail=data['prize_detail'], prize_type=6, get=1)
                mysql.insertOne(re_log)
                mysql.dispose()
                return data
            #余额
            if int(data['prize_type']) == 7:
                print('余额')
                sql = "SELECT num FROM prize_phv WHERE prize_id = {prize_id}".format(prize_id=info.get('id'))
                money = mysql.getOne(sql)
                money = float(money.get('num'))
                up_sql, log_sql = Type_Log.balance_log(user_id=user_id, handle=2, money=money, asd=1)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
                re_log = Type_Log.reward_log(user_id=user_id, prize_id=data['prize_id'], detail=data['prize_detail'], prize_type=7, get=1)
                mysql.insertOne(re_log)
                mysql.dispose()
                return data
            #谢谢惠顾
            if int(data['prize_type']) == 8:
                print('谢谢惠顾')
                data['turntable_id'] = 8
                data['prize_id'] = 66
                data['prize_type'] = 8
                data['prize_detail'] = '谢谢惠顾'
                re_log = Type_Log.reward_log(user_id=user_id, prize_id=data['prize_id'], detail=data['prize_detail'], prize_type=8, get=1)
                mysql.insertOne(re_log)
                mysql.dispose()
                return data
            #商品没了 继续抽 抽中为止(有风险已弃用)
            if int(data['prize_type']) == 9:
                print('商品没了 继续抽 抽中为止')
                return self.turntable_prize(user_id=user_id)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return False

    #转盘返回指针对应号数
    def turntable(self):
        mysql = Mysql()
        sql = "SELECT * FROM  probability ORDER BY id"
        info = mysql.getAll(sql)
        mysql.dispose()
        random_list = []
        id_list = []
        for i in info:
            random_list.append(i.get('probability_num'))
            id_list.append(i.get('id'))
        a = sum(random_list[0:1]) + 1
        b = sum(random_list[0:2]) + 1
        c = sum(random_list[0:3]) + 1
        d = sum(random_list[0:4]) + 1
        e = sum(random_list[0:5]) + 1
        f = sum(random_list[0:6]) + 1
        g = sum(random_list[0:7]) + 1
        h = sum(random_list[0:8]) + 1
        num = randint(1, 100)
        if num in list(range(1, a)):
            return id_list[0]
        elif num in list(range(a, b)):
            return id_list[1]
        elif num in list(range(b, c)):
            return id_list[2]
        elif num in list(range(c, d)):
            return id_list[3]
        elif num in list(range(d, e)):
            return id_list[4]
        elif num in list(range(e, f)):
            return id_list[5]
        elif num in list(range(f, g)):
            return id_list[6]
        elif num in list(range(g, h)):
            return id_list[7]


#中奖记录
class Reward_Log(View):

    def get(self, request):
        user_id = request.GET.get("user_id")
        row = request.GET.get('row')
        page = request.GET.get('page')
        mysql = Mysql()
        page, row = Pagings.mysqlPagings(page=page, row=row)
        sql = f"SELECT id, logtime, detail, prize_type, `get` FROM \
            reward_log WHERE user_id = {user_id} AND prize_type !=8 \
            ORDER BY logtime DESC limit {page}, {row}"
        info = mysql.getAll(sql)
        sql = f"SELECT COUNT(id) as c FROM reward_log WHERE \
            user_id = {user_id} AND prize_type !=8"
        sum_page = mysql.getOne(sql)
        sum_page = math.ceil(int(sum_page.get('c')) / int(row))
        mysql.dispose()
        if info:
            data = {}
            data['sum_page'] = sum_page
            data['info'] = info
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(data)
        return HttpResponse(0)


