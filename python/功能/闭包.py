import json
import re
import sys
from random import randint
#最多两个函数
def ExFunc(n):
     sum=n
     def InsFunc(x):
        print(sum+x)
     return InsFunc
for i in range(5):
    xz = i + 10
    yz = i + 20
    myFunc=ExFunc(50)
    myFunc(10)

url = 'www.baidu.com'
print(re.match('www', url).span())
print(sys.path)


def rand():
   x = randint(1,3)
   print('rand')
   print(x)
   return x

def reward():
   x = rand()
   print('reward')
   print(x)
   if x == 3:
      return 999
   else:
      reward()
      
reward()
      
