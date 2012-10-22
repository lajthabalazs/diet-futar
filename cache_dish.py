'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import Dish
from cache_helper import createDishObjectDb
	
def removeDishFromCategory(categoryKey, dishKey):
	client = memcache.Client()
	category = client.get(categoryKey)
	# If not in memcache, does nothing
	if category != None:
		dishKeys=[]
		for key in category.dishKeys:
			if key != dishKey:
				dishKeys.append(key)
		category['disheKeys'] = dishKeys
		client.set(categoryKey, category)


def addDishToCategory(categoryKey, dishKey):
	client = memcache.Client()
	category = client.get(categoryKey)
	if category != None:
		dishKeys=[]
		for key in category.dishKeys:
			if key != dishKey:
				dishKeys.append(key)
				# Save modified value
			dishKeys.append(dishKey)
			category['disheKeys'] = dishKeys
			client.set(key, category)

def getDish(key):
	client = memcache.Client()
	dish = client.get(key)
	if dish == None:
		dishDb = Dish.get(key)
		if dishDb != None:
			dish = createDishObjectDb(dishDb)
			client.set(key, dish)
			return dish
	else:
		return dish

# Modify dish
def modifyDish(dishDb):
	client = memcache.Client()
	key = str(dishDb.key())
	# Update dishes old category
	dishObject = getDish(key)
	categoryKey = str(dishDb.category.key())
	if dishObject != None and dishObject["categoryKey"] != categoryKey:
		# Update category objects in cacge
		removeDishFromCategory(dishObject["categoryKey"], key)
	# Create object
	newDishObject = createDishObjectDb(dishDb)
	if dishObject == None or dishObject["categoryKey"] != categoryKey:
		addDishToCategory(categoryKey, key)
	client.set(key, newDishObject)

# Adds a dishDb to the cache
def addDish(dishDb):
	client = memcache.Client()
	key = str(dishDb.key())
	if dishDb.category != None:
		categoryKey = str(dishDb.category.key())
		addDishToCategory(categoryKey, key)
	dishObject = createDishObjectDb(dishDb)
	client.set(str(dishDb.key()), dishObject)

# Delete dish from cache
def deleteDish(key):
	client = memcache.Client()
	dishObject = client.get(key)
	if dishObject == None:
		return
	else:
		removeDishFromCategory(dishObject["categoryKey"], key)
		client.delete(key)