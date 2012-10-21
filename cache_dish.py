'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import Dish
from google.appengine.ext import db

def removeDishFromCategory(categoryKey, dishKey):
	client = memcache.Client()
	category = client.get(categoryKey)
	# If not in memcache, does nothing
	if category != None:
		dishKeys=[]
		for key in category.dishKeys:
			if key != dishKey:
				dishKeys.append(key)
		categoryObject={
			'key':category.key,
			'name':category.name,
			'isMenu':category.isMenu,
			'index':category.index,
			'disheKeys':dishKeys
		}
		client.set(categoryKey, categoryObject)


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
			categoryObject={
				'key':category.key,
				'name':category.name,
				'isMenu':category.isMenu,
				'index':category.index,
				'dishKeys':dishKeys
			}
			client.set(key, categoryObject)
			return categoryObject
	else:
		return category

def getDish(key):
	client = memcache.Client()
	dish = client.get(key)
	if dish == None:
		dish = Dish.get(key)
		if dish != None:
			dishDict={
				'key':key,
				'title':dish.title,
				'categoryKey':str(dish.category.key()),
				'price':dish.price
			}
			client.set(key, dishDict)
			return dishDict
	else:
		return dish

# Modify dish
def modifyDish(dish):
	client = memcache.Client()
	key = str(dish.key())
	# Update dishes old category
	dishObject = getDish(key)
	categoryKey = str(dish.category.key())
	if dishObject != None and dishObject["categoryKey"] != categoryKey:
		# Update category objects in cacge
		removeDishFromCategory(dishObject["categoryKey"], key)
	# Create object
	dishDict={
		'key':key,
		'title':dish.title,
		'categoryKey':categoryKey,
		'price':dish.price
	}
	if dishObject == None or dishObject["categoryKey"] != categoryKey:
		addDishToCategory(categoryKey, key)
	client.set(key, dishDict)

# Adds a dish to the cache
def addDish(dish):
	client = memcache.Client()
	key = str(dish.key())
	categoryKey = str(dish.category.key())
	dishDict={
		'key':key,
		'title':dish.title,
		'categoryKey':categoryKey,
		'price':dish.price
	}
	addDishToCategory(categoryKey, key)
	client.set(str(dish.key()), dishDict)

# Delete dish from cache
def deleteDish(key):
	client = memcache.Client()
	dishObject = client.get(key)
	if dishObject == None:
		return
	else:
		removeDishFromCategory(dishObject["categoryKey"], key)
		client.delete(key)