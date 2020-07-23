import jwt
from jwt import exceptions

from django.http import JsonResponse, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from hhsc2019.settings import SECRET_KEY
from base.shop_base import erroLog

class MD1(MiddlewareMixin):

    def __init__(self, get_response=None):
        super().__init__(get_response=get_response)
        #url白名单
        self.info = [
            '/shops/api/test/',
            '/shops/api/prologin/', 
            '/shops/api/getcode/',
            '/shops/api/getToken/',
            '/shops/api/wxdate/getOpenid',
            '/shops/api/wxdate/checkToken'
            '/adminsApi/api/login/', 
            '/adminsApi/api/store_login/',
            #-------微信回调------- 
            '/shops/api/wx_callback/',
            '/shops/api/mer_wxcallback/', 
            '/shops/api/merpay_wxcallback/',
        ]

    def process_request(self, request):
        next_url = request.path_info
        try:
            if next_url in self.info:
                pass
            else:
                self._token = request.META.get('HTTP_TOKEN')
                try:
                    self._payload = jwt.decode(self._token, SECRET_KEY, True)
                    # 生成的是byte类型，可转换为字符串
                except exceptions.ExpiredSignatureError:
                    print('token过期')
                    return JsonResponse({
                        'ret' : -7,
                        'msg' : 'token过期'
                    })
                except jwt.DecodeError:
                    print('token认证失效')
                    return JsonResponse({
                        'ret' : -8,
                        'msg' : 'token认证失效'
                    })
                except jwt.InvalidSignatureError:
                    print('非法token')
                    return JsonResponse({
                        'ret' : -9,
                        'msg' : '非法token'
                    })
        except Exception as e:
            print(e)
            return JsonResponse({
                'ret' : -10,
                'msg' : '网络繁忙'
            })

    def process_view(self, request, view_func, view_args, view_kwargs):
        #try:
        next_url = request.path_info
        if next_url in self.info:
            pass
        else:
            view_kwargs = {**view_kwargs, **self._payload}
            return view_func(request, **view_kwargs)
        # except Exception as e:
        #     print(e)
        #     erroLog(e)
        #     return JsonResponse({
        #         'ret' : -10,
        #         'msg' : '网络繁忙'
        #     })    