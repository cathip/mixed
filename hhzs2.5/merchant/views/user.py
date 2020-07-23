import json
from django.http import request, HttpResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Pagings, ComplexEncode
import datetime

#查看商户下对应的账户
class Sel_User(View):

    def get(self, request):
        mer_id = request.GET.get('mer_id')
        mysql = Mysql()
        sql = f"SELECT mer_userid, user_name, wx_img, phone, is_admin, openid FROM mer_admin WHERE mer_id = {mer_id}"
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            data = json.dumps(info, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(data)
        return HttpResponse(0)

#更新用户头像
class Up_User(View):

    def post(self, request):
        wx_name = request.POST.get('wx_name')
        wx_img = request.POST.get('wx_img')
        openid = request.POST.get('openid')
        mysql = Mysql()
        sql = f"SELECT mer_userid FROM mer_admin WHERE openid = '{openid}'"
        check_user = mysql.getOne(sql)
        if check_user:
            sql = f"UPDATE mer_admin SET wx_img='{wx_img}', wx_name='{wx_name}' WHERE openid='{openid}'"
            suc = mysql.update(sql)
            if suc:
                mysql.dispose()
                return HttpResponse(1)
            mysql.errdispose()
            return HttpResponse(0)
        mysql.dispose()
        return HttpResponse("openid不存在")

#增加用户
class Add_User(View):

    def post(self, request):
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        pwd = request.POST.get('pwd')
        mer_id = request.POST.get('mer_id')
        mysql = Mysql()
        sql = f"SELECT mer_userid FROM mer_admin WHERE phone = '{phone}'"
        check_user = mysql.getOne(sql)
        if check_user:
            return HttpResponse(2) #已被注册
        sql = f"INSERT INTO mer_admin SET phone='{phone}', user_name='{name}',\
            `password`='{pwd}', is_admin='0', mer_id='{mer_id}'"
        suc = mysql.insertOne(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#删除用户
class Del_User(View):

    def post(self, request):
        mer_userid = request.POST.get('mer_userid')
        mysql = Mysql()
        #sql = f"DELETE FROM mer_admin WHERE phone = '{phone}' "
        sql = f"DELETE FROM mer_admin WHERE mer_userid = '{mer_userid}'"
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

class Test(View):
    
    def get(self, request):
        mysql = Mysql()
        sql = 'SELECT *, DATE_ADD(pay_time,INTERVAL 3 DAY) as c  FROM mer_orders WHERE order_num="BI15631632207349"'
        info = mysql.getOne(sql)
        ex_time = info.get('c')
        now_time = datetime.datetime.now()
        if ex_time > now_time:
            print('没过期')
        if ex_time <= now_time:
            print('过期了')
        # d1 = datetime.datetime.strptime(info.get('c'), '%Y-%m-%d %H:%M:%S')
        # d2 = datetime.datetime.strptime(info.get('pay_time'), '%Y-%m-%d %H:%M:%S')
        # print(d1)
        # print(d2)
        # if d1 > d2:
        #     print('zzzzzzzzz')
        mysql.dispose()
        info = json.dumps(info, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
        return HttpResponse(info)