import json
from django.http import request, HttpResponse, JsonResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import query, returnJson

#查看所有机器
class Sel_Machine(View):

    def post(self, request, **payload):
        sql = "SELECT mchState, address, addremark, jd, wd, zhi_weight, shu_weight, `Repair` \
            FROM machine WHERE (jd AND wd) IS NOT NULL AND (jd AND wd) != ''"
        info = query(sql)
        return HttpResponse(returnJson(0, '查询成功', info))