# utf-8

'''
获取用户信息，如openid等
'''
import jwt
import json
import time
import hashlib
import datetime
import requests

from django.views import View
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse

from base import wx_config
from base.jwt import getToken
from base.cmysql import Mysql
from base.Predis import Open_Redis
from base.wx_config import APPID, SECRET
from base.GetData import WXBizDataCrypt
from base.shop_base import Type_Log, getNonceStr, getSign, getShaSign, returnJson, queryOne, query
from hhsc2019.settings import SECRET_KEY

#获取微信步数 手机号 unionId --ok
class WxData(View):

    def __init__(self):
        self.Info = {}

    def post(self, request, **payload):
        '''
        获取解密后的微信步数以及VIP信息
        '''
        handle = payload.get('handle')

        self.Info['openid'] = payload.get('openid')
        self.Info['sessionKey'] = payload.get('session_key')
        self.Info['user_id'] = payload.get('user_id')
    
        #用来判断是获取手机号还是微信步数, 0获取手机号, 1获取步数, 2获取unionid
        self.Info['iv'] = request.POST.get('iv') #加密算法的初始向量
        self.Info['encryptedData'] = request.POST.get('encryptedData')

        self.Info["jscode"] = request.POST.get("jscode")


        if handle == "getPhone":
            data = self.get_data()
            print(data)
            phone = data.get('phoneNumber')
            self.save_data(data.get('phoneNumber'))
            return HttpResponse(returnJson(0, '获取手机号成功', {'phone' : phone}))

        if handle == "getUnionid":
            data = self.get_data()
            print(data)
            unionId = data.get('unionId')
            return HttpResponse(returnJson(0, '获取数据成功', {'unionid' : unionId}))

        if handle == 'checkStep':
            data = self.get_data()
            print(data)
            return self.checkStep()

        if handle == "getStep":
            data = self.get_data()
            print(data)
            stepInfoList = data.get('stepInfoList')
            yes_step = self.parse_stepnum(stepInfoList)
            mysql = Mysql()
            sql = "SELECT * FROM coin_log WHERE userid = %s \
                AND handleType = 3 AND to_days(handletime) = to_days(now()) "
            check = mysql.getOne(sql, param=[self.Info['user_id']])
            if check:
                mysql.dispose()
                return HttpResponse(returnJson(0, '获取数据成功', {'yes_step' : yes_step}))
            else:
                hhcoin = 30 if int(int(yes_step) / 500) >= 30 else int(int(yes_step) / 500)
                up_sql, log_sql = Type_Log.coin_handle(
                    user_id=self.Info['user_id'], handle=3, num=hhcoin, asd=1)
                mysql.update(up_sql)
                mysql.insertOne(log_sql)
                mysql.dispose()
                data = {
                    "yes_step": yes_step, 
                    "hhcoin": hhcoin
                }
                return HttpResponse(returnJson(0, '获取数据成功', data))

        if handle == 'getOpenid':
            return self.getOpenid()

        if handle == 'checkToken':
            return self.checkToken(request)

        return HttpResponse(returnJson(-2, '非法路径'))

    def get_data(self):
        ps = WXBizDataCrypt(self.Info['sessionKey'])
        data = ps.decrypt(self.Info['encryptedData'], self.Info['iv'])
        return data

    def save_data(self, mobile):
        mysql = Mysql()
        sql = "update  userInfo set mobile=%s  where openid=%s"
        checkOk = mysql.update(sql, param=[mobile, self.Info['openid']])
        mysql.dispose()
        print(f"用户 {self.Info['openid']} 更新手机号 {mobile}")
        return True

    def parse_stepnum(self, stepInfoList=[]):
        if stepInfoList:
            for i in stepInfoList:
                timestamp = i.get('timestamp')
                stepnum = i.get('step')
                yes_time = (datetime.datetime.now() + datetime.timedelta(days=-1)).isoformat()[:10]
                localtime = time.localtime(timestamp)
                # 利用strftime()函数重新格式化时间
                dt = time.strftime('%Y-%m-%d', localtime)
                if dt == yes_time:
                    return stepnum
        else:
            raise Exception('获取步数错误')

    def checkStep(self):
        date = datetime.datetime.today().isoformat().split('T')[0]
        sql = 'select * from coin_log where userid=%s and handleType=3 AND %s =  %s'
        data = queryOne(sql, param=[
            self.Info['user_id'],
            'date_format(handletime,"%Y-%m-%d")',
            data
        ])
        data = {'isok' : True} if data else {'isok' : False}
        return HttpResponse(returnJson(0, '查询成功', data))

    def checkToken(self, request):
        token = request.META.get('HTTP_TOKEN')
        try:
            jwt.decode(token, SECRET_KEY, True)
            return JsonResponse({
                'ret' : 0,
                'msg' : '有效token'
            })
        except Exception as e:
            return JsonResponse({
                'ret' : -2,
                'msg' : '无效token'
            })

    def getOpenid(self):
        data = self.requestWx(self.Info["jscode"])
        if not data:
            return JsonResponse({
                'ret' : -2,
                'msg' : 'jscode错误'
            })
        openid = data[0]
        session_key = data[1]
        user_info = self.isEsxit(openid)
        if user_info:
            user_info['openid'] = openid
            user_info['session_key'] = session_key

            payload = {
                'user_id' : user_info.get('id'),
                'openid' : openid,
                'session_key' : session_key
            }

            token = getToken(payload, 24)
            user_info['token'] = token
            return JsonResponse({
                'ret' : 0,
                'msg' : '登录成功',
                'result' : user_info
            })
        return JsonResponse({
            'ret' : -2,
            'msg' : '网络异常'
        })

    def isEsxit(self, openid):
        '''
        判断用户是否存在，不存在则插入
        '''
        mysql = Mysql()
        sql = 'select id, mobile, school_id from userInfo where openid=%s'
        data = mysql.getOne(sql, param=[openid])
        if data:
            print(f"***********用户已经存在了****id{data.get('id')}*********")
            mysql.dispose()
            data['isnew'] = 0
            return data
        else:
            sql = "INSERT INTO userInfo(openid, createTime, isVip, vipEndTime, hhcoin) VALUE \
                  (%s, NOW(),1, DATE_ADD(Now(), INTERVAL 7 day ), 100)"
            user_id = mysql.insertOne(sql, param=[openid])
            if user_id:
                mysql.dispose()
                data = {}
                data['id'] = user_id
                data['mobile'] = None
                data['school_id'] = None
                data['isnew'] = 1
                print(f"**************新增用户成功****id{user_id}**********")
                return data
            else:
                mysql.errdispose()
                print("**************新增用户失败****************")
                return False

    def requestWx(self, jscode):
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={js_code}&grant_type=authorization_code'
        full_url = url.format(appid=wx_config.GZH_APPID,
            secret=wx_config.GZH_SECRET, js_code=self.Info["jscode"])
        # 1.请求微信小程序的接口，获取返回的值
        response = requests.get(full_url).text
        res_data = json.loads(response)  # 把json格式的转成python类型的数据
        if res_data.get('errcode'):
            return False
        openid = res_data.get('openid')
        session_key = res_data.get('session_key')
        return openid, session_key

# 获取openid
class OpenView(View):
    '''
    获取openid
    '''
    def __init__(self):
        self.info = {}

    def get_openid(self, jscode):
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={js_code}&grant_type=authorization_code'
        full_url = url.format(appid=wx_config.GZH_APPID,
            secret=wx_config.GZH_SECRET, js_code=jscode)
        # 1.请求微信小程序的接口，获取返回的值
        response = requests.get(full_url).text
        res_data = json.loads(response)  # 把json格式的转成python类型的数据
        if res_data.get('errcode'):
            return False
        openid = res_data.get('openid')
        session_key = res_data.get('session_key')
        return openid, session_key
        
    def post(self, request):
        '''
        逻辑方法
        '''
        self.info["jscode"] = request.POST.get("jscode")
        data = self.get_openid(self.info["jscode"])
        if not data:
            return JsonResponse({
                'ret' : -2,
                'msg' : 'jscode错误'
            })
        openid = data[0]
        session_key = data[1]
        user_info = self.isEsxit(openid)
        if user_info:
            user_info['openid'] = openid
            user_info['session_key'] = session_key

            payload = {
                'user_id' : user_info.get('id'),
                'openid' : openid,
                'session_key' : session_key
            }

            token = getToken(payload, 2)
            user_info['token'] = token
            return JsonResponse({
                'ret' : 0,
                'msg' : '登录成功',
                'result' : user_info
            })
        return JsonResponse({
            'ret' : -2,
            'msg' : '网络异常'
        })

    def isEsxit(self, openid):
        '''
        判断用户是否存在，不存在则插入
        '''
        mysql = Mysql()
        sql = 'select id, mobile, school_id from userInfo where openid=%s'
        data = mysql.getOne(sql, param=[openid])
        if data:
            print(f"***********用户已经存在了****id{data.get('id')}*********")
            mysql.dispose()
            data['isnew'] = 0
            return data
        else:
            sql = "INSERT INTO userInfo(openid, createTime, isVip, vipEndTime, hhcoin) VALUE \
                  (%s, NOW(),1, DATE_ADD(Now(), INTERVAL 7 day ), 100)"
            user_id = mysql.insertOne(sql, param=[openid])
            if user_id:
                mysql.dispose()
                data = {}
                data['id'] = user_id
                data['mobile'] = None
                data['school_id'] = None
                data['isnew'] = 1
                print(f"**************新增用户成功****id{user_id}**********")
                return data
            else:
                mysql.errdispose()
                print("**************新增用户失败****************")
                return False

#获取网页签名
class AutoGraph(View):

    def post(self, request, **payload):
        url = request.POST.get('url')

        token = self.request_wx()
        timestamp = int(time.time())
        js_ticket = self.get_jsapi_ticket(token)
        nonce = getNonceStr()
        ret = {
            'noncestr':nonce,
            'jsapi_ticket':js_ticket,
            'timestamp':timestamp,
            'url':url
        }
        sign = getShaSign(ret)
        data = {
            'timestamp': timestamp,
            'nonce': nonce,
            'signature': sign
		}
        return JsonResponse(data)

    def request_wx(self):
        url = "http://gzh.hehezaisheng.com/Api/pub.asmx/getAccessToken"
        response = requests.get(url)
        response = response.text
        return response #凭证有效时间，单位：秒

    def get_jsapi_ticket(self, token):
        url = f'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={token}&type=jsapi'
        response =  requests.get(url)
        response = response.json()
        if response.get('errcode') != 0:
            raise Exception(response)
        ticket = response.get('ticket')
        return ticket

#公众号获取用户信息 
class SnsApiUserInfo(View):

    def post(self, request, **payload):
        self.info = {}
        self.info['code'] = request.POST.get('code')
        acccess_info = self.get_access_token(self.info['code'] )
        print(acccess_info)
        if not acccess_info.get('openid'):
            return JsonResponse({
                'ret' : -2,
                'msg' : '参数错误'
            })
        self.info['access_token'] = acccess_info.get('access_token')
        self.info['openid'] = acccess_info.get('openid')
        user_info = self.get_userinfo(self.info['access_token'], self.info['openid'])
        
        openid = user_info.get('openid')
        nickname = user_info.get('nickname')
        unionid = user_info.get('unionid')
        return JsonResponse({
            'ret' : 0,
            'msg' : '获取成功',
            'result' : {
                'openid' : openid,
                'nickname' : nickname,
                'unionid' : unionid
            }            
        })

    def get_access_token(self, code):
        url = f'https://api.weixin.qq.com/sns/oauth2/access_token?appid={APPID}&secret={SECRET}&code={code}&grant_type=authorization_code'
        response = requests.get(url)
        response = response.json()
        return response

    def get_userinfo(self, access_token, openid):
        mysql = Mysql()
        sql = "SELECT * FROM h5_user WHERE openid = %s"
        check = mysql.getOne(sql, param=[openid])
        if check:
            mysql.dispose()
            return check
        url = f'https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}&lang=zh_CN'
        response = requests.get(url)
        response.encoding = 'utf-8' 
        response.text
        user_info = response.json()
        sql = 'INSERT INTO h5_user SET unionid=%s, openid=%s, \
            city=%s, country=%s, headimgurl=%s, lucky_draw_times=1'
        mysql.insertOne(sql, param=[
            user_info.get('unionid'),
            user_info.get('openid'),
            user_info.get('city'),
            user_info.get('country'),
            user_info.get('headimgurl')
        ])
        mysql.dispose()
        return user_info


#检查登录态
class Check_Openid(View):

    def get(self, request, **payload):
        token = request.META.get('HTTP_TOKEN')
        try:
            jwt.decode(token, SECRET_KEY, True)
            return JsonResponse({
                'ret' : 0,
                'msg' : '有效token'
            })
        except Exception as e:
            return JsonResponse({
                'ret' : -2,
                'msg' : '无效token'
            })

#腾讯地图
class distance(View):

    def __init__(self):
        self.Info = {}

    def get_param(self, request):
        self.Info['addr'] = request.GET.get('addr')

    def get(self, request, **payload):
        self.get_param(request)
        data = self.get_dis_data()
        if 'from元素的值不合法' in data:
            return HttpResponse("传入地址参数格式或者数据有误！请重新传入.....")
        dat = self.get_name(data)  # 获取到名字
        finalData = self.get_lowest(dat)
        return JsonResponse({'data': finalData})

    def get_dis_data(self):
        addrs = self.AllStore()
        full_url = 'https://apis.map.qq.com/ws/distance/v1/?key={key}&mode=walking&from={addr}&to={addrs}'.format(
            key=wx_config.Distance_key, addr=self.Info['addr'], addrs=addrs)
        data = requests.get(url=full_url).text
        return data

    def AllStore(self):
        mysql = Mysql()
        sql = 'select * from store'
        data = mysql.getAll(sql)
        mysql.dispose()
        li = []
        for dat in data:
            lng = dat.get('longitude')
            lat = dat.get('latitude')
            addr = str(lng)+','+str(lat)
            li.append(addr)
        if len(li) == 1:
            addrs = li[0]
        else:
            addrs = ';'.join(li)
        return addrs

    def get_lowest(self, data):
        results = data
        ss = min([res.get('distance') for res in results])
        dic = {}
        for res in results:
            if res.get('distance') == ss:
                results.remove(res)
                dic = res
                break
        results.insert(0, dic)
        return results

    def get_name(self, data):
        '''
        获取地址名字
        :param dic:
        :return:
        '''
        mysql = Mysql()
        sql = 'select * from store'
        datas = mysql.getAll(sql)
        mysql.dispose()
        dic = json.loads(data).get('result').get('elements')
        dis = []
        for d in dic:
            for i in range(len(datas)):
                lat = float(datas[i].get('longitude'))
                lng = float(datas[i].get('latitude'))
                if lat == d.get('to').get('lat') and lng == d.get('to').get('lng'):
                    d['name'] = datas[i].get('name')
                    dis.append(d)
                    break
        return dis
