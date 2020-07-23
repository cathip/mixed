import json
import random
import datetime

from django.views import View
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.http import request, JsonResponse, HttpResponse

from base.cmysql import Mysql
from base.shop_base import Type_Log, ComplexEncode, callJson, returnJson




# 查看题目（每日一答）
class Daily_Quiz(View):

    def __init__(self):
        self.info = {}

    def post(self, request, **payload):
        handle = payload.get('handle')
        self.info['user_id'] = payload.get('user_id')
        self.info['quiz_id'] = request.POST.get('quiz_id')
        self.info['answer_id'] = request.POST.get('answer_id')

        if handle == 'see':
            return self.see()

        if handle == 'do':
            return self.do()

        return HttpResponse(returnJson(-2, '非法路径'))

    def see(self):
        cache_name = str(self.info['user_id']) + 'daily_quiz'
        mysql = Mysql()
        # 总数
        sql = "SELECT COUNT(id) AS right_numbs FROM quiz_log WHERE user_id = %s and is_right = 1"
        right_numbs = mysql.getOne(sql, param=[self.info['user_id']])
        right_numbs = right_numbs.get('right_numbs') if right_numbs else 0
        
        # 连续正确回答数
        sql = "SELECT correct FROM userInfo WHERE id = %s"
        serial_numbs = mysql.getOne(sql, param=[self.info['user_id']])
        serial_numbs = serial_numbs.get('correct')

        # 检查是否参加
        sql = "SELECT * FROM quiz_log WHERE user_id = %s \
            AND to_days(create_time) = to_days(now())"
        check = mysql.getOne(sql, param=[self.info['user_id']])
        # 已经参加过
        if check:
            sql = "SELECT id, quiz_name FROM daily_quiz WHERE id = %s"
            info = mysql.getOne(sql, param=[check.get('quiz_id')])
            sql = "SELECT id, answer, is_right FROM quiz_bank WHERE quiz_id =%s"
            answer = mysql.getAll(sql, param=[info.get('id')])
            mysql.dispose()

            info['answer'] = answer
            info['right_numbs'] = right_numbs
            info['serial_numbs'] = serial_numbs
            info['choice_id'] = check.get('answer_id')
            return HttpResponse(returnJson(0, '查询成功', info))

        # 没有参加过 随机抽一题
        sql = "SELECT id, quiz_name FROM daily_quiz WHERE id NOT \
            IN (SELECT quiz_id FROM quiz_log WHERE user_id = %s)"
        info = mysql.getAll(sql, param=[self.info['user_id']])
        # 返回题目
        if info:
            if cache.has_key(cache_name):
                data = json.loads(cache.get(cache_name))
                return HttpResponse(returnJson(0, '查询成功', data))

            info = random.choice(info)
            sql = "SELECT id, answer FROM quiz_bank WHERE quiz_id = %s"
            answer = mysql.getAll(sql, param=[info.get('id')])
            mysql.dispose()

            info['answer'] = answer
            info['right_numbs'] = right_numbs
            info['serial_numbs'] = serial_numbs
            data = callJson(info)
            # 计算当时时间差
            now = datetime.datetime.now()
            zero_today = now - datetime.timedelta(hours=now.hour,
                minutes=now.minute,
                seconds=now.second, 
                microseconds=now.microsecond) + datetime.timedelta(days=1)
            t = (zero_today-now).seconds
            cache.set(cache_name, data, t)

            return HttpResponse(returnJson(0, '查询成功', info))
        else:
            return HttpResponse(returnJson(-2, '每日一答出现错误'))

    def do(self):
        
        mysql = Mysql()
        # 查答案
        sql = "SELECT is_right FROM quiz_bank WHERE id = %s AND quiz_id = %s"
        check = mysql.getOne(sql, param=[self.info['answer_id'], self.info['quiz_id']])
        right = int(check.get('is_right'))
        # 插记录
        sql = "INSERT INTO quiz_log SET user_id = %s, \
            quiz_id = %s, answer_id=%s, is_right = %s"
        mysql.insertOne(sql, param=[
            self.info['user_id'], self.info['quiz_id'],
            self.info['answer_id'], right
        ])
        # 放奖励
        if right == 1:
            sql = "UPDATE userInfo SET correct = correct + 1 WHERE id = %s"
            mysql.update(sql, param=[self.info['user_id']])
            up_sql, log_sql = Type_Log.coin_handle(
                user_id = self.info['user_id'], handle=7, num=15, asd=1)
            mysql.update(up_sql)
            mysql.insertOne(log_sql)
            mysql.dispose()
            return HttpResponse(returnJson(0, '答题成功', {'state' : 1}))

        else:
            sql = "SELECT id FROM quiz_bank WHERE quiz_id = %s AND is_right = 1"
            real_answer = mysql.getOne(sql, param=[self.info['quiz_id']])
            sql = "UPDATE userInfo SET correct = 0 WHERE id = %s"
            mysql.update(sql, param=[self.info['user_id']])
            mysql.dispose()

            data = {
                'real_answer' : real_answer.get('id'),
                'state' : 0
            }
            return HttpResponse(returnJson(0, '答题成功', data))
