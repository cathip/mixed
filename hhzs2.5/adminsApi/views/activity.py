# coding=utf-8
import datetime
import json
import requests
from django.http import request, JsonResponse, HttpResponse
from base import wx_config
from django.views import View
from base.cmysql import Mysql
from base.shop_base import Pagings
from datetime import datetime

'''
关于活动的接口
'''
#活动查询
class Get_One_Activity(View):
    
    def __init__(self):
        self.__reqDtat = {}

    def get(self, request):
        self.get_params(request)
        info, iswin = self.get_one_activity()
        data = {}
        data['iswin'] = iswin
        if info:
            sumpage, Asoder = Pagings.paging(info, self.__reqDtat['row'], self.__reqDtat['page'])
            if len(Asoder) == 0:
                pass
            else:
                data['pagecount'] = sumpage
                asos = []
                data['info'] = asos
                for aso in Asoder:
                    asos.append({'act_id':aso.get('id'), 'activityName':aso.get('activityName'), 'activityImg':aso.get('activityImg'), 'startTime':aso.get('startTime'), 'endTime':aso.get('endTime'), 'poster':aso.get('poster'), 'class_id':aso.get('acti_class_id')})
        else:
            pass     
        return JsonResponse(data)

    def get_params(self, request):
        self.__reqDtat['name'] = request.GET.get('name')
        self.__reqDtat['row'] = request.GET.get('row')
        self.__reqDtat['page'] = request.GET.get('page')
    
    def get_one_activity(self):
        mysql = Mysql()
        sql = 'SELECT * FROM activity WHERE activityName LIKE "%{name}%"'.format(name=self.__reqDtat['name'])
        info = mysql.getAll(sql)
        mysql.dispose()
        if info:
            iswin = 1
        else:
            iswin = 0
        return info, iswin

#获取活动列表
class Get_Activity(View):

    def get(self, request):
        info, iswin = self.sel_activity()
        data = {}
        data['iswin'] = iswin
        if info:
            sumpage, Asoder = Pagings.paging(info, request.GET.get('row'), request.GET.get('page'))
            if len(Asoder) == 0:
                pass
            else:
                data['pagecount'] = sumpage
                asos = []
                data['info'] = asos
                for aso in Asoder:
                    asos.append({'act_id':aso.get('id'),'activityName':aso.get('activityName'), 'activityImg':aso.get('activityImg'), 'startTime':aso.get('startTime'), 'endTime':aso.get('endTime'), 'poster':aso.get('poster'), 'class_id':aso.get('acti_class_id')})
        else:
            pass
        return JsonResponse(data)

    def sel_activity(self):
        mysql = Mysql()
        sql = 'SELECT * FROM activity'
        info = mysql.getAll(sql)
        if info:
            iswin = 1
        else:
            iswin = 0
        mysql.dispose()
        return info, iswin

#增加活动
class Add_Activity(View):
     
    def __init__(self):
        self.__reqData = {}

    def post(self, request):
        self.post_params(request)
        iswin = self.add_activity()
        data = {}
        data['iswin'] = iswin
        return JsonResponse(data)

    def post_params(self, request):
        self.__reqData['activityName'] = request.POST.get('activityName')
        self.__reqData['activityImg'] = request.POST.get('activityImg')
        self.__reqData['startTime'] = request.POST.get('startTime')
        self.__reqData['endTime'] = request.POST.get('endTime')
        self.__reqData['class_id'] = request.POST.get('class_id')
        self.__reqData['poster'] = int(request.POST.get('poster')) #活动类型 1代表商品活动 0代表海报
        self.__reqData['act_list'] = request.POST.get('act_list', False)



    def add_activity(self):
        mysql = Mysql()
        if  self.__reqData['poster'] == 0:
            sql = 'INSERT INTO activity(activityName, activityImg, startTime, endTime, poster, acti_class_id) VALUES("{name}","{img}","{start}","{end}","{poster}","{class_id}")'.format(name=self.__reqData['activityName'], img=self.__reqData['activityImg'], start=self.__reqData['startTime'], end=self.__reqData['endTime'], poster=self.__reqData['poster'], class_id=1)
            mysql.insertOne(sql)
            iswin = 1
        elif self.__reqData['poster'] == 1:
            sql = 'INSERT INTO activity(activityName, activityImg, startTime, endTime, poster, acti_class_id) VALUES("{name}","{img}","{start}","{end}","{poster}","{class_id}")'.format(name=self.__reqData['activityName'], img=self.__reqData['activityImg'], start=self.__reqData['startTime'], end=self.__reqData['endTime'], poster=self.__reqData['poster'], class_id=1)
            print(sql)
            act_info = mysql.insertOne(sql)
            print(act_info)
            # sql = 'SELECT id FROM activity WHERE activityName="{activityName}"'.format(activityName=self.__reqData['activityName'])
            # act_info = mysql.getOne(sql)
            act_dict = json.loads(self.__reqData['act_list'])
            for k, v in act_dict.items():
                stockProductId = v.get('stockProductId')
                newPrice = v.get('newPrice')
                newHHcoin = v.get('newHHcoin')
                limitnum = v.get('limitnum')
                sql = 'INSERT INTO activityproduct(activityId,stockProductId,newPrice,newHHcoin,limitnum) ' \
                      'VALUES({act_num},{stockProductId},{newPrice},{newHHcoin},{limitnum})'.format(
                    act_num=act_info, stockProductId=stockProductId, newPrice=newPrice,
                    newHHcoin=newHHcoin, limitnum=limitnum)
                print(sql)
                mysql.insertOne(sql)
                sql = "UPDATE product, spec SET  product.act_num='{act_num}', product.limitNum='{limitnum}', \
                        spec.limitNum='{limitnum}', spec.acti_hehecoin='{newHHcoin}', \
                        spec.acti_price='{newPrice}' \
                        WHERE spec.productId = product.id \
                        AND spec.id='{stockProductId}'".format(act_num=act_info, limitnum=limitnum, newHHcoin=newHHcoin, newPrice=newPrice, stockProductId=stockProductId)
                print(sql)
                mysql.update(sql)
            iswin = 1
        else:
            iswin = 0
        mysql.dispose()
        return iswin

#编辑活动
class Edit_Activity(View):

    def __init__(self):
        self.__reqData = {}

    def post(self, request):
        self.post_params(request)
        iswin = self.edit_act()
        data = {}
        data['iswin'] = iswin
        return JsonResponse(data) 

    def post_params(self, request):
        self.__reqData['id'] = request.POST.get('id')
        self.__reqData['activityName'] = request.POST.get('activityName')
        self.__reqData['activityImg'] = request.POST.get('activityImg')
        self.__reqData['startTime'] = request.POST.get('startTime')
        self.__reqData['endTime'] = request.POST.get('endTime')
        self.__reqData['poster'] = int(request.POST.get('poster'))
        self.__reqData['class_id'] = request.POST.get('class_id')
        self.__reqData['act_list'] = request.POST.get('act_list', False)


    def edit_act(self):
        mysql = Mysql()
        if self.__reqData['poster'] == 0:
            sql = "UPDATE activity SET activityName='{activityName}', activityImg='{activityImg}', startTime='{startTime}', endTime='{endTime}', acti_class_id='{class_id}' WHERE id = '{id}'".format(activityName=self.__reqData['activityName'], activityImg=self.__reqData['activityImg'], startTime=self.__reqData['startTime'], endTime=self.__reqData['endTime'], id=self.__reqData['id'], class_id=self.__reqData['class_id'])
            print(sql)
            mysql.update(sql)
            iswin = 1
        elif self.__reqData['poster'] == 1:
            sql = "UPDATE activity SET activityName='{activityName}', activityImg='{activityImg}', startTime='{startTime}', endTime='{endTime}', acti_class_id='{class_id}' WHERE id = '{id}'".format(activityName=self.__reqData['activityName'], activityImg=self.__reqData['activityImg'], startTime=self.__reqData['startTime'], endTime=self.__reqData['endTime'], id=self.__reqData['id'], class_id=self.__reqData['class_id'])
            mysql.update(sql)
            if self.__reqData['act_list']:
                act_dict = json.loads(self.__reqData['act_list'])
                for k, v in act_dict.items():
                    newPrice = v.get('newPrice')
                    newHHcoin = v.get('newHHcoin')
                    limitnum = v.get('limitnum')
                    new_stockProductId = v.get('stockProductId')
                    sql1 = "INSERT INTO activityproduct(activityId,stockProductId,newPrice,newHHcoin,limitnum) \
                        VALUES('{act_num}','{stockProductId}','{newPrice}','{newHHcoin}','{limitnum}')".format(
                        act_num=self.__reqData['id'], stockProductId=new_stockProductId, newPrice=newPrice,
                        newHHcoin=newHHcoin, limitnum=limitnum)
                    print(sql1)
                    mysql.insertOne(sql1)
                    sql = "UPDATE product, spec SET product.act_num='{actid}', product.limitNum='{limitnum}', \
                                            spec.limitNum='{limitnum}', spec.acti_hehecoin='{newHHcoin}', \
                                            spec.acti_price='{newPrice}' \
                                            WHERE spec.productId = product.id \
                                            AND spec.id='{stockProductId}'".format\
                        (actid=self.__reqData['id'], limitnum=limitnum, newHHcoin=newHHcoin, newPrice=newPrice, stockProductId=new_stockProductId)
                    mysql.update(sql)
                    print(sql)
                iswin = 1
            else:
                iswin = 2
        else:
            iswin = 0
        mysql.dispose()
        return iswin

#删除活动    
class Del_Activity(View):

    def __init__(self):
        self.__reqData = {}     

    def get(self, request):
        self.get_params(request)
        iswin = self.del_act()
        print('--------------iswin--------------')
        print(iswin)
        data = {}
        data['iswin'] = iswin
        return JsonResponse(data)

    def get_params(self, request):
        self.__reqData['act_id'] = request.GET.get('act_id')
        self.__reqData['act_type'] = int(request.GET.get('act_type'))
    
    def del_act(self):
        mysql = Mysql()
        if self.__reqData['act_type'] == 1:
            sql = "SELECT stockProductId FROM activityproduct WHERE activityId='{act_id}'".format(act_id=self.__reqData['act_id'])
            suc = mysql.getAll(sql)
            for i in suc:
                sql = "UPDATE product, spec SET product.act_num='0', product.limitNum='0', \
                                        spec.limitNum='0', spec.acti_hehecoin='0', \
                                        spec.acti_price='0' \
                                        WHERE spec.productId = product.id \
                                        AND spec.id='{stockProductId}'".format(stockProductId=i.get('stockProductId'))
                mysql.update(sql)
            sql = "DELETE FROM activity WHERE id = '{act_id}'".format(act_id=self.__reqData['act_id'])
            del_one = mysql.delete(sql)
            sql = "DELETE FROM activityproduct WHERE activityId = '{act_id}'".format(act_id=self.__reqData['act_id'])
            del_two = mysql.delete(sql)
            if del_one and del_two:
                iswin  = 1
            else:
                iswin = 0
        elif self.__reqData['act_type'] == 0:
            sql = "DELETE FROM activity WHERE id = '{act_id}'".format(act_id=self.__reqData['act_id'])
            del_tre = mysql.delete(sql)
            if del_tre:
                iswin = 1
            else:
                iswin = 0
        else:
            iswin = "活动类型错误"
        mysql.dispose()
        return iswin

#获取单个活动商品详情
class Edit_Button(View):

    def get(self, request):
        spec_id = self.sel_actp(request)
        new_spec_id = json.dumps(spec_id, ensure_ascii=False, sort_keys=True, indent=4)
        return HttpResponse(new_spec_id)

    def sel_actp(self, request):
        mysql = Mysql()
        poster = request.GET.get('act_type')
        if int(poster) == 1:
            sql = "SELECT stockProductId FROM activityproduct WHERE activityId = '{act_id}'".format(act_id=request.GET.get('act_id'))
            spro_id = mysql.getAll(sql)
            product_list = []
            for i in spro_id:
                sql = "SELECT  spec.price, spec.hehecoin, spec.limitNum, spec.acti_price, spec.acti_hehecoin, product.productName \
                    FROM spec LEFT JOIN product ON spec.productId = product.id WHERE spec.id = '{spec_id}'".format(spec_id=i.get('stockProductId'))
                info = mysql.getOne(sql)
                info['id'] = i.get('stockProductId')
                product_list.append(info)
            return product_list
        else:
            spro_id = 0
        mysql.dispose()
        return spro_id

#删除单个活动商品
class Del_One_ActiviryProduct(View):

    def get(self, request):
        print('删除活动')
        iswin = self.del_one_activiryproduct(request)
        return HttpResponse(iswin)

    def del_one_activiryproduct(self, request):
        mysql = Mysql()
        sql = 'DELETE FROM activityproduct WHERE activityId="{act_id}" \
            AND stockProductId = "{spec_id}"'.format(act_id=request.GET.get('act_id'), spec_id=request.GET.get('spec_id'))
        del_info = mysql.delete(sql)
        print(sql)
        sql = "UPDATE product, spec SET product.act_num='0', product.limitNum='0', \
                                        spec.limitNum='0', spec.acti_hehecoin='0', \
                                        spec.acti_price='0' \
                                        WHERE spec.productId = product.id \
                                        AND spec.id='{spec_id}'".format(spec_id=request.GET.get('spec_id'))
        print(sql)
        update_info = mysql.update(sql)
        mysql.dispose()
        if del_info and update_info:
            iswin = 1
            return iswin
        else:
            iswin = 0
            return iswin

#新增活动分类
class Add_Activity_Class(View):
    
    def __init__(self):
        self.__reqData = {}

    def post(self, request):
        self.post_params(request)
        suc = self.add_activity_class()
        return HttpResponse(suc)

    def post_params(self, request):
        self.__reqData['name'] = request.POST.get('name')
        self.__reqData['parentId'] = request.POST.get('acti_parentId') #增加分类 顶级分类0

    def add_activity_class(self):
        mysql = Mysql()
        sql = "INSERT INTO activity_class SET acti_classname = '{name}', \
            acti_parentId = '{parentId}'".format(name=self.__reqData['name'], parentId=self.__reqData['parentId'])
        suc = mysql.insertOne(sql)
        if suc:
            return 1
        else:
            return 0

#删除活动分类
class Del_Activity_Class(View):
    
    def __init__(self):
        self.__reqData = {}

    def post(self, request):
        self.post_params(request)
        suc = self.del_activity_class()
        return HttpResponse(suc)

    def post_params(self, request):
        self.__reqData['id'] = request.POST.get('id')
        
    def del_activity_class(self):
        mysql = Mysql()
        sql = "SELECT * FROM activity WHERE acti_class_id = '{id}'".format(id=self.__reqData['id'])
        info = mysql.getAll(sql)
        if info:
            #有活动
            return 2
        else:
            sql = "SELECT * FROM activity_class WHERE acti_parentId = '{id}'".format(id=self.__reqData['id'])
            suc = mysql.getOne(sql)
            if suc:
                #分类下有子分类
                return 3
            else:
                sql = "DELETE FROM activity_class WHERE id = '{id}'".format(id=self.__reqData['id'])
                suc = mysql.delete(sql)
                if suc:
                    mysql.dispose()
                    return 1
                else:
                    mysql.errdispose()
                    return 0

#查询活动分类
class Sel_Activity_Class(View):
    
    def __init__(self):
        self.__reqData = {}

    def post(self, request):
        self.post_params(request)
        info = self.sel_activity_class()
        data = json.dumps(info, ensure_ascii=False, sort_keys=True, indent=4)
        return HttpResponse(data)

    def post_params(self, request):
        self.__reqData['parentId'] = request.POST.get('parentId', False)
        
    def sel_activity_class(self):
        mysql = Mysql()
        if self.__reqData['parentId']:
            sql = 'SELECT * FROM activity_class WHERE acti_parentId = "{parentId}"'.format(id=self.__reqData['parentId'])
            info = mysql.getAll(sql)
            return info
        else:
            sql = 'SELECT * FROM activity_class WHERE acti_parentId = 0'
            info = mysql.getAll(sql)
            mysql.dispose()
            return info

#编辑活动分类
class Edit_Activity_Class(View):
    
    def __init__(self):
        self.__reqData = {}

    def post(self, request):
        self.post_params(request)
        suc = self.edit_activity_class()
        return HttpResponse(suc)

    def post_params(self, request):
        self.__reqData['name'] = request.POST.get('name')
        self.__reqData['img'] = request.POST.get('img')
        self.__reqData['id'] = request.POST.get('id')
        
    def edit_activity_class(self):
        mysql = Mysql()
        sql = "UPDATE activity_class SET acti_classname = '{name}', acti_class_img = '{img}' \
            WHERE id = '{id}'".format(name=self.__reqData['name'], img=self.__reqData['img'], id=self.__reqData['id'])
        suc = mysql.update(sql)
        if suc:
            return 1
        else:
            return 0
