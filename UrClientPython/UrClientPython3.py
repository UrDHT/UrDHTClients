import myrequests as requests
import pymultihash as pmh
import time
import random

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
		buildURL.append(kwargs["time"])
	elif cmd == "post":
		buildURL.append(kwargs["id"])
		postData = kwargs["data"]
	elif cmd == "store":
		buildURL.append(kwargs["id"])
		postData = kwargs["data"]

	trgAddr = ''.join(buildURL)
	if postData is not None:
		r = requests.post(trgAddr, data=postData)
		return r.json()
	else:
		r = requests.get(trgAddr)
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
		nextHop = None
		while(not nextHop or nextHop["id"]!=serverStack[-1]["id"]):
			try:
				nextHop = dial(serverStack[-1],"seek",id=targetID)
			except:
				print(serverStack.pop(),"failed dial")

			if len(serverStack) == 0:
				raise Exception("lookup failed")
		return nextHop



bootstrap = {"id":"5du2nPHVMXejLeQM14Dbxv18ErUPTb", "addr":"http://127.0.0.1:8000/", "wsAddr":"ws://127.0.0.1:8001"}

c = UrDHTClient("",[bootstrap])
print(c.lookup("5du2nPHVMXejLeQM14Dbxv18ErUPTb"))
