'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import IngredientCategory
from cache_helper import createIngredientCategoryDb, createIngredientDb

CATEGORIES_KEY="INGREDIENTS_CATS"

def getIngredientCategories():
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories == None:
		categories = IngredientCategory.all().order("name")
		categoryList=[]
		for category in categories:
			categoryList.append(createIngredientCategoryDb(category))
		client.set(CATEGORIES_KEY, categoryList)
		return categoryList
	return categories

def addIngredientCategory(category):
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories != None:
		categories.append(createIngredientCategoryDb(category))
		client.set(CATEGORIES_KEY, categories)

def deleteIngredientCategory(key):
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

def modifyIngredientCategory(category):
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories != None:
		categoryList=[]
		for categoryObject in categories:
			if category.key == categoryObject.key:
				categoryObject['name'] = category.name
			categoryList.append(categoryObject)
		client.set(CATEGORIES_KEY, categoryList)

def getIngredientCategoryWithIngredients(key):
	client = memcache.Client()
	category = client.get(key)
	if category == None:
		categoryDb = IngredientCategory.get(key)
		if categoryDb != None:
			ingredient = []
			for ingredientDb in categoryDb.ingredients:
				ingredient.append(createIngredientDb(ingredientDb))
			category={
				'key':key,
				'name':categoryDb.name,
				'ingredients':ingredient
			}
			client.set(key, category)
		else:
			return None
	return category