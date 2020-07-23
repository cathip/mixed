import datetime
import json
from django.http import request, JsonResponse, HttpResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import Pagings

#----------------------校区------------------------------

#增加校区
class Add_School_Area(View):

    def post(self, request):
        area_name = request.POST.get('area_name')
        mysql = Mysql()
        sql = "INSERT INTO school_area SET area_name = '{area_name}'".format(area_name=area_name)
        suc = mysql.insertOne(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#编辑校区
class Edit_School_Area(View):

    def post(self, request):
        area_name = request.POST.get('area_name')
        area_id = request.POST.get('area_id')
        mysql = Mysql()
        sql = "UPDATE school_area SET area_name='{area_name}' WHERE \
            id='{area_id}' ".format(area_name=area_name, area_id=area_id)
        try:
            mysql.update(sql)
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#删除校区
class Del_School_Area(View):

    def post(self, request):
        area_id = request.POST.get('area_id')
        mysql = Mysql()
        sql = "SELECT id FROM school WHERE area_id = '{area_id}'".format(area_id=area_id)
        info = mysql.getOne(sql)
        if info:
            mysql.dispose()
            return HttpResponse(2) #有学校绑定 要先删学校
        sql = "DELETE FROM school_area WHERE id='{area_id}'".format(area_id=area_id)
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#查看校区
class Sel_School_Area(View):

    def get(self, request):
        area_name = request.GET.get('area_name')
        row = request.GET.get('row')
        page = request.GET.get('page')
        area_id = request.GET.get('area_id')
        get_school = request.GET.get('get_school')
        mysql = Mysql()
        if int(get_school) == 0:
            sql = "SELECT * FROM school_area WHERE area_name like '%{area_name}%'".format(area_name=area_name)
        if int(get_school) == 1:
            sql = "SELECT * FROM school WHERE area_id = '{area_id}'".format(area_id=area_id)
        print(sql)
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
            

#----------------------学校----------------------------

#增加学校
class Add_School(View):
    
    def post(self, request):
        school_img = request.POST.get('school_img')
        english_name = request.POST.get('english_name')
        school_name = request.POST.get('school_name')
        school_motto = request.POST.get('school_motto')
        area_id = request.POST.get('area_id')
        mysql = Mysql()
        sql = "INSERT INTO school SET school_name='{school_name}', school_img='{school_img}', \
            english_name='{english_name}', school_motto='{school_motto}', area_id='{area_id}' \
            ".format(school_img=school_img, school_name=school_name, school_motto=school_motto, \
            area_id=area_id, english_name=english_name)
        suc = mysql.insertOne(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#删除学校
class Del_School(View):

    def post(self, request):
        school_id = request.POST.get('school_id')
        mysql = Mysql()
        sql = "SELECT * FROM userInfo WHERE school_id = '{school_id}'".format(school_id=school_id)
        info = mysql.getOne(sql)
        if info:
            mysql.dispose()
            return HttpResponse(2) #有学生绑定 要先删学生
        sql = "DELETE FROM school WHERE id = '{school_id}'".format(school_id=school_id)
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0) 

#编辑学校
class Edit_School(View):

    def post(self, request):
        school_id = request.POST.get('school_id')
        school_img = request.POST.get('school_img')
        english_name = request.POST.get('english_name')
        school_name = request.POST.get('school_name')
        school_motto = request.POST.get('school_motto')
        area_id = request.POST.get('area_id')
        mysql = Mysql()
        sql = "UPDATE school SET school_name='{school_name}', school_img='{school_img}', \
            english_name='{english_name}', school_motto='{school_motto}', area_id='{area_id}' WHERE id='{school_id}' \
            ".format(school_img=school_img, school_name=school_name, school_motto=school_motto, \
            area_id=area_id, english_name=english_name, school_id=school_id)
        try:
            mysql.update(sql)
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#查看学校
class Sel_School(View):

    def get(self, request):
        school_name = request.GET.get('school_name')
        row = request.GET.get('row')
        page = request.GET.get('page')
        mysql = Mysql()
        sql = "SELECT school.*, school_area.area_name FROM school LEFT JOIN school_area \
                ON school.area_id = school_area.id \
                WHERE school_name like '%{school_name}%'".format(school_name=school_name)
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            sumpage, info = Pagings.paging(info, row, page)
            data = {}
            data['sumpage'] = sumpage
            data['info'] = info
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)
            return HttpResponse(data)
        return HttpResponse(0)


#----------------------学校地址------------------------------

#增加学校地址
class Add_School_Address(View):
    
    def post(self, request):
        school_id = request.POST.get('school_id')
        address = str(request.POST.get('address'))
        mysql = Mysql()
        sql = "INSERT INTO school_address SET school_id='{school_id}', \
            address='{address}'".format(school_id=school_id, address=address)
        suc = mysql.insertOne(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#编辑学校地址
class Edit_School_Address(View):

    def post(self, request):
        address_id = request.POST.get('address_id')
        school_id = request.POST.get('school_id')
        address = request.POST.get('address')
        mysql = Mysql()
        sql = "UPDATE school_address SET school_id='{school_id}', \
            address='{address}' WHERE id='{address_id}'".format(school_id=school_id, address=address, address_id=address_id)
        try:
            mysql.update(sql)
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#删除学校地址
class Del_School_Address(View):
    
    def post(self, request):
        address_id = request.POST.get('address_id')
        mysql = Mysql()
        sql = "DELETE FROM school_address WHERE id = '{address_id}'".format(address_id=address_id)
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0) 

#根据学校查看地址
class Sel_School_Address(View):

    def get(self, request):
        school_id = request.GET.get('school_id')
        row = request.GET.get('row')
        page = request.GET.get('page')
        mysql = Mysql()
        sql = "SELECT * FROM school_address WHERE school_id = '{school_id}'".format(school_id=school_id)
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            sumpage, info = Pagings.paging(info, row, page)
            data = {}
            data['sumpage'] = sumpage
            data['info'] = info
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)
            return HttpResponse(data)
        return HttpResponse(0)