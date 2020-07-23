import redis

class Open_Redis():
	
	def __init__(self):
		self.__SESSION_EXPIRE = 60
		self.__SESSION_TYPE = 'Redis'
		#redis地址
		self.__REDIS_HOST = '129.211.136.124'
		self.__REDIS_PASSWD = ""
		#redis端口
		self.__REDIS_PORT = 6379

	def getConn(self, db):
		pool = redis.ConnectionPool(host=self.__REDIS_HOST, 
									port=self.__REDIS_PORT, 
									password=self.__REDIS_PASSWD, 
									db=db, 
									max_connections=10)
		conn = redis.Redis(connection_pool=pool, decode_responses=True)
		return conn