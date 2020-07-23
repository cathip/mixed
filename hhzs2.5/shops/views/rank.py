import json

from django.views import View
from django.utils.decorators import method_decorator
from django.http import request, HttpResponse, JsonResponse

from base.cmysql import Mysql
from base.config import START_TIME, END_TIME
from base.shop_base import ComplexEncode, Pagings, query, returnJson


# 查看排行榜
class Rank(View):

    def post(self, request, **payload):
        self.params = {}
        self.params['start_time'] = request.POST.get('start_time')
        self.params['end_time'] = request.POST.get('end_time')
        self.params['is_school'] = int(request.POST.get('is_school'))  # 0个人 1学校
        if self.params['is_school'] == 0:
            sql = f'''SELECT \
                        SUM(d.wight) AS weight, \
                        u.id AS user_id, \
                        u.wxname, \
                        u.school_id, \
                        u.user_img, \
                        s.school_img \
                    FROM \
                        deliver AS d \
					    LEFT JOIN gzh_user AS g ON g.openid = d.openid \
                        LEFT JOIN userInfo AS u ON u.unionId = g.unionid \
                        LEFT JOIN school AS s ON u.school_id = s.id \
                    WHERE \
                    u.wxname IS NOT NULL \
                    AND g.openid NOT IN 
                    ('oLKbX1JCYRryfJsXPNvl69kNTXFU','oLKbX1BjDWpeyuVFPGzm9H7szvoo', \
                    'oLKbX1CXeWasiulsOR-_CeYnlprk', 'oLKbX1KuMDzJe2e46z0WyLAhkKHQ', \
                    'oLKbX1O-HV9pXabfE5BWB6jsMbQY', 'oICg44y-TQLpvENQFvVtTUEqXRT8',\
                    'oLKbX1Hc8lNNZmNNQcM0WhvbvnhM','oLKbX1OJgSIZrb2Hxi2nYRnRPpTQ',
                    'oLKbX1GgjlWc155Qk927f7hHhWv8') \
                    AND d.create_time \
                        BETWEEN '{START_TIME}' AND '{END_TIME}' \
                    GROUP BY \
                        d.openid \
                    ORDER BY \
                        weight DESC \
                    LIMIT 0, \
                    100'''
        else:
            sql = f'''SELECT \
                        SUM(d.wight) AS weight, \
                        u.id AS user_id, \
                        u.school_id, \
                        s.school_name, \
                        s.school_img \
                    FROM \
                        deliver AS d \
                        LEFT JOIN gzh_user AS g ON g.openid = d.openid \
                        LEFT JOIN userInfo AS u ON u.unionId = g.unionid \
                        LEFT JOIN school AS s ON u.school_id = s.id \
                    WHERE \
                    u.wxname IS NOT NULL \
                    AND u.school_id is NOT NULL \
                    AND d.create_time BETWEEN '{START_TIME}' AND '{END_TIME}' \
                    GROUP BY \
                        u.school_id \
                    ORDER BY \
                        weight DESC \
                    LIMIT 0, \
                    100'''
        info = query(sql)
        return HttpResponse(returnJson(0, '查询成功', info))

# 上周排行榜
class Last_Rank(View):

    def post(self, request, **payload):
        is_school = int(request.POST.get('is_school')) #0个人 1学校
        if is_school == 0:
            sql = "SELECT * FROM last_ranklist"
        else:
            sql = "SELECT * FROM last_school_ranklist"
        info = query(sql)
        return HttpResponse(returnJson(0, '查询成功', info))


# 更改排行榜对应规则
class Rank_Ruler(View):

    def post(self, request, **payload):
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        banner = request.POST.get('banner')
        ruler = request.POST.get('ruler')
        get_info = int(request.POST.get('get_info'))
        filename = "/home/ubuntu/hhsc2019/adminsApi/views/rank.json"
        if get_info == 1:
            with open(filename, 'r') as f:
                return HttpResponse(f.read())
        if get_info == 0:
            with open(filename, 'w') as f:
                json.dump({'start_time': start_time, 'end_time': end_time,
                           'banner': banner, 'ruler': ruler}, f)
            return HttpResponse(1)
        else:
            return HttpResponse("请输入get_info")

