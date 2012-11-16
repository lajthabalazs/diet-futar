'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import Dish
from cache_helper import createDishObjectDb
	
ALL_DISHES="avilable_dishes"

def removeDishFromCategory(categoryKey, dishKey):
	client = memcache.Client()
	category = client.get(categoryKey)
	# If not in memcache, does nothing
	if category != None:
		dishKeys=[]
		for key in category['dishKeys']:
			if key != dishKey:
				dishKeys.append(key)
		category['dishKeys'] = dishKeys
		client.set(categoryKey, category)


def addDishToCategory(categoryKey, dishKey):
	client = memcache.Client()
	category = client.get(categoryKey)
	if category != None:
		dishKeys=[]
		for key in category['dishKeys']:
			if key != dishKey:
				dishKeys.append(key)
				# Save modified value
		dishKeys.append(dishKey)
		category['dishKeys'] = dishKeys
		client.set(categoryKey, category)

def getDish(key):
	client = memcache.Client()
	dish = client.get(key)
	if dish == None:
		dishDb = Dish.get(key)
		if dishDb != None:
			dish = createDishObjectDb(dishDb)
			client.set(dish['key'], dish)
	return dish

# Modify dish
def modifyDish(key, title, subtitle, description, dishCategoryDb):
	dishDb = Dish.get(key)
	client = memcache.Client()
	dishDb.title = title
	dishDb.subtitle = subtitle
	dishDb.description = description
	dishDb.category = dishCategoryDb
	# Update dishes old category
	dishObject = getDish(key)
	categoryKey = None
	if dishDb.category != None:
		categoryKey = str(dishDb.category.key())
	if dishObject != None and dishObject["category"]!= None and dishObject["category"]['key'] != categoryKey:
		# Update category objects in cacge
		removeDishFromCategory(dishObject["category"]['key'], key)
	# Create object
	newDishObject = createDishObjectDb(dishDb)
	dishDb.price = int(newDishObject['price'])
	if ( dishObject == None or dishObject["category"] != categoryKey ) and categoryKey != None:
		addDishToCategory(categoryKey, key)
	client.set(key, newDishObject)
	dishDb.put()

# Adds a dishDb to the cache
def addDish(dishDb):
	client = memcache.Client()
	key = str(dishDb.key())
	if dishDb.category != None:
		categoryKey = str(dishDb.category.key())
		addDishToCategory(categoryKey, key)
	dishKeys = client.get(ALL_DISHES)
	if dishKeys != None:
		dishKeys.append(str(dishDb.key()))
		client.set(ALL_DISHES, dishKeys)
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
	dishKeys = client.get(ALL_DISHES)
	# If not in memcache, does nothing
	if dishKeys != None:
		dishKeys=[]
		for actualKey in dishKeys:
			if actualKey != key:
				dishKeys.append(actualKey)
		client.set(ALL_DISHES, dishKeys)

		
def getDishes():
	client = memcache.Client()
	dishKeys = client.get(ALL_DISHES)
	if dishKeys == None:
		dishKeys=[]
		dishes = Dish.gql("ORDER BY title")
		if dishes != None:
			for dish in dishes:
				dishKeys.append(str(dish.key()))
			client.set(ALL_DISHES, dishKeys)
		else:
			return None
	# Fetch dishes
	dishes = []
	for dishKey in dishKeys:
		dishes.append(getDish(dishKey))
	return dishes
