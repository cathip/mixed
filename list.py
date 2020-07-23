a = ['honda', 'yamaha', 'toyota', 'honda', 'suzuki']
b = {'zzz':1, 'bbb':2}
print(b['zzz'])
pop_a = a.pop(1)
print(a)
print(pop_a)
pop_b = a.pop()
print(a)
print(pop_b)
#remove移除整定值 从左开始只移除一个
a.remove('honda')
print(a)

l = [i for i in range(1,10000001)]
print(sum(l))