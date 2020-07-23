import json
from django.http import request, HttpResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Pagings
import os

#排名对应的奖励编号
class Sel_Rank_Reward(View):
    def get(self, request):
        rank_type = request.GET.get('rank_type') #0个人 校园
        if not rank_type:
            return HttpResponse('没有传入排行类型')
        if int(rank_type) == 1:
            sql = "SELECT rank_num, prize_detail, prize_type_name, prize_id FROM rank_reward \
                    LEFT JOIN prize ON rank_reward.prize_id = prize.id \
                    LEFT JOIN prize_type_class ON prize.prize_type = prize_type_class.prize_type_id \
                    WHERE rank_type=1 ORDER BY rank_num"
        if int(rank_type) == 0:
            sql = "SELECT rank_num, prize_detail, prize_type_name, prize_id FROM rank_reward \
                    LEFT JOIN prize ON rank_reward.prize_id = prize.id \
                    LEFT JOIN prize_type_class ON prize.prize_type = prize_type_class.prize_type_id \
                    WHERE rank_type=0 ORDER BY rank_num"
        mysql = Mysql()
        info = mysql.getAll(sql)
        mysql.dispose()
        info = json.dumps(info, ensure_ascii=False, sort_keys=True, indent=4)
        return HttpResponse(info)

#更改排名对应的奖励
class Edit_Rank_Reward(View):
    
    def post(self, request):
        rank_type = request.POST.get('rank_type') #0个人 校园
        rank_num = request.POST.get('rank_num') #排名
        prize_id = request.POST.get('prize_id') #奖品编号
        mysql = Mysql()
        sql = f"UPDATE rank_reward SET prize_id = '{prize_id}' \
            WHERE rank_num ='{rank_num}' AND rank_type = '{rank_type}'"
        print(sql)
        suc =  mysql.update(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#更改排行榜对应规则
class Rank_Ruler(View):

    def post(self, request):
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        banner = request.POST.get('banner')
        ruler = request.POST.get('ruler')
        get_info = int(request.POST.get('get_info'))
        #filename = "C:\\Users\\86248\\Desktop\\git\\hhzs_2.0\\hhsc2019\\adminsApi\\views\\rank.json"
        filename = "/home/ubuntu/hhsc2019/adminsApi/views/rank.json"
        if get_info == 1:
            with open(filename, 'r') as f:
                return HttpResponse(f.read())
        if get_info == 0:
            with open(filename, 'w') as f:
                json.dump({'start_time': start_time, 'end_time': end_time, \
                    'banner': banner, 'ruler': ruler}, f)
            return HttpResponse(1)
        else:
            return HttpResponse("请输入get_info")
