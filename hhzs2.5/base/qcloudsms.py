import time
import datetime

from qcloudsms_py import SmsSingleSender
from qcloudsms_py import SmsMobileStatusPuller
from qcloudsms_py.httpclient import HTTPError

from base.shop_base import randomNumber
from base.Predis import Open_Redis


appid = 1400135199
appkey = "5b103eb2d75a3a6e7923d1119b095a72"
#phone_numbers = ["18607776985"]
template_id = 186527 
sms_sign = "腾讯云"
params = ["186527"]  # 当模板没有参数时，`params = []`

#发送短信
def sendSms(phone_numbers):
  ssender = SmsSingleSender(appid, appkey)
  code = randomNumber()
  msg = f'{code}为您的验证码'
  result = ssender.send(0, 86, phone_numbers, msg) 
  conn = Open_Redis().getConn(7)
  conn.set(phone_numbers, str(code), 60)
  print('返回值')
  print(result)
  code = code if result.get('result') == 0 else False
  return code

#拉取短信
def pullSms(phone_numbers):
  now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  # 转为时间数组
  now = time.strptime(now, "%Y-%m-%d %H:%M:%S")
  # 转为时间戳
  now = int(time.mktime(now))
  begin_time = now - 2000
  end_time = now    # 结束时间（UNIX timestamp）
  max_num = 10             # 单次拉取最大量
  mspuller = SmsMobileStatusPuller(appid, appkey)
  try:
    # 拉取短信回执
    callback_result = mspuller.pull_callback("86", phone_numbers,
        begin_time, end_time, max_num)
    # 拉取回复，国际/港澳台短信不支持回复功能
    reply_result = mspuller.pull_reply("86", phone_numbers,
        begin_time, end_time, max_num)
    print(callback_result)
    print(reply_result)
    return callback_result, reply_result
  except HTTPError as e:
    print(e)
  except Exception as e:
    print(e)