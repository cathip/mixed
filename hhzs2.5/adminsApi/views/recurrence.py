import json
from django.http import request, HttpResponse, JsonResponse
from django.views import View
from base.cmysql import Mysql
from base.shop_base import ComplexEncode, Pagings

#增加递推人员
class Add_Recurrence(View):

    def post(self, request):
        recurrence_no = request.POST.get('recurrence_no')
        recurrence_name = request.POST.get('recurrence_name')
        mysql = Mysql()
        sql = f"SELECT id FROM recurrence WHERE recurrence_no='{recurrence_no}'"
        check = mysql.getOne(sql)
        if check:
            mysql.dispose()
            return HttpResponse(0)
        sql = f"INSERT INTO recurrence SET recurrence_no \
            = '{recurrence_no}', recurrence_name = '{recurrence_name}'"
        suc = mysql.insertOne(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#编辑递推人员
class Edit_Recurrence(View):

    def post(self, request):
        recurrence_id = request.POST.get('recurrence_id')
        recurrence_no = request.POST.get('recurrence_no')
        recurrence_name = request.POST.get('recurrence_name')
        mysql = Mysql()
        sql = f"UPDATE recurrence SET recurrence_no = '{recurrence_no}', \
            recurrence_name = '{recurrence_name}' WHERE id = '{recurrence_id}'"
        suc = mysql.update(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#删除递推人员
class Del_Recurrence(View):

    def post(self, request):
        recurrence_id = request.POST.get('recurrence_id')
        mysql = Mysql()
        sql = f"DELETE FROM recurrence WHERE id = '{recurrence_id}'"
        suc = mysql.delete(sql)
        if suc:
            mysql.dispose()
            return HttpResponse(1)
        mysql.errdispose()
        return HttpResponse(0)

#查询递推人员
class Sel_Recurrence(View):

    def get(self, request):
        recurrence_no = request.GET.get('recurrence_no')
        recurrence_name = request.GET.get('recurrence_name')
        row = int(request.GET.get('row'))
        page = int(request.GET.get('page'))
        mysql = Mysql()
        if recurrence_no:
            sql = f"SELECT * FROM recurrence WHERE recurrence_no \
                = '{recurrence_no}'"
        if recurrence_name:
            sql = f"SELECT * FROM recurrence WHERE recurrence_name \
                LIKE '%{recurrence_name}%'"
        if not recurrence_no and not recurrence_name:
            sql = "SELECT * FROM recurrence"
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            sum_page, info = Pagings.paging(info, row=row, page=page)
            data = {}
            data['sum_page'] = sum_page
            data['info'] = info
            data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)
            return HttpResponse(data)
        return HttpResponse(0)