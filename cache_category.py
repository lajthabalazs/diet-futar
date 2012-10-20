'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import DishCategory
from google.appengine.ext import db

CATEGORIES_KEY="CATS"

def getCategories():
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories == None:
		categories = DishCategory.all().order("index")
		categoryList=[]
		for category in categories:
			categoryObject={
				'key':str(category.key()),
				'name':category.name,
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
	if categories == None:
		categoryList=[]
		for categoryObject in categories:
			if category.key == categoryObject.key:
				categoryObject['name'] = category.name
				categoryObject['isMenu'] = category.isMenu
				categoryObject['index'] = category.index
				categoryObject['dishes'] = categoryObject.dishes
			categoryList.append(categoryObject)
		client.set(CATEGORIES_KEY, categoryList)

def getCategoryWithDishes(key):
	client = memcache.Client()
	category = client.get(key)
	if category == None:
		categoryDb = DishCategory.get(key)
		if categoryDb != None:
			dishKeys=[]
			for dish in category.dishes:
				dishKeys.append(str(dish.key()))
				category={
				'key':key,
				'name':category.name,
				'isMenu':category.isMenu,
				'index':category.index,
				'dishesKeys':dishKeys
			}
			client.set(key, category)
		else:
			return None
	return category

