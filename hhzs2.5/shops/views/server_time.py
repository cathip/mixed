import datetime

from django.views import View
from django.http import request, HttpResponse
from django.utils.decorators import method_decorator

class Server_Time(View):
    def get(self, request, **payload):
        time_info = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return HttpResponse(time_info)
