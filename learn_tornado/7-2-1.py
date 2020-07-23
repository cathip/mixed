# from tornado.httpclient import HTTPClient

# #同步访问
# def synchronous_visit():
#     http_client = HTTPClient()
#     response = http_client.fetch("http://www.baidu.com")
#     print('同步访问')

# synchronous_visit()


from tornado.httpclient import AsyncHTTPClient
#异步访问
def handle_response(response):
    print(response.body)
    print('异步访问')

def asynchronous_visit():
    http_client = AsyncHTTPClient()
    http_client.fetch("http://www.baidu.com", callback=handle_response)

if __name__ == "__main__":
    asynchronous_visit()