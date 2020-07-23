import json
import datetime

from django.views import View
from django.http import request, HttpResponse

from base.cmysql import Mysql

#增加banner
class Add_Banner(View):

    def __init__(self):
        self.__reqData = {}

    def post(self, request):
        self.post_params(request)
        suc = self.add_banner()
        return HttpResponse(suc)

    def post_params(self, request):
        self.__reqData['img_name'] = request.POST.get('img_name')
        self.__reqData['text'] = request.POST.get('text')
        self.__reqData['banner_type'] = request.POST.get('banner_type') #0详情 1跳转连接
        self.__reqData['banner_path'] = request.POST.get('banner_path') #banner对应的页面
        

    def add_banner(self):
        mysql = Mysql()
        sql = "INSERT INTO banner SET img=%s, text=%s, banner_type=%s, banner_path=%s"
        suc = mysql.insertOne(sql, param=[
            self.__reqData['img_name'],
            self.__reqData['text'],
            self.__reqData['banner_type'],
            self.__reqData['banner_path']
        ])
        if suc:
            mysql.dispose()
            return 1
        else:
            mysql.errdispose()
            print('-----插入图片失败-----')
            return 0

#删除banner
class Del_Banner(View):

    def post(self, request):
        try:
            self.__reqData = {}
            self.__reqData['img_id'] = request.POST.get('img_id')
            mysql = Mysql()
            sql = "DELETE FROM banner WHERE id = %s"
            suc = mysql.delete(sql, param=[self.__reqData['img_id']])
            mysql.dispose() 
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)
        
#编辑banner
class Edit_Banner(View):

    def __init__(self):
        self.__reqData = {} 
        
    def post(self, request):
        try:
            self.__reqData['img_name'] = request.POST.get('img_name')
            self.__reqData['text'] = request.POST.get('text')
            self.__reqData['img_id'] = request.POST.get('img_id')
            self.__reqData['banner_type'] = request.POST.get('banner_type')
            self.__reqData['banner_path'] = request.POST.get('banner_path')
            mysql = Mysql()
            sql = "UPDATE banner SET img = %s, text = %s, banner_type = %s, \
            banner_path = %s WHERE id = %s"
            mysql.update(sql, param=[
                self.__reqData['img_name'],
                self.__reqData['text'],
                self.__reqData['banner_type'],
                self.__reqData['banner_path'],
                self.__reqData['img_id']
            ])
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            mysql.errdispose()
            return HttpResponse(0)

#查询banner
class Sel_Banner(View):

    def get(self, request):
        banner_path = request.GET.get('banner_path')
        mysql = Mysql()
        sql = "SELECT *  FROM banner WHERE banner_path = %s ORDER BY banner_type"
        info = mysql.getAll(sql, param=[banner_path])
        mysql.dispose()
        info = json.dumps(info, ensure_ascii=False, sort_keys=True, indent=4)
        if info:
            return HttpResponse(info)
        return HttpResponse(0)
