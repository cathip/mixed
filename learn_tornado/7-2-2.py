#迭代器 与 可迭代对象

#创建一个迭代器(Iterator) iter  
numbers = [1, 3, 5, 7, 8]
t = iter(numbers)
print(t)
print(next(t))
print(next(t))
print(next(t))
print(next(t))
print(next(t))
print('---------------------------------')
'''
此时如果 调用next方法的次数 超过 numbers的长度
返回 StopIteration 异常类 表示迭代已完成
'''

#在关键宇 in 后面接收的是 lterable 对象
#for循环本质就是 循环之前 生成一个迭代器 Iterator 
#然后调用其 next() 方法 直到 StopIteration
for number in range(5):
    print(number)