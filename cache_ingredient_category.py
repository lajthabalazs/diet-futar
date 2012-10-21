'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import IngredientCategory
from google.appengine.ext import db
from cache_ingredient import getIngredient

CATEGORIES_KEY="INGREDIENTS_CATS"

def getIngredientCategories():
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories == None:
		categories = IngredientCategory.all().order("name")
		categoryList=[]
		for category in categories:
			categoryObject={
				'key':str(category.key()),
				'name':category.name,
			}
			categoryList.append(categoryObject)
		client.set(CATEGORIES_KEY, categoryList)
		return categoryList
	return categories

def addIngredientCategory(category):
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories != None:
		categoryObject={
			'key':str(category.key()),
			'name':category.name,
		}
		categories.append(categoryObject)
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
				ingredientKeys = []
				for ingredient in categoryObject.ingredients:
					ingredientKeys.append(str(ingredient.key()))
				categoryObject['name'] = category.name
				categoryObject['ingredientsKeys'] = ingredientKeys
			categoryList.append(categoryObject)
		client.set(CATEGORIES_KEY, categoryList)

def getIngredientCategoryWithIngredients(key):
	client = memcache.Client()
	category = client.get(key)
	if category == None:
		categoryDb = IngredientCategory.get(key)
		if categoryDb != None:
			ingredientKeys = []
			for ingredient in categoryDb.ingredients:
				ingredientKeys.append(str(ingredient.key()))
			category={
				'key':key,
				'name':category.name,
				'ingredientsKeys':ingredientKeys
			}
			client.set(key, category)
		else:
			return None
		# Fetch dishes
	ingredients = []
	for dishKey in category['ingredientsKeys']:
		ingredients.append(getIngredient(dishKey))
	category['dishes'] = ingredients

	return category

