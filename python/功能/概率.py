from random import randint

num = randint(1, 100)

print(num)
# 10
# 11
# 19
# 10
# 10
# 10
# 10
# 30

#第一
if num in range(1, 6):
    pass
#第二
elif num in range(6, 10):
    pass
#第三
elif num in range(6, 10):
    pass
#第四
elif num in range(6, 10):
    pass
#第五
elif num in range(6, 10):
    pass
#第六
elif num in range(6, 10):
    pass
#第七
elif num in range(6, 10):
    pass
#第八
elif num in range(6, 10):
    pass

while True:
    list_1 = [1,2,3]
    list_2 = [2,3,4]
    list_1.append(list_2)
    list_2.append(list_1)
print(list_2)
print(list_1)
list_2 = []
print(list_2)