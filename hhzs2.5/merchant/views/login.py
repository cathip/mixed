import json
from django.http import request, HttpResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Pagings

class Login(View):
    
    def post(self, request):
        self.params = {}
        self.params['phone'] = request.POST.get('phone')
        self.params['password'] = request.POST.get('password')
        self.params['openid'] = request.POST.get('openid')
        mysql = Mysql()
        sql = "SELECT * FROM mer_admin WHERE openid='{openid}'".format(openid=self.params['openid'])
        check_openid = mysql.getOne(sql)
        #如有openid 自动登陆
        if check_openid:
            print('有openid 自动登陆')
            data = {}
            data['msg'] = 'OK'
            data['login_type'] = 'openid'
            data['user_name'] = check_openid.get('user_name')
            data['is_admin'] = check_openid.get('is_admin')
            data['mer_id'] = check_openid.get('mer_id')
            sql = f"SELECT * FROM merchant WHERE mer_id = {check_openid.get('mer_id')}"
            print(sql)
            mer_info = mysql.getOne(sql)
            data['mer_name'] = mer_info.get('mer_name')
            data['mer_address'] = mer_info.get('mer_address')
            data['mer_img'] = mer_info.get('mer_img')
            data['mer_type'] = mer_info.get('mer_type')
            mysql.dispose()
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(data)
        sql = "SELECT * FROM mer_admin WHERE phone='{phone}' AND \
            `password`='{password}'".format(phone=self.params['phone'], password=self.params['password'])
        check_pwd = mysql.getOne(sql)
        #如果没有openid 检查账号密码 并且更新openid
        if check_pwd:
            data = {}
            if self.params['openid']:
                sql = "UPDATE mer_admin SET openid='{openid}' WHERE \
                    phone='{phone}' AND `password` ='{password}'".format(openid=self.params['openid'], \
                    phone=self.params['phone'], password=self.params['password'])
                print(sql)
                mysql.update(sql)
                data['up_openid'] = 'OK'
            else:
                data['up_openid'] = 'FAIL'
            data['msg'] = 'OK'
            data['login_type'] = 'phone'
            data['user_name'] = check_pwd.get('user_name')
            data['is_admin'] = check_pwd.get('is_admin')
            data['mer_id'] = check_pwd.get('mer_id')
            sql = f"SELECT * FROM merchant WHERE mer_id = {check_pwd.get('mer_id')}"
            mer_info = mysql.getOne(sql)
            data['mer_name'] = mer_info.get('mer_name')
            data['mer_address'] = mer_info.get('mer_address')
            data['mer_img'] = mer_info.get('mer_img')
            data['mer_type'] = mer_info.get('mer_type')
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            mysql.dispose()
            return HttpResponse(data)
        #账号密码错误
        mysql.dispose()
        data = {}
        data['msg'] = 'FAIL'
        data['erro_info'] = '账号或密码错误'
        data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
        return HttpResponse(data)