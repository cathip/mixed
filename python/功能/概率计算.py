from random import randint

num = randint(1, 100)
list_a = [1,10,20,20,10,10,10,19]
print(sum(list_a))
a = sum(list_a[0:1]) + 1
b = sum(list_a[0:2]) + 1
c = sum(list_a[0:3]) + 1
d = sum(list_a[0:4]) + 1
e = sum(list_a[0:5]) + 1
f = sum(list_a[0:6]) + 1
g = sum(list_a[0:7]) + 1
h = sum(list_a[0:8]) + 1

if num in list(range(1, a)):
    print('第一个')
elif num in list(range(a, b)):
    print('第二个')
elif num in list(range(b, c)):
    print('第三个')
elif num in list(range(c, d)):
    print('第四个')
elif num in list(range(d, e)):
    print('第五个')
elif num in list(range(e, f)):
    print('第六个')
elif num in list(range(f, g)):
    print('第七个')
elif num in list(range(g, h)):
    print('第八个')