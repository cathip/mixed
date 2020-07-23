import math

from django.views import View
from django.http import request, JsonResponse, HttpResponse

from base.shop_base import Pagings, callJson
from base.config import BOOK_ID
from base.cmysql import Mysql


#添加分类
class Addclass(View):
    
    def __init__(self):
        self.__reqData = {}

    def post(self, request):
        try:
            mysql = Mysql()
            self.__reqData['name'] = request.POST.get('name')
            self.__reqData['parent_id'] = request.POST.get('bigclass')
            self.__reqData['img'] = request.POST.get('img')
            self.__reqData['sort'] = request.POST.get('sort')
            sql = 'INSERT INTO proclass (`name`,parentId,img,sort) VALUES (%s, %s, %s, %s)'
            suc = mysql.insertOne(sql, param=[
                self.__reqData['name'],
                self.__reqData['parent_id'], 
                self.__reqData['img'],
                self.__reqData['sort']
            ])
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#删除分类
class DelClass(View):

    def post(self, request):
        del_id = request.POST.get('id')
        if int(del_id) == BOOK_ID:
            return HttpResponse(0) 
        mysql = Mysql()
        sql = "SELECT id FROM product WHERE productTypeId = %s"
        info_one = mysql.getOne(sql, param=[del_id])
        sql = "SELECT id FROM proclass WHERE parentId = %s"
        info_two = mysql.getOne(sql, param=[del_id])
        if info_one or info_two:
            return HttpResponse(2)
        else:
            sql = "DELETE FROM proclass WHERE id = %s"
            suc = mysql.delete(sql, param=[del_id])
            return HttpResponse(suc)

#获取子级分类（父级传0）
class Getclass(View):
    
    def get(self, request):
        parentid=request.GET.get('parentid')
        mysql = Mysql()
        sql = 'SELECT * FROM proclass WHERE parentId = %s'
        class_info = mysql.getAll(sql, param=[parentid])
        mysql.dispose()
        return HttpResponse(callJson(class_info))

#编辑分类
class Editclass(View):
    
    def __init__(self):
        self.__reqData = {}

    def post(self, request):
        try:
            mysql = Mysql()
            self.__reqData['name'] = request.POST.get('name')
            self.__reqData['id'] = request.POST.get('id')
            self.__reqData['img'] = request.POST.get('img', '')
            self.__reqData['parentId'] = request.POST.get('parentId')
            self.__reqData['sort'] = request.POST.get('sort')
            sql = 'update proclass set name=%s,parentId=%s, img=%s, sort=%s \
                where id = %s' 
            mysql.update(sql, param=[
                self.__reqData['name'],
                self.__reqData['parentId'],
                self.__reqData['img'],
                self.__reqData['sort'],
                self.__reqData['id']
            ])
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#管理分类列表
class GetClassList(View):

    def __init__(self):
        self.__reqData = {}

    def post(self, request):
        self.__reqData['name'] = request.POST.get('name', False)
        self.__reqData['row'] = request.POST.get('row')
        self.__reqData['page'] = request.POST.get('page')
        info = self.sel_class_list()
        if not info:
            return HttpResponse(0)
        pages, classes = Pagings.paging(
            info, self.__reqData['row'], self.__reqData['page']
        )
        data = {}
        data["pages"] = pages
        data['classes'] = classes
        return HttpResponse(callJson(data))

    def sel_class_list(self):
        mysql = Mysql()
        if self.__reqData['name']:
            sql = "SELECT * FROM proclass WHERE `name` LIKE '%{name}%'".format(name=self.__reqData['name'])
            info = mysql.getAll(sql)
        else:
            sql = "SELECT * FROM proclass"
        info = mysql.getAll(sql)
        for i in info:
            sql = "SELECT `name` FROM proclass WHERE id = %a"
            parent_name = mysql.getOne(sql, param=[i.get('parentId')])
            if parent_name:
                i['parentName'] = parent_name.get('name')
            else:
                i['parentName'] = None
        return info

#获取分类下的商品
class GetClassProduct(View):
    
    def get(self, request):
        pro_typeid = request.GET.get('class_id')
        page = request.GET.get('page')
        row = request.GET.get('row')

        mysql = Mysql()
        sql = "SELECT * FROM product WHERE productTypeId \
             = %s"
        info = mysql.getAll(sql, param=[pro_typeid])
        mysql.dispose()

        if info:
            page_count, info = Pagings.paging(info, row=row, page=page)
            data = {}
            data['page_count'] = page_count
            data['info'] = info
            return HttpResponse(callJson(data))
        return HttpResponse(0)