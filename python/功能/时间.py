import time
import random
#时间戳
str_time = str(int(time.time()))
num = str(random.randint(1,100))
img_name = str_time + num + '.png'
print(img_name)