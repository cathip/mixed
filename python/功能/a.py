s = 'tm20190410155113125'
v = 'oxnmC1q927W4iEq1IEx99g-SZtU'
a = [{'or_actinum': 'di20190410155019788', 'or_openid': 'oxnmC1q927W4iEq1IEx99g-SZtUk'}, {'or_actinum': 'ft20190410155050321', 'or_openid': 'oxnmC1q927W4iEq1IEx99g-SZtUk'}, {'or_actinum': 'di20190410155019788', 'or_openid': 'oxnmC1q927W4iEq1IEx99g-SZtUk'}, {'or_actinum': 'tm20190410155113125', 'or_openid': 'oxnmC1q927W4iEq1IEx99g-SZtUk'}, {'or_actinum': 'tm20190410155113125', 'or_openid': 'oxnmC1q927W4iEq1IEx99g-SZtUk'}, {'or_actinum': 'tm20190410155113125', 'or_openid': 'oxnmC1q927W4iEq1IEx99g-SZtUk'}, {'or_actinum': 'tm20190410155113125', 'or_openid': 'oxnmC1q927W4iEq1IEx99g-SZtUk'}, {'or_actinum': 'ft20190410155050321', 'or_openid': 'oxnmC1q927W4iEq1IEx99g-SZtUk'}]
b = []
c = []
for i in range(len(a)):
    b.append(a[i].get('or_actinum'))
    c.append(a[i].get('or_openid'))
print(b)
print(c)
if s in b and v in c:
    print('在里面')
