import json

from django.views import View
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.shop_base import returnJson, query

#获取banner
class Banner(View):

    def post(self, request, **payload):
        banner_path = request.POST.get('banner_path')
        sql = "SELECT * FROM banner WHERE banner_path = %s"
        info = query(sql, param=[banner_path])
        return HttpResponse(returnJson(0, '查询成功', info))