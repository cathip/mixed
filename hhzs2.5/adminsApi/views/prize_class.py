import json
from django.http import request, HttpResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import ComplexEncode

#增加奖品分类
class Add_Prizeclass(View):

    def post(self, request):
        class_name = request.POST.get('class_name')
        mysql = Mysql()
        sql = "INSERT INTO prize_class SET class_name = '{class_name}'".format(class_name=class_name)
        suc = mysql.insertOne(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#删除奖品分类
class Del_Prizeclass(View):

    def post(self, request):
        class_id = request.POST.get('class_id')
        mysql = Mysql()
        sql = "SELECT * FROM prize WHERE class_id='{class_id}''".format(class_id=class_id)
        info = mysql.getOne(sql)
        if info:
            mysql.dispose()
            return HttpResponse(2) #分类下有奖品 不能删
        sql = "DELETE FROM prize_class WHERE id = '{class_id}'".format(class_id=class_id)
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)
    
#编辑奖品分类
class Edit_Prizeclass(View):

    def post(self, request):
        class_id = request.POST.get('class_id')
        class_name = request.POST.get('class_name')
        mysql = Mysql()
        sql = "UPDATE prize_class SET class_name = '{class_name}' WHERE \
            id = '{class_id}'".format(class_name=class_name, class_id=class_id)
        try:
            mysql.update(sql)
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)
    
#查询奖品分类
class Sel_Prizeclass(View):

    def get(self, request):
        mysql = Mysql()
        sql = "SELECT * FROM prize_class"
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            info = json.dumps(info, ensure_ascii=False, sort_keys=True, indent=4)
            return HttpResponse(info)
        return HttpResponse(0)
    
#根据分类查询奖品
class Sel_Class_Prize(View):

    def get(self, request):
        class_id = request.POST.get('class_id')
        mysql = Mysql()
        sql = "SELECT * FROM prize WHERE class_id='{class_id}'".format(class_id=class_id)
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            info = json.dumps(info, ensure_ascii=False, sort_keys=True, indent=4)
            return HttpResponse(info)
        return HttpResponse(0)

#根据分类获取操作类型
class Sel_Class_Type(View):

    def get(self, request):
        class_id = request.GET.get('class_id')
        mysql = Mysql()
        sql = "SELECT prize_type_id, prize_type_name FROM \
            prize_type_class WHERE prize_class_id ='{class_id}'".format(class_id=class_id)
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            info = json.dumps(info, ensure_ascii=False, sort_keys=True, indent=4)
            return HttpResponse(info)
        return HttpResponse(0)
    