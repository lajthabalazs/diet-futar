'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import ZipCodes
def getZipCodeEntry(code):
	client = memcache.Client()
	costs = client.get("zip_code_cost_" + str(code))
	# If not in memcache, does nothing
	if costs != None:
		return costs
	else:
		rawCodes = ZipCodes.all().get()
		if (rawCodes == None):
			return None
		ret = None
		for code in rawCodes.deliveryCosts:
			parts=code.rsplit(" ")
			key = "zip_code_cost_" + parts[0]
			costs = {
					'cost':int(parts[1]),
					'limit':int(parts[2])
				}
			client.add(key, costs)
			if parts[0] == str(code):
				ret = costs
		return ret

def updateZipCodeScript(rawCodes):
	client = memcache.Client()
	costArrayScript = "{"
	limitArrayScript = "{"
	if (rawCodes == None):
		return
	for code in rawCodes.deliveryCosts:
		parts=code.rsplit(" ")
		costArrayScript = costArrayScript + "c" + parts[0] + ": '" + parts[1] + "',\n"
		limitArrayScript = limitArrayScript + "c" + parts[0] + ": '" + parts[2] + "',\n"
	costArrayScript = costArrayScript + "}"
	limitArrayScript = limitArrayScript + "}"
	client.add("costArrayScript", costArrayScript)
	client.add("limitArrayScript", limitArrayScript)

def getCostArrayScript():
	client = memcache.Client()
	costArrayScript = client.get("costArrayScript")
	if costArrayScript == None:
		updateZipCodeScript(ZipCodes.all().get())
	return client.get("costArrayScript")

def getLimitArrayScript():
	client = memcache.Client()
	limitArrayScript = client.get("limitArrayScript")
	if limitArrayScript == None:
		updateZipCodeScript(ZipCodes.all().get())
	return client.get("limitArrayScript")

def updateZipCodeEntry(code, cost, limit):
	client = memcache.Client()
	key = "zip_code_cost_" + str(code)
	client.add(key, {
					'cost':cost,
					'limit':limit
				})
	updateZipCodeScript()