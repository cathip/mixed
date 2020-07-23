from urllib import request
import os
ua_list = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64)','AppleWebKit/537.36 (KHTML, like Gecko)', 'Chrome/78.0.3904.108', 'Safari/537.36']
import time
import random
import re
import requests
from lxml import etree

class MeiziSpider():
    def __init__(self):
        self.url = 'https://www.mzitu.com/all/'

    def get_html(self, url):
        headers = {'User-Agent': random.choice(ua_list)}
        req = request.Request(url=url, headers=headers)
        res = request.urlopen(req)
        html = res.read()
        return html
        # print(html)

    def re_func(self, re_bds, html):
        pattern = re.compile(re_bds, re.S)
        r_list = pattern.findall(html)
        return r_list

    # 获取想要的数据 - 解析一级页面
    # def parse_html(self, url):
    #     one_html = self.get_html(url).decode()
    #     # print(one_html)
    #     re_bds = '<p class="url">.*?<a href="(.*?)" target="_blank">(.*?)</a>'
    #     one_list = self.re_func(re_bds, one_html)
    #     # print(one_list)
    #     # time.sleep(random.randint(1, 3))
    #     self.write_html(one_list)


    def parse_html(self,url):
        html = self.get_html(url).decode()
        parse_obj = etree.HTML(html)
        href_list = parse_obj.xpath('//div[@class="all"]/ul[@class="archives"]/li/p[@class="url"]/a/@href')
        print("href_list:",href_list)
        self.write_html(href_list)





    def write_html(self, href_list):
        for href in href_list:
            two_url = href
            print(two_url)
            time.sleep(random.randint(1, 3))
            self.save_image(two_url)

    def save_image(self, two_url):
        headers = {'Referer': two_url, 'User-Agent': random.choice(ua_list)}
        print('---------two_url-----------', two_url)
        # 向图片链接发请求.得到bytes类型
        i = 0
        while True:
            try:
                img_link = two_url + '/{}'.format(i)
                print("img_link:", img_link)
                html = requests.get(url=img_link, headers=headers).text
                re_bds = ' <div class="main-image"><p><a href="https://www.mzitu.com/.*?" ><img ' \
                         'src="(.*?)" alt="(.*?)" width=".*?" height=".*?" /></a></p>'
                img_html_list = self.re_func(re_bds, html)
                print("img_html_list", img_html_list)
                name = img_html_list[0][1]
                print("-----name:",name)
                direc = '/home/ubuntu/meizi/{}/'.format(name)
                print("direc:",direc)
                if not os.path.exists(direc):
                    os.makedirs(direc)
                img_ = requests.get(url=img_html_list[0][0], headers=headers).content
                filename = direc + name + img_link.split('/')[-1] + '.jpg'
                # print("img_:",img_)
                with open(filename, 'wb') as f:
                    f.write(img_)
                i += 1
            except Exception as e:
                break


if __name__ == '__main__':
    spider = MeiziSpider()
    spider.parse_html('https://www.mzitu.com/all')
