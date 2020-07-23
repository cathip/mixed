import datetime
import json
from django.http import request, JsonResponse, HttpResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import Pagings, ComplexEncode

#插入留言信息
class Add_Message(View):
    
    def __init__(self):
        pass

    def post(self, request):
        pass
    
    def post_params(self, request):
        pass

    def add_message(self):
        pass

#删除留言信息
class Del_Message(View):
    pass

#查询留言信息
class Sel_Message(View):
    pass

#编辑留言信息(已读 未读 备注)
class Edit_Message(View):
    pass