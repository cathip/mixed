import jwt
import datetime

from hhsc2019.settings import SECRET_KEY

def getToken(data : dict, hours : int) -> str: 
    if not isinstance(data, dict):
        raise Exception('生成token错误')
    header = {
                'type' : 'jwt',
                'alg' : 'HS256'
            }
    payload = data
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
    
    token = jwt.encode(headers=header, 
        payload=payload, 
        key=SECRET_KEY, 
        algorithm='HS256').decode('utf-8')
    return token