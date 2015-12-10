import myrequests as requests
import pymultihash as pmh
import time
import random
import json

def bootstrapSubnet(subnet,UrDHTPeers):
	c = UrDHTClient("UrDHT",UrDHTPeers)
	subnetPeers = []
	peerListMessages = c.poll(self.hash(subnet),0)
	if len(peerList) == 0:
		raise Exception("No sponsoring Peers found")
	else:
		for m in peerListMessages:
			pString = m[1]
			peer = json.loads(pString)
			subnetPeers.append(peer)
		return UrDHTClient(subnet,subnetPeers)

def dial(subnet,target, cmd, **kwargs):

	buildURL = [target["addr"]]
	buildURL.append(subnet+"/client/")
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
	if postData is not None:
		r = requests.post(trgAddr, data=postData)
		if r.text:
			return r.json()
	else:
		r = requests.get(trgAddr)
		#print(r.text)
		if len(r.text)>0:
			if cmd == "get":
				return r.text
			else:
				return r.json()

class UrDHTClient(object):
	def __init__(self, subnet, bootstraps):
		self.subnet = subnet
		self.knownPeers = bootstraps

	def hash(self, string):
		return pmh.genHash(string,0x12)

	def lookup(self,targetID):
		serverStack = self.knownPeers[:]#I think this is kinda elegant.
		#it will try all the known peers before failing
		random.shuffle(serverStack)
		nextHop = None
		current = serverStack.pop()
		while True:
			try:
				nextHop = dial(self.subnet,current,"seek",id=targetID)
				if nextHop == current:
					break
				current =  nextHop
			except:
				current =  serverstack.pop()
				print(current,"failed dial")
		return nextHop

	def get(self,key):
		target_id = self.hash(key)
		target_peer = self.lookup(target_id)
		result = dial(self.subnet,target_peer,"get",id=target_id)
		return result

	def store(self,key, data):
		target_id = self.hash(key)
		target_peer = self.lookup(target_id)
		dial(self.subnet,target_peer,"store",id=target_id,data=data)

	def post(self,key, data):
		target_id = self.hash(key)
		target_peer = self.lookup(target_id)
		dial(self.subnet,target_peer,"post",id=target_id,data=data)

	def poll(self,key, time):
		target_id = self.hash(key)
		target_peer = self.lookup(target_id)
		return dial(self.subnet,target_peer,"poll",id=target_id,time=time)


bootstrap = {"id":"QmUyLNdX8S1LoM2v1RvbzEF89WzYwqGz5YjndrCk5pNurX", "addr":"http://127.0.0.1:8000/"}

c = UrDHTClient("websocket",[bootstrap])
for x in range(100):
	#c.store("foo%d"%x,"hello world%d"%x)
	print(c.get("foo%d"%x))
