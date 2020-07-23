#utf-8


import base64
import json
from Crypto.Cipher import AES

from base.wx_config import GZH_APPID


class WXBizDataCrypt:
    def __init__(self, sessionKey):
        self.appId = GZH_APPID
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)

        decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)))

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        print('加密前:------------')
        print(s)
        print('加密后:------------')
        print(s[:-ord(s[len(s)-1:])])
        return s[:-ord(s[len(s)-1:])]