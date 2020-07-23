import datetime

from django.views import View
from django.utils.decorators import method_decorator
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.Predis import Open_Redis
from base.shop_base import callJson, query, erroLog, Type_Log
from base.star_sign_config import starSignLog, randomH5Patch, \
    STAR_SIGIN, NUMBER_DICT, starryMarketLog

class Share(View):

    def post(self, request):
        try:
            handle_type = request.POST.get('handle_type')
            unionid = request.POST.get('unionid')

            if handle_type == 'share':
                mysql = Mysql()
                sql = 'SELECT id as share_id FROM h5_user WHERE unionid = %s'
                share_info = mysql.getOne(sql, param=[unionid])
                if not share_info:
                    mysql.dispose()
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '公众号信息未授权'
                    })
                sql = 'SELECT * FROM gzh_user WHERE unionid = %s AND state = 1'
                gzh_info = mysql.getOne(sql, param=[unionid])
                if not gzh_info:
                    mysql.dispose()
                    return JsonResponse({
                        'ret' : -1,
                        'msg' : '未关注公众号'
                    })
                mysql.dispose()
                return JsonResponse({
                    'ret' : 0,
                    'msg' : '分享成功',
                    'result' : share_info
                })

            if handle_type == 'help':
                mysql = Mysql()
                share_id = request.POST.get('share_id')
                print(share_id)
                unionid = request.POST.get('unionid')
                sql = 'SELECT * FROM h5_user WHERE unionid = %s'
                user_info = mysql.getOne(sql, param=[unionid])
                if not share_id and not unionid:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '参错错误'
                    })
                if not user_info:
                    mysql.dispose()
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '助力者公众号信息未授权'
                    })
                sql = 'SELECT * FROM gzh_user WHERE unionid = %s AND state = 1'
                gzh_info = mysql.getOne(sql, param=[unionid])
                if not gzh_info:
                    mysql.dispose()
                    return JsonResponse({
                        'ret' : -1,
                        'msg' : '未关注公众号'
                    })
                sql = 'SELECT * FROM h5_user WHERE id = %s FOR UPDATE'
                share_info = mysql.getOne(sql, param=[share_id])
                sql = 'SELECT * FROM h5_help_log WHERE leader_unionid = %s AND help_unionid = %s'
                check = mysql.getOne(sql, param=[share_info.get('unionid'), unionid])
                if check or share_info.get('unionid') == unionid:
                    mysql.dispose()
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '已经助力, 请勿重复'
                    })
                sql = 'INSERT INTO h5_help_log SET leader_unionid = %s, help_unionid = %s'
                mysql.insertOne(sql, param=[share_info.get('unionid'), unionid])
                sql = 'UPDATE h5_user SET lucky_draw_times = lucky_draw_times + 1, \
                    help_times = help_times + 1 WHERE id = %s'
                mysql.update(sql, param=[share_id])
                sql = 'UPDATE h5_user SET lucky_draw_times = lucky_draw_times + 1 \
                    WHERE unionid = %s'
                mysql.update(sql, param=[unionid])
                mysql.dispose()
                return JsonResponse({
                    'ret' : 0,
                    'msg' : '助力成功'
                })

            return JsonResponse({
                'ret' : -2,
                'msg' : '参数错误'
            })
            
        except Exception as e:
            erroLog(e)
            return JsonResponse({
                'ret' : -2,
                'msg' : '网络错误'
            })

    def get(self, request):
        try:
            unionid = request.GET.get('unionid')
            if not unionid:
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '缺少参数'
                })
            mysql = Mysql()
            sql = 'SELECT * FROM h5_user WHERE unionid = %s'
            share_info = mysql.getOne(sql, param=[unionid])
            if not share_info:
                mysql.dispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '公众号信息未授权'
                })
            # sql = 'SELECT id FROM userInfo WHERE unionId = %s'
            # user_id = mysql.getOne(sql, param=[unionid])
            # if not user_id:
            #     mysql.dispose()
            #     return JsonResponse({
            #         'ret' : -2,
            #         'msg' : '小程序信息未授权'
            #     })
            user_id = user_id.get('id')
            sql = 'SELECT one, two, three, four, five, six, seven, \
                eight, nine, ten, eleven, twelve \
                FROM user_star_sign WHERE user_id = %s'
            patch_info = mysql.getOne(sql, param=[user_id])
            sql = "SELECT hu.nickname,  hu.headimgurl \
                    FROM h5_help_log AS hl \
                    LEFT JOIN h5_user AS hu ON hl.help_unionid = hu.unionid \
                    WHERE leader_unionid = %s"
            helpuser_info = mysql.getAll(sql, param=[unionid])
            mysql.dispose()
            data = {
                'ret' : 0,
                'msg' : '查询成功',
                'resule' : {
                    'patch_info' : patch_info,
                    'help_user' : helpuser_info,
                    'lucky_draw_times' : share_info.get('lucky_draw_times')
                }
            }
            return JsonResponse(data)

        except Exception as e:
            erroLog(e)
            mysql.errdispose()
            return JsonResponse({
                'ret' : -2,
                'msg' : '网络错误'
            })
            

#抽奖
class H5LuckyDraw(View):

    def __init__(self):
        now = datetime.datetime.now()
        self.START_TIME = now -  datetime.timedelta(hours=now.hour,
        minutes=now.minute,
        seconds=now.second, 
        microseconds=now.microsecond) + datetime.timedelta(hours=4)
        self.END_TIME = now -  datetime.timedelta(hours=now.hour,
        minutes=now.minute,
        seconds=now.second, 
        microseconds=now.microsecond) + datetime.timedelta(days=1, hours=4)

    def post(self, request):
        try:
            unionid = request.POST.get('unionid')
            position = request.POST.get('position')
            mysql = Mysql()
            sql = "SELECT * FROM h5_user WHERE unionid = %s FOR UPDATE"
            user_info = mysql.getOne(sql, param=[unionid])
            if not user_info:
                mysql.dispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '无用户信息'
                })
            sql = 'SELECT * FROM gzh_user WHERE unionid = %s AND state = 1'
            gzh_info = mysql.getOne(sql, param=[unionid])
            if not gzh_info:
                mysql.dispose()
                return JsonResponse({
                    'ret' : -1,
                    'msg' : '未关注公众号'
                })
            sql = "SELECT COUNT(*) AS numbers FROM h5_luckdraw_log \
                WHERE unionid = %s AND create_time BETWEEN %s AND %s"
            numbers = mysql.getOne(sql, param=[unionid, self.START_TIME, self.END_TIME])
            if numbers:
                if numbers.get('numbers') >= 12:
                    mysql.dispose()
                    return JsonResponse({
                    'ret' : -2,
                    'msg' : '当日抽奖次数达到上限'
                })
            if user_info.get('lucky_draw_times') < 1:
                mysql.dispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '抽奖次数不足'
                })
            sql = 'SELECT * FROM h5_luckdraw_log WHERE unionid = %s \
            AND position = %s AND create_time BETWEEN %s AND %s'
            luckdraw_postion = mysql.getOne(sql, param=[unionid, position, self.START_TIME, self.END_TIME])
            if luckdraw_postion:
                mysql.dispose()
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '网络繁忙'
                })
            sql = "UPDATE h5_user SET lucky_draw_times = \
                lucky_draw_times - 1 WHERE unionid = %s"
            mysql.update(sql, param=[unionid])
            patch_id = randomH5Patch()
            sql = "INSERT INTO h5_luckdraw_log SET unionid = %s, \
                patch_id = %s, state = 0, position=%s"
            mysql.insertOne(sql, param=[unionid, patch_id, position])
            mysql.dispose()
            return JsonResponse({
                'ret' : 0,
                'msg' : '抽奖成功',
                'result' : {
                    'patch_id' : patch_id,
                    'patch_name' : STAR_SIGIN[patch_id]
                }
            })
        except Exception as e:
            mysql.errdispose()
            erroLog(e)
            return JsonResponse({
                'ret' : -2,
                'msg' : '网络错误'
            })

    def get(self, request):
        unionid = request.GET.get('unionid')
        sql = 'SELECT * FROM h5_luckdraw_log WHERE unionid = %s \
            AND create_time BETWEEN %s AND %s'
        data = query(sql, param=[unionid, self.START_TIME, self.END_TIME])
        return HttpResponse(callJson(data))

        
class Test(View):

    def get(self, request):
        try:
            qqq = 1
            zzz
            return HttpResponse(1)
        except Exception as e:
            erroLog(e)
            return HttpResponse(1)
        