#utf-8
import os
import json
import time
import base64


class Imghand:

    def __init__(self):
        self.imgpath = "/home/ubuntu/img/"

    def uploadImg(self, img):
        '''
        :图片上传
        :param img:上传的图片
        :return:
        '''
        imgname = self.imgpath + str(int(time.time())) + '.png'
        if isinstance(img, str):
            myfiles = img
        else:
            myfiles = json.loads(img)
        if len(myfiles):
            imgdata = base64.b64decode(myfiles)
            with open(imgname, 'wb+') as f:
                f.write(imgdata)
            return imgname

    def upload_manyimg(self, img):
        myfiles = json.loads(img)
        imgurls = []
        if len(myfiles):
            myfiles = myfiles[:-1].split(';')
            for myfile in myfiles:
                imgname = self.imgpath + str(int(time.time())) + '.png'
                imgurls.append(imgname)
                time.sleep(1)
                imgdata = base64.b64decode(myfile)
                with open(imgname, 'wb+') as f:
                    f.write(imgdata)
        return imgurls