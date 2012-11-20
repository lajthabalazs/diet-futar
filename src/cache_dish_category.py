'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import DishCategory
from cache_dish import getDish

CATEGORIES_KEY="CATS"

def getDishCategories():
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories == None:
		categories = DishCategory.all().order("index")
		categoryList=[]
		for category in categories:
			categoryObject={
				'key':str(category.key()),
				'name':category.name,
				'basePrice':category.basePrice,
				'isMenu':category.isMenu,
				'index':category.index
			}
			categoryList.append(categoryObject)
		client.set(CATEGORIES_KEY, categoryList)
		return categoryList
	return categories

def addCategory(category):
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories != None:
		categoryObject={
			'key':str(category.key()),
			'name':category.name,
			'basePrice':category.basePrice,
			'isMenu':category.isMenu,
			'index':category.index
		}
		categories.append(categoryObject)
		client.set(CATEGORIES_KEY, categories)

def deleteCategory(key):
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories != None:
		categoryList=[]
		for category in categories:
			if category.key == key:
				continue
			else:
				categoryList.append(category)
		client.set(CATEGORIES_KEY, categoryList)

def modifyCategory(category):
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories != None:
		categoryList=[]
		for categoryObject in categories:
			dishKeys=[]
			for dish in category.dishes:
				dishKeys.append(str(dish.key()))
			if category.key == categoryObject.key:
				categoryObject['name'] = category.name
				categoryObject['isMenu'] = category.isMenu
				categoryObject['index'] = category.index
				categoryObject['basePrice'] = category.basePrice
				categoryObject['dishKeys'] = categoryObject.dishKeys
			categoryList.append(categoryObject)
		client.set(CATEGORIES_KEY, categoryList)

def getCategoryWithDishes(key):
	client = memcache.Client()
	category = client.get(key)
	if category == None:
		categoryDb = DishCategory.get(key)
		if categoryDb != None:
			dishKeys=[]
			for dish in categoryDb.dishes:
				dishKeys.append(str(dish.key()))
			category={
				'key':key,
				'name':categoryDb.name,
				'isMenu':categoryDb.isMenu,
				'index':categoryDb.index,
				'basePrice':category.basePrice,
				'dishKeys':dishKeys
			}
			client.set(key, category)
		else:
			return None
	# Fetch dishes
	dishes = []
	for dishKey in category['dishKeys']:
		dishes.append(getDish(dishKey))
	category['dishes'] = dishes
	return category