class Stack():

    '''堆栈'''

    def __init__(self, size):
        self.size = size
        self.stack = []
        self.top = -1

    def isfull(self):
        return self.top + 1 == self.size

    def isempty(self):
        return self.top == -1

    def showStack(self):
            print(self.stack)

    def pop(self):
        if self.isempty():
            raise Exception("stack is empty")
        else:
            self.top = self.top - 1
            self.stack.pop()

    def push(self, x):
        if self.isfull():
            raise Exception('stack is full')
        else:
            self.stack.append(x)
            self.top = self.top + 1

    def clear(self):
        self.stack.clear()

S = Stack(10)
for i in range(5):
    S.push(i)
S.showStack()
for i in range(3):
    S.pop()
S.showStack()


class Queue():

    '''队列'''

    def __init__(self, size):
        self.size = size
        self.front = -1
        self.rear = -1
        self.queue = []

    def isfull(self):
        return self.rear - self.front +1 == self.size

    def isempty(self):
        return self.front == self.rear

    def showQueue(self):
        print(self.queue)

    def enqueue(self, ele):
        if self.isfull():
            raise Exception("queue is full")
        else:
            self.queue.append(ele)
            self.rear = self.rear + 1
    
    def dequeue(self):
        if self.isempty():
            raise Exception("queue is empty")
        else:
            self.queue.pop(0)
            self.front = self.front + 1

Q = Queue(10)
for i in range(5):
    Q.enqueue(i)
Q.showQueue()
for i in range(4):
    Q.dequeue()
Q.showQueue()