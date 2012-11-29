'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import DishCategory
from cache_dish import getDish

CATEGORIES_KEY="CATS"

def createCategoryObject(categoryDb):
	categoryObject={
		'key':str(categoryDb.key()),
		'name':categoryDb.name,
		'basePrice':categoryDb.basePrice,
		'isMenu':categoryDb.isMenu,
		'canBeTopLevel':categoryDb.canBeTopLevel,
		'index':categoryDb.index
	}
	dishKeys=[]
	for dish in categoryDb.dishes:
		dishKeys.append(str(dish.key()))
	categoryObject['dishKeys'] = dishKeys
	return categoryObject
	
def getDishCategories():
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories == None:
		categories = DishCategory.all().order("index")
		categoryList=[]
		for category in categories:
			categoryObject=createCategoryObject(category);
			categoryList.append(categoryObject)
		client.set(CATEGORIES_KEY, categoryList)
		return categoryList
	return categories

def addCategory(category):
	client = memcache.Client()
	categoryObject=createCategoryObject(category)
	categories=client.get(CATEGORIES_KEY)
	client.set(str(category.key()), categoryObject)
	if categories != None:
		categories.append(categoryObject)
		client.set(CATEGORIES_KEY, categories)

def deleteCategory(key):
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories != None:
		categoryList=[]
		for category in categories:
			if category['key'] == key:
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
			if str(category.key()) == categoryObject['key']:
				categoryObject=createCategoryObject(category);
			categoryList.append(categoryObject)
		client.set(CATEGORIES_KEY, categoryList)

def getCategoryWithDishes(key):
	client = memcache.Client()
	category = client.get(key)
	if category == None:
		categoryDb = DishCategory.get(key)
		if categoryDb != None:
			category = createCategoryObject(categoryDb);
			client.set(key, category)
		else:
			return None
	# Fetch dishes
	dishes = []
	for dishKey in category['dishKeys']:
		dishes.append(getDish(dishKey))
	category['dishes'] = dishes
	return category