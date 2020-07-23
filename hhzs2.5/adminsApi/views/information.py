from django.shortcuts import render
from django.views import View
from django.http import request, HttpResponse, JsonResponse
from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Pagings
import json
import html

#增加资讯
class Add_Details(View):

    def post(self, request):
        banner = request.POST.get('banner')
        title = request.POST.get('title')
        details = html.escape(request.POST.get('details'))
        profile = request.POST.get('profile')
        mysql = Mysql()
        sql = f"INSERT INTO information SET banner='{banner}', \
            title='{title}', details='{details}', profile='{profile}'"
        suc = mysql.insertOne(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#删除资讯
class Del_Details(View):

    def post(self, request):
        news_id = request.POST.get('news_id')
        mysql = Mysql()
        sql = f"DELETE FROM information WHERE id = {news_id}"
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#编辑资讯
class Edit_Details(View):

    def post(self, request):
        banner = request.POST.get('banner')
        title = request.POST.get('title')
        details = html.escape(request.POST.get('details'))
        news_id = request.POST.get('news_id')
        profile = request.POST.get('profile')
        mysql = Mysql()
        sql = f"UPDATE information SET banner='{banner}', profile='{profile}', \
            title='{title}', details='{details}' WHERE id = {news_id}"
        suc = mysql.update(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#查看资讯
class Sel_Details(View):

    def get(self, request):
        title = request.GET.get('title')
        news_id = request.GET.get('news_id')
        row = request.GET.get('row')
        page = request.GET.get('page')
        mysql = Mysql()
        if news_id:
            sql = f"SELECT * FROM information WHERE title LIKE '%{title}%' ORDER BY create_time DESC "
            info = mysql.getAll(sql)
            mysql.dispose()
            if info:
                for i in info:
                    i['details'] = html.unescape(i.get('details'))
                sum_page, info = Pagings.paging(info, row=row, page=page)
                data = {}
                data['sum_page'] = sum_page
                data['info'] = info
                data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
                return HttpResponse(data)
            return HttpResponse(0)
        else:
            print('id形式')
            sql = f"SELECT * FROM information WHERE id = '{news_id}'"
            info = mysql.getOne(sql)
            info['details'] = html.unescape(info.get('details'))
            mysql.dispose()
            if info:
                info = json.dumps(info, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
                return HttpResponse(info)
            else:
                return HttpResponse(0)