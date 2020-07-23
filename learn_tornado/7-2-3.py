#生成器的使用

#传统生成器

class New_Iter(object):

    def __init__(self):
        self.data = [2, 4, 8]
        self.step = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.step >= len(self.data):
            raise StopIteration
        data = self.data[self.step]
        print (f"I'm in the idx:{self.step} call of next ()")
        self.step += 1
        return data

for i in New_Iter():
    print(i)

print('--------------使用yield 生成器--------------')

#使用yield 生成器
def myIter():
    for i, data in enumerate([1, 3, 9]):
        print (f"I'm in the idx:{i} call of next ()")
        yield data

for i in myIter():
    print(i)