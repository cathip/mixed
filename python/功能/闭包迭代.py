a = [1,2,3,4,5,6,7]

def p():
	def start(x,y):
		for i in range(x): 
			y.pop()
		return y
	return start

z = p()
l = z(2,a)
print(l)

def run(c):
    c+=1
    if c == 3:
        return 1
    else:
        return run(c)
    
x = run(c=1)
print(x)