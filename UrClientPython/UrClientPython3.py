import myrequests as requests
import pymultihash as pmh
import time
import random

MAX_RETRYS = 10

def dial(target, cmd, **kwargs):

	buildURL = [target["addr"]]
	buildURL.append("api/v0/client/")
	buildURL.append(cmd)
	buildURL.append("/")
	postData = None
	if cmd == "seek" or cmd == "get":
		buildURL.append(kwargs["id"])
	elif cmd == "poll":
		buildURL.append(kwargs["id"])
		buildURL.append("/")
		buildURL.append(str(kwargs["time"]))
	elif cmd == "post":
		buildURL.append(kwargs["id"])
		postData = kwargs["data"]
	elif cmd == "store":
		buildURL.append(kwargs["id"])
		postData = kwargs["data"]

	trgAddr = ''.join(buildURL)
	print("dial", trgAddr)
	if postData is not None:
		r = requests.post(trgAddr, data=postData)
		return None
	else:
		r = requests.get(trgAddr)
		if cmd == "get":
			return r.text
		elif cmd == "poll" or cmd == "seek":
			return r.json()
		

class UrDHTClient(object):
	def __init__(self, apiStr, bootstraps):
		self.apiStr = apiStr
		self.knownPeers = bootstraps

	def hash(self, string):
		return pmh.genHash(self.apiStr+string,0x12)

	def lookup(self,targetID):
		serverStack = self.knownPeers[:]#I think this is kinda elegant.
		#it will try all the known peers before failing
		random.shuffle(serverStack)
		while(len(serverStack)>0):
			try:
				nextHop = dial(serverStack[-1],"seek",id=targetID)
				if serverStack[-1]["id"] == nextHop["id"]:
					return nextHop
				else:
					serverStack.append(nextHop)
			except:
				print(serverStack.pop(),"failed dial")

			if len(serverStack) == 0:
				raise Exception("lookup failed")


	def get(self,key):
		try:
			target_id = self.hash(key)
			target_peer = self.lookup(target_id)
			result = dial(target_peer,"get",id=target_id)
		except:
			return self.get(key)
		return result

	def store(self,key, data):
		try:
			target_id = self.hash(key)
			target_peer = self.lookup(target_id)
			dial(target_peer,"store",id=target_id,data=data)
		except:
			return self.store(key,data)

	def post(self,key, data):
		try:
			target_id = self.hash(key)
			target_peer = self.lookup(target_id)
			dial(target_peer,"post",id=target_id,data=data)
		except:
			return self.post(key,data)


	def poll(self,key, time):
		try:
			target_id = self.hash(key)
			target_peer = self.lookup(target_id)
			return dial(target_peer,"poll",id=target_id,time=time)
		except:
			return self.poll(key,time)





def quickTest():
	for k in range(100):
		bootstrap = {"id":"QmadXgpUy2sSkjNfsAD9o7Y44jGY8LB8wpAukUXKeNYmjo", "addr":"http://73.207.38.249:8000/", "wsAddr":"ws:/73.207.38.249:8001"}
		key = "foo"+str(k)
		c = UrDHTClient("",[bootstrap])
		teststr = "hello world"+str(k)
		c.store(key,teststr)
		assert(c.get(key)==teststr)
		c.post(key,teststr)
		results = c.poll(key,0)
		print("results",results)
		strings = map(lambda x: x[1], results)

		assert(repr(bytes(teststr,"UTF-8")) in strings)

quickTest()


