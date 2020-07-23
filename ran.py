import random

#生成随机骰子
def getRan(n):
    list_a = []
    for x in range(n):
        list_a.append(random.randint(1,6))
    return list_a

userA = getRan(5)
userB = getRan(5)
print('玩家A骰子为：', userA)
print('玩家B骰子为：', userB)

#计算骰子总个数
def resultFuc(usera, userb):
    a = usera + userb
    b = set(a)
    result = []
    for each_b in b:
        count = 0
        for each_a in a:
            if each_b == each_a:
                count += 1
        result.append(tuple([each_b, count]))
    print('总个数', result)
    return result

result = resultFuc(userA, userB)

#判断输赢
def winner(chose, result, zhai=True):
    finish_list = []
    for i in result:
        if i[0] == chose[0]:
            finish_list.append(i)
        if i[0] == 1 and zhai:
            finish_list.append(i)
    print(finish_list)
    f = 0
    for x in finish_list:
        f += x[1]
    print(f)
    if f >= chose[1]:
        print('猜对了 获胜')
    else:
        print('错了 喝酒')

winner((2,8), result)

