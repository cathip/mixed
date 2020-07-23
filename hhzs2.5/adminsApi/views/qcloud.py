import sys
import json
import time
import base64
import logging
import requests

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosServiceError
from qcloud_cos import CosClientError

from django.views import View
from django.http import HttpRequest, HttpResponse, JsonResponse, QueryDict

from base.shop_base import getImgName

#配置信息
#Bucket = 'cat-1257765943'
Appid = '1257765943'
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
SecretId = ''
SecretKey = ''
Region = ''
Token = None
config = CosConfig(Appid=Appid, Region=Region, Secret_id=SecretId, Secret_key=SecretKey, Token=Token)
cos_client = CosS3Client(config)

'''
关于腾讯云上传图片一切操作
'''
class Tencent_Cos(View):

    #上传图片
    def post(self, request):
        try:
            #获取参数
            up_file = request.POST.get('up_file')
            bucket = request.POST.get('bucket')
            img_name = request.POST.get('img_name', False)
            file_path = "new_img/"
            #base64转二进制
            imgdata = base64.b64decode(up_file)
            #上传
            if img_name:
                new_file_name = file_path + img_name
                cos_client.put_object(Bucket=bucket, Body=imgdata, Key=new_file_name)
                return HttpResponse(img_name)
            file_name = getImgName()
            new_file_name = file_path + file_name
            cos_client.put_object(Bucket=bucket, Body=imgdata, Key=new_file_name)
            return HttpResponse(file_name)
        except Exception as e:
            print(e)
            print('上传图片出现错误！！！！！！！！！！！')
            return HttpResponse(0)

    #批量删除图片
    def delete(self, request):
        try:
            #获取参数
            del_name = QueryDict(request.body)
            for k, v in del_name.items():
                info = json.loads(k)
            print(info.get('file_name'))
            print(info.get('bucket'))
            data = {"Quiet": "true","Object": info.get('file_name')}
            cos_client.delete_objects(Bucket=info.get('bucket'), Delete=data)
            return HttpResponse(1)
        except Exception as e:
            print(e)
            print('删除图片出现错误！！！！！！！！！！！！！！')
            return HttpResponse(0)

    #删除单张图片
    # def delete(self, request):
    #     try:
    #         #获取参数
    #         del_name = QueryDict(request.body)
    #         for k, v in del_name.items():
    #             info = json.loads(k)
    #         print(info.get('file_name'))
    #         cos_client.delete_object(Bucket=Bucket, Key=info.get('file_name'))
    #         return HttpResponse(1)
    #     except Exception as e:
    #         print(e)
    #         print('删除图片出现错误！！！！！！！！！！！！！！')
    #         return HttpResponse(0)

    #获取图片名字
    # def get(self, request):
    #     #获取参数
    #     file_name = request.GET.get('file_name')
    #     bucket = request.GET.get('bucket')
    #     #获取文件
    #     url = cos_client.get_presigned_url(Bucket=bucket, Key=file_name, Method='GET')
    #     return HttpResponse(url)

