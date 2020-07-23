import json
from django.http import request, HttpResponse, JsonResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Pagings

#增加商家
class Add_Merchant(View):

    def post(self, request):
        self.params = {}
        self.params['mer_address'] = request.POST.get('mer_address')
        self.params['mer_name'] = request.POST.get('mer_name')
        self.params['mer_slogan'] = request.POST.get('mer_slogan')
        self.params['mer_longitude'] = float(request.POST.get('mer_longitude')) #经度
        self.params['mer_latitude'] = float(request.POST.get('mer_latitude')) #纬度
        self.params['mer_img'] = request.POST.get('mer_img') #商户banner
        self.params['mer_type'] = int(request.POST.get('mer_type')) #属性1吃的2喝的3玩的
        self.params['mer_logo'] = request.POST.get('mer_logo') #商户头像 mer_logo
        self.params['mer_sales'] = float(request.POST.get('mer_sales')) #折扣 mer_sales 
        mysql = Mysql()
        sql = "INSERT INTO merchant SET mer_address='{mer_address}', mer_name='{mer_name}', \
            mer_longitude='{mer_longitude}', mer_latitude='{mer_latitude}',mer_img='{mer_img}', \
            mer_type='{mer_type}', mer_slogan='{mer_slogan}', mer_logo='{mer_logo}', \
            mer_sales='{mer_sales}'".format(mer_address=self.params['mer_address'], \
            mer_name=self.params['mer_name'], mer_longitude=self.params['mer_longitude'], \
            mer_latitude=self.params['mer_latitude'],mer_img=self.params['mer_img'], \
            mer_type=self.params['mer_type'], mer_slogan=self.params['mer_slogan'], \
            mer_logo=self.params['mer_logo'], mer_sales=self.params['mer_sales'])
        print(sql)
        suc = mysql.insertOne(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        else:
            mysql.errdispose()
            return HttpResponse(0)

#编辑商家
class Edit_Merchant(View):

    def post(self, request):
        self.params = {}
        self.params['mer_id'] = int(request.POST.get('mer_id'))
        self.params['mer_address'] = request.POST.get('mer_address')
        self.params['mer_name'] = request.POST.get('mer_name')
        self.params['mer_slogan'] = request.POST.get('mer_slogan')
        self.params['mer_longitude'] = float(request.POST.get('mer_longitude')) #经度
        self.params['mer_latitude'] = float(request.POST.get('mer_latitude')) #纬度
        self.params['mer_img'] = request.POST.get('mer_img') #商户banner
        self.params['mer_type'] = int(request.POST.get('mer_type')) #属性1吃的2喝的3玩的
        self.params['mer_logo'] = request.POST.get('mer_logo') #商户头像 mer_logo
        self.params['mer_sales'] = float(request.POST.get('mer_sales')) #折扣 mer_sales 
        mysql = Mysql()
        sql = "UPDATE merchant SET mer_address='{mer_address}', mer_name='{mer_name}', \
            mer_longitude='{mer_longitude}', mer_latitude='{mer_latitude}',mer_img='{mer_img}', \
            mer_type='{mer_type}', mer_slogan='{mer_slogan}', mer_logo='{mer_logo}', \
            mer_sales='{mer_sales}' WHERE mer_id='{mer_id}'".format(mer_address=self.params['mer_address'], \
            mer_name=self.params['mer_name'], mer_longitude=self.params['mer_longitude'], \
            mer_latitude=self.params['mer_latitude'], mer_img=self.params['mer_img'], mer_type=self.params['mer_type'], \
            mer_id=self.params['mer_id'], mer_slogan=self.params['mer_slogan'], mer_logo=self.params['mer_logo'], \
            mer_sales=self.params['mer_sales'])
        print(sql)
        suc = mysql.update(sql)
        print(suc)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        else:
            mysql.errdispose()
            return HttpResponse(0)

#查询商家
class Sel_Merchant(View):

    def get(self, request):
        self.params = {}
        self.params['mer_name'] = request.GET.get('mer_name')
        self.params['row'] = int(request.GET.get('row'))
        self.params['page'] = int(request.GET.get('page'))
        mysql = Mysql()
        sql = "SELECT * FROM merchant WHERE mer_name like '%{mer_name}%'".format(mer_name=self.params['mer_name'])
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            sumpage, info = Pagings.paging(info, row=self.params['row'], page=self.params['page'])
            data = {}
            data['sumpage'] = sumpage
            data['info'] = info
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(data)
        return HttpResponse(0)

#删除商家
class Del_Merchant(View):

    def post(self, request):
        self.params = {}
        self.params['mer_id'] = request.POST.get('mer_id')
        mysql = Mysql()
        sql = "DELETE FROM merchant WHERE mer_id = '{mer_id}'".format(mer_id=self.params['mer_id'])
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#添加管理员
class Add_MerAdmin(View):
    
    def post(self, request):
        self.params = {}
        self.params['phone'] = request.POST.get('phone')
        self.params['user_name'] = request.POST.get('user_name') 
        self.params['password'] = request.POST.get('password') #可以随机生成密码
        self.params['mer_id'] = request.POST.get('mer_id') #商户id 必传
        mysql = Mysql()
        sql = "SELECT is_admin FROM mer_admin WHERE mer_id = '{mer_id}' AND phone ='{phone}' \
            AND is_admin = '1'".format(mer_id=self.params['mer_id'], phone=self.params['phone'])
        check = mysql.getOne(sql)
        sql = "SELECT is_admin FROM mer_admin WHERE phone ='{phone}'".format(phone=self.params['phone'])
        check_phone = mysql.getOne(sql)
        if check or check_phone:
            mysql.dispose()
            return HttpResponse(2)
        sql = "INSERT INTO mer_admin SET phone='{phone}', user_name='{user_name}',\
            `password`='{password}', is_admin='1', mer_id='{mer_id}'\
            ".format(phone=self.params['phone'],password=self.params['password'], \
            mer_id=self.params['mer_id'], user_name=self.params['user_name'])
        suc = mysql.insertOne(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#编辑管理员
class Edit_MerAdmin(View):
    
    def post(self, request):
        self.params = {}
        self.params['mer_userid'] = request.POST.get('mer_userid')
        self.params['user_name'] = request.POST.get('user_name')
        self.params['phone'] = request.POST.get('phone')
        self.params['password'] = request.POST.get('password') #可以随机生成密码
        mysql = Mysql()
        sql = "UPDATE mer_admin SET  user_name='{user_name}', phone = {phone}, \
            `password`='{password}' WHERE mer_userid='{mer_userid}'".format(\
            password=self.params['password'], phone =self.params['phone'], \
            mer_userid=self.params['mer_userid'],user_name=self.params['user_name'])
        print(sql)
        try:
            mysql.update(sql)
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            mysql.errdispose()
            return HttpResponse(0)

#查看管理员
class Sel_MerAdmin(View):
    
    def get(self, request):
        self.params = {}
        self.params['mer_id'] = request.GET.get('mer_id')
        self.params['row'] = int(request.GET.get('row'))
        self.params['page'] = int(request.GET.get('page'))
        mysql = Mysql()
        sql = "SELECT * FROM mer_admin WHERE mer_id = '{mer_id}'".format(mer_id=self.params['mer_id'])
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            sumpage, info = Pagings.paging(info, row=self.params['row'], page=self.params['page'])
            data = {}
            data['sumpage'] = sumpage
            data['info'] = info
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(data)
        return HttpResponse(0)

#删除管理员
class Del_MerAdmin(View):

    def post(self, request):
        self.params = {}
        self.params['mer_userid'] = request.POST.get('mer_userid')
        mysql = Mysql()
        sql = "DELETE FROM mer_admin WHERE mer_userid \
        = '{mer_userid}'".format(mer_userid=self.params['mer_userid'])
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)