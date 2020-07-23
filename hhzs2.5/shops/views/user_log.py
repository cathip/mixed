from django.views import View
from django.http import request, HttpResponse, JsonResponse

from base.shop_base import returnJson, query

'''
有关用户的一些操作以及消费记录
'''
#盒盒币记录
class UserLog(View):

    def __init__(self):
        self.info = {}

    def post(self, request, **payload):
        handle = payload.get('handle')
        state = payload.get('state')
        
        self.info['user_id'] = payload.get('user_id')
        self.info['area_id'] = request.POST.get('area_id')

        if handle == 'hhcoin':

            if state == 'obtain':
                sql = "SELECT * FROM coin_log WHERE userid = %s AND\
                    consumeType = '1' AND num != 0 ORDER BY handletime DESC"
                info = query(sql, param=[self.info['user_id']])
                return HttpResponse(0, '查询成功', info)

            if handle == 'consume':
                sql = "SELECT * FROM coin_log WHERE userid = %s AND \
                consumeType = '0' AND num != 0 ORDER BY handletime DESC"
                info = query(sql, param=[self.info['user_id']])
                return HttpResponse(0, '查询成功', info)

            if handle == 'all':
                sql = "SELECT * FROM coin_log WHERE userid = %s AND num != 0 \
                    ORDER BY handletime DESC"
                info = query(sql, param=[self.info['user_id']])
                return HttpResponse(0, '查询成功', info)

        if handle == 'allDelivery':
            return self.getDelivery()

        if handle == 'campusDelivery':
            return self.campus()

        return HttpResponse(-2, '非法路径')

    #全部投递
    def getDelivery(self):
        sql = "SELECT SUM(d.wight) as wight, sa.id, sa.area_name \
                    FROM deliver AS d \
                    LEFT JOIN gzh_user AS g ON d.openid = g.openid \
                    LEFT JOIN userInfo AS u ON g.unionid = u.unionId \
                    LEFT JOIN school AS s ON s.id = u.school_id \
                    LEFT JOIN school_area AS sa ON sa.id = s.area_id \
                    WHERE u.school_id IS NOT NULL GROUP BY sa.id "
        info = query(sql)
        return HttpResponse(returnJson(0, '查询成功', info))

    #校区投递记录
    def campus(self):
        sql = "SELECT SUM(d.wight) as wight, s.school_name \
                FROM deliver AS d \
                LEFT JOIN gzh_user AS g ON d.openid = g.openid \
                LEFT JOIN userInfo AS u ON g.unionid = u.unionId \
                LEFT JOIN school AS s ON s.id = u.school_id \
                LEFT JOIN school_area AS sa ON sa.id = s.area_id \
                WHERE u.school_id IS NOT NULL AND sa.id = %s GROUP BY u.school_id" 
        info = query(sql, self.info['area_id'])
        return HttpResponse(returnJson(0, '查询成功', info))