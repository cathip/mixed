import json

from django.views import View
from django.utils.decorators import method_decorator
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.shop_base import returnJson, query

#首页大树（全员总投递量）
class Index(View):

    def post(self, request, **payload):
        sql = "SELECT SUM(wight) as wight FROM deliver"
        info = query(sql)
        return HttpResponse(returnJson(0, '查询成功', info))