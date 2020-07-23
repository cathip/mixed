import requests
import json
from django.http import request, HttpResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Pagings

#获取openid
class Get_Openid(View):

    def get(self, request):
        appid = 'wx9bd2c0f581998530'
        #secret = '44ba22700e0db2d12d053d04bb3fbec8' 
        secret = 'd501dd5c2afa2165afb8907e45d68c97'
        jscode = request.GET.get('jscode')
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={js_code}&grant_type=authorization_code'
        full_url = url.format(appid=appid, secret=secret, js_code=jscode)
        # 1.请求微信小程序的接口，获取返回的值
        response = requests.get(full_url).text
        # res_data = json.loads(response)  # 把json格式的转成python类型的数据
        print("res_data:", response)
        # openid = res_data.get('openid')
        # session_key = res_data.get('session_key')
        return HttpResponse(response)