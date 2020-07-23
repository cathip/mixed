li = [i for i in range(10)]
print(li)

def mulTen(n):
    return n * 10

# for i in map(mulTen, li):
#     print(i)

li1 = list(map(mulTen, li))
#print(li1)

