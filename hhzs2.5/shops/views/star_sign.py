import datetime

from django.views import View
from django.utils.decorators import method_decorator
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.shop_base import callJson, query, erroLog, Type_Log
from base.star_sign_config import starSignLog, getPatch, randomPath, \
    STAR_SIGIN, NUMBER_DICT, starryMarketLog, randomWxPatch, PATCH_SELL_MONEY



START_TIME = '2019-12-08 00:00:00'
END_TIME = '2019-12-17 17:00:00'

#查看我的碎片
class SelMyPatch(View):

    def get(self, request, **payload):
        try:
            user_id = payload.get('user_id')
            mysql = Mysql()
            data = {}
            sql = "SELECT * FROM user_star_sign WHERE user_id = %s"
            result = mysql.getAll(sql, param=[user_id])
            data = {'ret' : 0, 'result': result}
            if not result:
                sql = "INSERT INTO user_star_sign SET user_id = %s "
                mysql.insertOne(sql, param=[user_id])
                sql = "SELECT * FROM user_star_sign WHERE user_id = %s"
                info = mysql.getAll(sql, param=[user_id])
                data = {'ret' : 0, 'msg': '查询成功', 'result': info}

            sql = "SELECT unionId FROM userInfo WHERE id = %s"
            user_info = mysql.getOne(sql, param=[user_id])
            if user_info.get('unionId'):
                sql = "SELECT * FROM h5_luckdraw_log WHERE unionid = %s AND state = 0"
                luckdraw_log = mysql.getAll(sql, param=[user_info.get('unionId')])
                if luckdraw_log:
                    patch_list = []
                    for i in luckdraw_log:
                        patch_list.append(i.get('patch_id'))
                        sql = 'UPDATE h5_luckdraw_log SET state = 1 WHERE id = %s'
                        mysql.update(sql, param=[i.get('id')])
                    getPatch(user_id, patch_list, 3, 1, mysql)
                    data['msg'] = '查询成功 碎片领取成功'
                    sql = "SELECT * FROM user_star_sign WHERE user_id = %s"
                    info = mysql.getAll(sql, param=[user_id])
                    data['result'] = info
                else:
                    data['msg'] = '查询成功 无碎片领取'
            else:
                data['ret'] = -1
                data['msg'] = '查询成功 但未绑定unionid 可能会导致h5抽奖碎片领取失败'
            mysql.dispose()
            return HttpResponse(callJson(data))
        except Exception as e:
            print(e)
            mysql.errdispose()
            erroLog(e)
            return JsonResponse({
                'ret' : -2,
                'msg' : '网络错误'
            })
            
#查看碎片日志
class SelPatchLog(View):

    def get(self, request, **payload):
        user_id = payload.get('user_id')
        sql = "SELECT * FROM star_sign_log WHERE user_id = %s"
        data = query(sql, param=[user_id])
        return HttpResponse(callJson(data))

#完成任务获取碎片
class MissionPatch(View):

    def post(self, request, **payload):
        try:
            user_id = payload.get('user_id')
            handle_type = request.POST.get('handle_type')
            mysql = Mysql()

            if handle_type == 'mobile':
                sql = "SELECT mobile FROM userInfo WHERE id = %s"
                check = mysql.getOne(sql, param=[user_id])
                mysql.dispose()
                if not check:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '请绑定手机号'
                    })
                state = starSignLog(user_id, 4)
                if state:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '已经领取'
                    })
                path_type = randomPath()
                path_type = [path_type]
                suc = getPatch(user_id, path_type, 4, 1)
                return JsonResponse(suc)

            if handle_type == 'school':
                sql = "SELECT school_id FROM userInfo WHERE id = %s"
                check = mysql.getOne(sql, param=[user_id])
                mysql.dispose()
                if not check:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '请绑定校徽'
                    })
                state = starSignLog(user_id, 5)
                if state:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '已经领取'
                    })
                path_type = randomPath()
                path_type = [path_type]
                suc = getPatch(user_id, path_type, 5, 1)
                return JsonResponse(suc)

            if handle_type == 'step':
                sql = "SELECT * FROM coin_log WHERE userid = %s AND handleType = 3 \
                    AND handletime BETWEEN %s AND %s"
                check = mysql.getOne(sql, param=[user_id, START_TIME, END_TIME])
                mysql.dispose()
                if not check:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '未进行过微信步数'
                    })
                state = starSignLog(user_id, 6)
                if state:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '已经领取'
                    })
                path_type = randomPath()
                path_type = [path_type]
                suc = getPatch(user_id, path_type, 6, 1)
                return JsonResponse(suc)

            if handle_type == 'answer':
                sql = "SELECT * FROM quiz_log WHERE user_id = %s \
                    AND create_time BETWEEN %s AND %s"
                check = mysql.getOne(sql, param=[user_id, START_TIME, END_TIME])
                mysql.dispose()
                if not check:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '未进行过每日一答'
                    })
                state = starSignLog(user_id, 7)
                if state:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '已经领取'
                    })
                path_type = randomPath()
                path_type = [path_type]
                suc = getPatch(user_id, path_type, 7, 1)
                return JsonResponse(suc)

            if handle_type == 'click_card':
                sql = "SELECT * FROM click_card WHERE userid = %s \
                    AND checkTime BETWEEN %s AND %s"
                check = mysql.getOne(sql, param=[user_id, START_TIME, END_TIME])
                mysql.dispose()
                if not check:
                    return JsonResponse({
                            'ret' : -2,
                            'msg' : '未进行过打卡'
                        })
                state = starSignLog(user_id, 8)
                if state:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '已经领取'
                    })
                path_type = randomPath()
                path_type = [path_type]
                suc = getPatch(user_id, path_type, 8, 1)
                return JsonResponse(suc)

            if handle_type == 'see':
                '''
                0未进行
                1已进行未领取
                2已领取
                '''
                sql = 'SELECT mobile, school_id FROM userInfo WHERE id = %s'
                user_info = mysql.getOne(sql, param=[user_id])
                check_mobile = 1 if user_info.get('mobile') else 0
                check_school = 1 if user_info.get('school_id') else 0

                sql = 'SELECT id FROM coin_log WHERE userid = %s AND handleType = 3 \
                    AND handletime BETWEEN %s AND %s'
                check_step = mysql.getOne(sql, param=[user_id, START_TIME, END_TIME])
                check_step = 1 if check_step else 0

                sql = 'SELECT id FROM quiz_log WHERE user_id = %s \
                    AND create_time BETWEEN %s AND %s'
                check_answer = mysql.getOne(sql, param=[user_id, START_TIME, END_TIME])
                check_answer = 1 if check_answer else 0

                sql = "SELECT id FROM click_card WHERE userid = %s \
                    AND checkTime BETWEEN %s AND %s"
                check_click_card = mysql.getOne(sql, param=[user_id, START_TIME, END_TIME])
                check_click_card = 1 if check_click_card else 0

                sql = "SELECT id FROM star_sign_log WHERE user_id = %s AND handle_type = %s"
                log_info = mysql.getOne(sql, param=[user_id, 4])
                check_mobile = 2 if log_info else check_mobile

                sql = "SELECT id FROM star_sign_log WHERE user_id = %s AND handle_type = %s"
                log_info = mysql.getOne(sql, param=[user_id, 5])
                check_school = 2 if log_info else check_school

                sql = "SELECT id FROM star_sign_log WHERE user_id = %s AND handle_type = %s"
                log_info = mysql.getOne(sql, param=[user_id, 6])

                check_step = 2 if log_info else check_step

                sql = "SELECT id FROM star_sign_log WHERE user_id = %s AND handle_type = %s"
                log_info = mysql.getOne(sql, param=[user_id, 7])
                check_answer = 2 if log_info else check_answer

                sql = "SELECT id FROM star_sign_log WHERE user_id = %s AND handle_type = %s"
                log_info = mysql.getOne(sql, param=[user_id, 8])
                check_click_card = 2 if log_info else check_click_card
                mysql.dispose()

                data = {
                    'ret' : 0,
                    'msg' : '查询成功',
                    'result' : {
                        'mobile' : check_mobile,
                        'school' : check_school,
                        'step' : check_step,
                        'answer' : check_answer,
                        'click_card' : check_click_card
                    }
                }
                return JsonResponse(data)

            mysql.dispose()
            return JsonResponse({
                'ret' : -2,
                'msg' : '参数错误'
            })
        except Exception as e:
            mysql.errdispose()
            erroLog(e)
            return JsonResponse({
                'ret' : -2,
                'msg' : '网络错误'
            })

#完成集碎片(未完成)
class Finish(View):
    
    def post(self, request, **payload):
        try:
            user_id = payload.get('user_id')
            address = request.POST.get('address')
            handle_type = request.POST.get('handle_type')
            if handle_type == 'finish':
                if not address:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '地址数据为空'
                    })
                mysql = Mysql()
                sql = "SELECT * FROM user_star_sign WHERE user_id = %s FOR UPDATE"
                mysql.getOne(sql, param=[user_id])
                sql = "SELECT * FROM user_star_sign WHERE \
                        user_id = %s \
                        AND one > 0 \
                        AND two > 0 \
                        AND three > 0 \
                        AND four > 0 \
                        AND five > 0 \
                        AND six > 0 \
                        AND seven > 0 \
                        AND eight > 0 \
                        AND nine > 0 \
                        AND ten > 0 \
                        AND eleven > 0 \
                        AND twelve > 0 \
                        AND state = 0"
                check = mysql.getOne(sql, param=[user_id])
                if not check:
                    mysql.dispose()
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '碎片不足或已被领取'
                    })
                sql = "UPDATE user_star_sign SET address = %s, \
                    state = 1 WHERE user_id = %s"
                mysql.update(sql, param=[address, user_id])
                patch_type = [i for i in range(1, 13)]
                getPatch(user_id, patch_type, 11, 0, mysql)
                mysql.dispose()
                return JsonResponse({
                    'ret' : 0,
                    'msg' : '领取成功'
                })
            if handle_type == 'update':
                mysql = Mysql()
                sql = "SELECT * FROM user_star_sign WHERE state = 1 \
                    AND user_id = %s FOR UPDATE"
                user_info = mysql.getOne(sql, param=[user_id])
                if not user_info:
                    mysql.dispose()
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '网络繁忙'
                    })
                sql = "UPDATE user_star_sign SET address = %s \
                    WHERE user_id = %s AND state = 1"
                mysql.update(sql, param=[address, user_id])
                mysql.dispose()
                return JsonResponse({
                    'ret' : 0,
                    'msg' : '领取成功'
                })
            return JsonResponse({
                    'ret' : -2,
                    'msg' : '参数错误'
                })

        except Exception as e:
            mysql.errdispose()
            erroLog(e)
            return JsonResponse({
                'ret' : -2,
                'msg' : '网络错误'
            })

#小程序抽奖获取
class Luck_Draw(View):

    def post(self, request, **payload):
        try:
            user_id = request.session.get('user_id')
            handle_type = request.POST.get('handle_type')

            if handle_type == 'one':
                mysql = Mysql()
                sql = "SELECT * FROM userInfo WHERE id = %s FOR UPDATE"
                user_info = mysql.getOne(sql, param=[user_id])
                if user_info.get('hhcoin') < 50:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '盒盒币不足'
                    })
                up_sql, log_sql = Type_Log.coin_handle(user_id, 14, 50, 0)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
                #抽碎片
                path_type = randomWxPatch()
                if isinstance(path_type, dict):
                    self.addHhcoin(user_id, [path_type.get('hhcoin')], mysql)
                    mysql.dispose()
                    return JsonResponse({
                        'ret' : 0,
                        'msg' : f"抽中盒盒币{path_type.get('hhcoin')}个",
                        'result' : {
                            'patch' : [],
                            'hhcoin' : [path_type.get('hhcoin')]
                        }
                    })
                getPatch(user_id, [path_type], 9, 1, mysql)
                mysql.dispose()
                data = {
                    'ret' : 0,
                    'msg' : f'抽奖成功, 获得了{STAR_SIGIN[path_type]}',
                    'result' : {
                        'patch' : [path_type],
                        'hhcoin' : []
                    }
                }
                return JsonResponse(data)

            if handle_type == 'ten':
                mysql = Mysql()
                sql = "SELECT * FROM userInfo WHERE id = %s FOR UPDATE"
                user_info = mysql.getOne(sql, param=[user_id])
                if user_info.get('hhcoin') < 450:
                    mysql.dispose()
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '盒盒币不足'
                    })
                up_sql, log_sql = Type_Log.coin_handle(user_id, 14, 450, 0)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
                #抽碎片
                result = list(map(randomWxPatch, [i for i in range(10)]))
                patch_list = list(filter(lambda x : isinstance(x, int), result))
                hhcoin_list = [x.get('hhcoin') for x in result if x not in patch_list]
                self.addHhcoin(user_id, hhcoin_list, mysql)
                getPatch(user_id, patch_list, 9, 1, mysql)
                mysql.dispose()
                data = {
                    'ret' : 0,
                    'msg' : '抽奖成功',
                    'result' : {
                        'patch' : patch_list,
                        'hhcoin' : hhcoin_list
                    }
                }
                return JsonResponse(data)

            if handle_type == 'log':
                mysql = Mysql()
                sql = "SELECT star_sign_id, create_time FROM star_sign_log \
                    WHERE user_id = %s AND handle_type = 9"
                patch_info = mysql.getAll(sql, param=[user_id])
                sql = "SELECT num, handletime FROM coin_log WHERE userid = %s \
                    AND handleType = 14 AND consumeType = 1"
                hhcoin_info = mysql.getAll(sql, param=[user_id])
                mysql.dispose()
                data = {
                    'ret' : 0,
                    'msg' : '查询成功',
                    'result' : {
                        'patch_info' : patch_info,
                        'hhcoin_info' : hhcoin_info
                    }
                }
                return HttpResponse(callJson(data))

            else:
                return JsonResponse({
                    'ret' : -2,
                    'msg' : '参数错误'
                })
        except Exception as e:
            mysql.errdispose()
            erroLog(e)
            return JsonResponse({
                    'ret' : -2,
                    'msg' : '网络错误'
                })

    def addHhcoin(self, user_id, num, mysql):
        if isinstance(num, list):
            if len(num) == 0:
                return
            for i in num:
                up_sql, log_sql = Type_Log.coin_handle(user_id, 14, i, 1)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
            return
        else:
            raise Exception('470行增加盒盒币错误')

#星空市场
class StarryMarket(View):

    def post(self, request, **payload):
        try:
            user_id = payload.get('user_id')
            handle_type = request.POST.get('handle_type')
            #查看
            if handle_type == 'see':
                sql = "SELECT * FROM starry_market"
                data = query(sql)
                return HttpResponse(callJson(data))
            #购买
            if handle_type == 'buy':
                patch_id = int(request.POST.get('patch_id'))
                mysql = Mysql()
                sql = "SELECT * FROM starry_market WHERE id = %s FOR UPDATE"
                path_info = mysql.getOne(sql, param=[patch_id])
                if path_info.get('number') <= 0:
                    mysql.dispose()
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '商品数量不足'
                    })
                need_hhcoin = path_info.get('hhcoin')
                sql = "SELECT * FROM userInfo WHERE id = %s FOR UPDATE"
                user_info = mysql.getOne(sql, param=[user_id])
                if user_info.get('hhcoin') < need_hhcoin:
                    mysql.dispose()
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '盒盒币不足'
                    })
                up_sql, log_sql = Type_Log.coin_handle(user_id, 15, need_hhcoin, 0)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
                up_sql, log_sql = starryMarketLog(user_id, patch_id, NUMBER_DICT[patch_id], need_hhcoin, 0, 1, mysql)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
                mysql.dispose()
                getPatch(user_id, [patch_id], 10, 1)
                return JsonResponse({
                    'ret' : 0,
                    'msg' : '购买成功'
                })
            #出售
            if handle_type == 'sell':
                patch_id = int(request.POST.get('patch_id'))
                numbes = int(request.POST.get('numbes'))
                print('patchid')
                print(patch_id)
                print('出售数量')
                print(numbes)
                if numbes <= 0:
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '网络繁忙'
                    })
                mysql = Mysql()
                sql = "SELECT * FROM starry_market WHERE id = %s FOR UPDATE"
                path_info = mysql.getOne(sql, param=[patch_id])
                sql = f"SELECT * FROM user_star_sign WHERE {NUMBER_DICT[patch_id]} >= {numbes} AND user_id = {user_id}"
                user_path = mysql.getOne(sql)
                if not user_path:
                    mysql.dispose()
                    return JsonResponse({
                        'ret' : -2,
                        'msg' : '用户碎片不足'
                    })
                sql = "SELECT * FROM userInfo WHERE id = %s FOR UPDATE"
                user_info = mysql.getOne(sql, param=[user_id])
                up_sql, log_sql = Type_Log.coin_handle(user_id, 15, PATCH_SELL_MONEY[patch_id], 1)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
                up_sql, log_sql = starryMarketLog(user_id, patch_id, NUMBER_DICT[patch_id], PATCH_SELL_MONEY[patch_id], 1, numbes, mysql)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
                mysql.dispose()
                getPatch(user_id, [patch_id], 10, 0)
                return JsonResponse({
                    'ret' : 0,
                    'msg' : '出售成功'
                })
            #查看日志
            if handle_type == 'log':
                sql = "SELECT * FROM starry_market_log WHERE user_id = %s"
                data = query(sql, param=[user_id])
                return HttpResponse(callJson(data))

        except Exception as e:
            erroLog(e)
            return JsonResponse({
                'ret' : -2,
                'msg' : '网络错误'
            })

# class Test(View):

#     def get(self, request):
#         mysql = Mysql()
#         for k, v in STAR_SIGIN.items():
#             sql = f"INSERT INTO starry_market SET id = '{k}', path_name = '{v}', price = 10"
#             mysql.insertOne(sql)
#         mysql.dispose()
#         return HttpResponse(1)
class StarryData(View):

    def get(self, request, **payload):
        mysql = Mysql()
        data = {}
        sql = 'SELECT \
                    COUNT(*) AS c \
                FROM \
                    user_star_sign \
                WHERE \
                    one > 0 \
                AND two > 0 \
                AND three > 0 \
                AND four > 0 \
                AND five > 0 \
                AND six > 0 \
                AND seven > 0 \
                AND eight > 0 \
                AND nine > 0 \
                AND ten > 0 \
                AND eleven > 0 \
                AND twelve > 0'
        finish = mysql.getOne(sql)
        sql = 'SELECT COUNT(*) AS c FROM user_star_sign WHERE state = 1'
        finish1 = mysql.getOne(sql)
        sql = 'SELECT *  FROM user_star_sign'
        userinfo = mysql.getAll(sql)
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        list5 = []
        list6 = []
        list7 = []
        list8 = []
        list9 = []
        list10 = []
        list11 = []
        for i in userinfo:
            sql = 'SELECT COUNT(*) AS c FROM (SELECT * FROM star_sign_log WHERE user_id = %s \
                AND consume_type = 1 GROUP BY star_sign_id) AS s'
            user_numbs = mysql.getOne(sql, param=(i.get('user_id')))
            print(user_numbs.get('c'))
            if user_numbs.get('c') >= 11:
                list11.append(user_numbs.get('c'))
            if user_numbs.get('c') >= 10:
                list10.append(user_numbs.get('c'))
            if user_numbs.get('c') >= 9:
                list9.append(user_numbs.get('c'))
            if user_numbs.get('c') >= 8:
                list8.append(user_numbs.get('c'))
            if user_numbs.get('c') >= 7:
                list7.append(user_numbs.get('c'))
            if user_numbs.get('c') >= 6:
                list6.append(user_numbs.get('c'))
            if user_numbs.get('c') >= 5:
                list5.append(user_numbs.get('c'))
            if user_numbs.get('c') >= 4:
                list4.append(user_numbs.get('c'))
            if user_numbs.get('c') >= 3:
                list3.append(user_numbs.get('c'))
            if user_numbs.get('c') >= 2:
                list2.append(user_numbs.get('c'))
            if user_numbs.get('c') >= 1:
                list1.append(user_numbs.get('c'))

        mysql.dispose()
        data = {
            '用户收集满12星座' : finish.get('c') + finish1.get('c'),
            '用户收集11个以上星座' : len(list11),
            '用户收集10个以上星座' : len(list10),
            '用户收集9个以上星座' : len(list9),
            '用户收集8个以上星座' : len(list8),
            '用户收集7个以上星座' : len(list7),
            '用户收集6个以上星座' : len(list6),
            '用户收集5个以上星座' : len(list5),
            '用户收集4个以上星座' : len(list4),
            '用户收集3个以上星座' : len(list3),
            '用户收集2个以上星座' : len(list2),
            '用户收集1个以上星座' : len(list1),
            '用户参与活动人数' : len(userinfo)
        }
        return JsonResponse(data)






