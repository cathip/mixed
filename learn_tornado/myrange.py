#真正的迭代器
class MyRange(object):

    def __init__(self, end):
        print('构造函数开始')
        self.start = 0
        self.end = end

    def __iter__(self):
        print('生成器开始')
        return self

    def __next__(self):
        print('迭代进行')
        if self.start < self.end:
            ret = self.start
            self.start += 1
            return ret
        else:
            raise StopIteration


for i in MyRange(10):
    print(i)

myrang = MyRange(8)

from collections.abc import *
print(isinstance(myrang, Iterable))
print(isinstance(myrang, Iterator))

def newMyRange(end):
    start = 0
    while start < end:
        yield start
        start += 1

for i in newMyRange(7):
    print(i)

print(isinstance(newMyRange(7), Iterable))
print(type(newMyRange(7)))
print(isinstance(newMyRange(7), Iterator))

a = newMyRange(2)
next(a)
next(a)
#next(a)
#抛出StopIteration



#yield有返回值
def xMyRange(end):
    start = 0
    while start < end:
        x = yield start  # 这里增加了获取返回值
        print('-------x---------')
        print(x)  # 打印出来
        print('-------x---------')
        start += 1

m = xMyRange(5)
print(next(m))
print('zzzzzzzzzz')
print(m.send(4))
print('zzzzzzzzzz')
print(m.send(3))
print('zzzzzzzzzz')
print(m.send(0))
print('zzzzzzzzzz')
print(m.send('hhhh'))
#如果send 方法超过yield 那么会抛出StopIteration异常
# for i in m:
#     print(i)
    