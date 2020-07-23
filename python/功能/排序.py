import operator
x = [{'name':'Homer', 'age':9}, {'name':'Homer', 'age':5}, {'name':'Bart', 'age':10}]  
sorted_x = sorted(x, key=operator.itemgetter('age'))  
print(sorted_x) 