import json
from django.views import View
from base.cmysql import Mysql
from django.http import request, HttpResponse, QueryDict
from base.shop_base import Pagings, ComplexEncode

#增加题目
class Add_Answer(View):

    def post(self, request):
        quiz_name = request.POST.get('quiz_name')
        answer_list = json.loads(request.POST.get('answer_list'))
        print(type(answer_list))
        #[{answer:xxx,is_right:1}]
        mysql = Mysql()
        try:
            sql = f"INSERT INTO daily_quiz SET quiz_name = '{quiz_name}'"
            quiz_id = mysql.insertOne(sql)
            for i in answer_list:
                sql = f'''INSERT INTO quiz_bank SET quiz_id = "{quiz_id}",\
                    answer = "{i.get('answer')}", is_right = "{i.get('is_right')}"'''
                mysql.insertOne(sql)
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)
            
#删除题目
class Del_Answer(View):

    def post(self, request):
        quiz_id = request.POST.get('quiz_id')
        mysql = Mysql()
        sql = f"DELETE FROM daily_quiz WHERE id = '{quiz_id}'"
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#编辑题目
class Edit_Answer(View):

    def post(self, request):
        quiz_name = request.POST.get('quiz_name')
        answer_list = json.loads(request.POST.get('answer_list'))
        quiz_id = request.POST.get('quiz_id')
        #[{answer:xxx,is_right:1}]
        mysql = Mysql()
        try:
            sql = f"UPDATE daily_quiz SET quiz_name = '{quiz_name}' WHERE id = '{quiz_id}'"
            mysql.update(sql)
            sql = f"DELETE FROM quiz_bank WHERE quiz_id = {quiz_id}"
            mysql.delete(sql)
            for i in answer_list:
                sql = f'''INSERT INTO quiz_bank SET quiz_id = {quiz_id}, \
                    answer="{i.get('answer')}", is_right = "{i.get('is_right')}"'''
                mysql.update(sql)
            mysql.dispose()
            return HttpResponse(1)
        except Exception as e:
            print(e)
            mysql.errdispose()
            return HttpResponse(0)

#查看题目
class Sel_Answer(View):

    def get(self, request):
        quiz_name = request.GET.get('quiz_name')
        row = request.GET.get('row')
        page = request.GET.get('page')
        mysql = Mysql()
        sql = f"SELECT * from daily_quiz as d \
            WHERE d.quiz_name LIKE '%{quiz_name}%'"
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            sum_page, info = Pagings.paging(info, row=row, page=page)
            data = {}
            data['sum_page'] = sum_page
            data['info'] = info
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(data)
        return HttpResponse(0)

#查看题目详情
class Sel_Answer_Detail(View):

    def get(self, request):
        quiz_id = request.GET.get("quiz_id")
        mysql = Mysql()
        sql = f"SELECT * FROM quiz_bank WHERE quiz_id = {quiz_id}"
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            info = json.dumps(info, ensure_ascii=False, sort_keys=True, indent=4, cls=ComplexEncode)
            return HttpResponse(info)
        return HttpResponse(0)
        