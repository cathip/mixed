from tornado import gen
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient
from concurrent.futures import ThreadPoolExecutor

@gen.coroutine
def coroutine_vist():
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch('http://www.baidu.com')
    print(response.body)

@gen.coroutine
def out_coroutine():
    print("start call")
    yield coroutine_vist()
    print('end call')

def func_normal():
    print('start call')
    IOLoop.current().run_sync(lambda: coroutine_vist())
    print('end call')

'''
本例中 spawn_callback() 函数将不会等待被调用协程执行完成，所以 spawn_callback（）之前和
之后的 print 语句将会被连续执行，而 coroutine_visit 本身将会由 IOLoop 在合适的时机进行调用
IO Loop 的 spawn_callback（）函数没有为开发者提供获取协程函数调用返回值的方法，所以
只能用 spawn callback（）调用没有返回值的协程函数
'''
def func_normal1():
    print('start call')
    IOLoop.current().spawn_callback(coroutine_vist)
    print('end call')

func_normal()


