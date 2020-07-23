import json
from django.http import request, HttpResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Pagings

#增加奖品
class Add_Prize(View):
    
    def post(self, request):
        prize_type = request.POST.get('prize_type') #1.商品 2.实物 3.二维码 4.cdk 5.盒盒币以及余额
        prize_detail = request.POST.get('prize_detail')
        class_id = request.POST.get('class_id')
        all_limit = request.POST.get('all_limit') #全体限量
        one_limit = request.POST.get('one_limit') #个人限量
        mysql = Mysql()
        sql = "INSERT INTO prize SET prize_type='{prize_type}', prize_detail='{prize_detail}',\
            class_id='{class_id}', all_limit='{all_limit}', one_limit='{one_limit}'".format(prize_type=prize_type, \
            prize_detail=prize_detail, class_id=class_id, all_limit=all_limit, one_limit=one_limit)
        suc = mysql.insertOne(sql)
        if suc:
            data = {}
            data['prize_id'] = suc
            data['state'] = 1
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)
            mysql.dispose()
            return HttpResponse(data)
        mysql.errdispose()
        return HttpResponse(0)

#编辑奖品
class Edit_Prize(View):

    def post(self, request):
        prize_id = request.POST.get('prize_id')
        prize_type = request.POST.get('prize_type') #1.商品 2.实物 3.二维码 4.cdk 5.盒盒币以及余额
        prize_detail = request.POST.get('prize_detail')
        class_id = request.POST.get('class_id')
        all_limit = request.POST.get('all_limit')
        one_limit = request.POST.get('one_limit')
        mysql = Mysql()
        sql = "UPDATE prize SET prize_type='{prize_type}', prize_detail='{prize_detail}', \
            class_id='{class_id}', all_limit='{all_limit}', one_limit='{one_limit}' \
            WHERE id = '{prize_id}'".format(prize_type=prize_type, prize_detail=prize_detail, \
            class_id=class_id, prize_id=prize_id, all_limit=all_limit, one_limit=one_limit)
        try:
            mysql.update(sql)
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#删除奖品
class Del_Prize(View):
    
    def post(self, request):
        prize_id = request.POST.get('prize_id')
        mysql = Mysql()
        sql = "SELECT * FROM probability WHERE prize_id = '{prize_id}'".format(prize_id=prize_id)
        info = mysql.getOne(sql)
        if info:
            mysql.dispose()
            return HttpResponse(2)  #转盘绑定了商品 不能删除
        #检查奖品类型
        sql = "SELECT * FROM prize WHERE id = '{prize_id}'".format(prize_id=prize_id)
        prize_type = mysql.getOne(sql)
        check_list = [5, 6, 7]
        #--------盒盒币余额类型
        if int(prize_type.get('prize_type')) in check_list:
            #已在数据库做对应操作
            print('删除phv类型')
        #---------卷码类型
        if int(prize_type.get('prize_type')) == 3:
            #已在数据库做对应操作
            print('删除cdk类型')
        #删除奖品
        sql = "DELETE FROM prize WHERE id='{prize_id}'".format(prize_id=prize_id)
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#查询奖品
class Sel_Prize(View):
    
    def get(self, request):
        prize_name = request.GET.get('prize_name')
        row = request.GET.get('row')
        page = request.GET.get('page')
        mysql = Mysql()
        sql = "SELECT prize.*, prize_class.class_name, prize_type_class.prize_type_name FROM prize \
            LEFT JOIN prize_class ON prize.class_id = prize_class.id \
            LEFT JOIN prize_type_class ON prize.prize_type = prize_type_class.prize_type_id \
            WHERE prize.prize_detail LIKE '%{prize_name}%'".format(prize_name=prize_name)
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            sumpage, info = Pagings.paging(info, row=row, page=page)
            data = {}
            data['sumpage'] = sumpage
            data['info'] = info
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)
            return HttpResponse(data)
        return HttpResponse(0)