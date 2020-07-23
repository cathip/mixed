import re

info = []
for i in info:
    remark = i.get('remark')
    #reg = '<img src="(http.*?\.jpg)"'
    # img = re.compile(reg)
    # img_name = img.findall(remark)
    res = re.compile('http.*?class\_img')
    real_name = re.sub(res, 'https://test-1257765943.cos.ap-chengdu.myqcloud.com/new_img', remark)
    print(real_name)
    print('--------------------------')
    # if len(img_name) == 0:
    #     pass
    #     #print(len(img_name))
    # #html = etree.HTML(remark.text)
    # #img = html.xpath('//img/@src')
    # else:
    #     #print(img_name)
    #     for x in img_name:
    #         #print(x)
            
    #         print(real_name)
    #         print('---------------')   
    #         #img_name[x] = 