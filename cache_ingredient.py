'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import Dish, Ingredient
from google.appengine.ext import db

INGREDIENTS_KEY = "Ingredients"

class MyClass:
	"""A simple example class"""

def createIngredientFromDic (ingredientDict):
	ingredient= MyClass()
	ingredient.key = ingredientDict['key'],
	ingredient.name = ingredientDict['name'],
	ingredient.category = ingredientDict['category'],
	ingredient.price = ingredientDict['price'],
	ingredient.energy = ingredientDict['energy'],
	ingredient.carbs = ingredientDict['carbs'],
	ingredient.protein = ingredientDict['protein'],
	ingredient.fat = ingredientDict['fat'],
	ingredient.fiber = ingredientDict['fiber'],
	ingredient.glucozeFree = ingredientDict['glucozeFree']
	return ingredient

def createCategoryDb(categoryDb):
	category = MyClass()
	category.key = str(categoryDb.key())
	category.name = categoryDb.name
	return category
	
def createIngredientDb (ingredientDb):
	ingredient={
		'key':str(ingredientDb.key()),
		'name':ingredientDb.name,
		'category':createCategoryDb(ingredientDb.category),
		'price':ingredientDb.price,
		'energy':ingredientDb.energy,
		'carbs':ingredientDb.carbs,
		'protein':ingredientDb.protein,
		'fat':ingredientDb.fat,
		'fiber':ingredientDb.fiber,
		'glucozeFree':ingredientDb.glucozeFree
	}
	return ingredient


def removeIngredientFromCategory(categoryKey, ingredientKey):
	client = memcache.Client()
	category = client.get(categoryKey)
	ingredient = client.get(ingredientKey)
	# If not in memcache, does nothing
	if ingredient != None:
		ingredient.category = None
		client.set(ingredientKey, ingredient)
		if category != None:
			ingredients=[]
			for ingredient in category.ingredients:
				if ingredient.key != ingredientKey:
					ingredients.append(ingredient)
			categoryObject={
				'key':category.key,
				'name':category.name,
				'ingredients':ingredients
			}		
			client.set(categoryKey, categoryObject)


def addIngredientToCategory(categoryKey, ingredientObject):
	client = memcache.Client()
	category = client.get(categoryKey)
	found = False
	if category != None:
		ingredients=[]
		for ingredient in category.ingredients:
			if ingredient.key == ingredientObject.key:
				found = True
			ingredients.append(ingredient)
		# Save modified value
		if not found:
			ingredients.append(ingredientObject)
			categoryObject={
				'key':category.key,
				'name':category.name,
				'ingredients':ingredients
			}
			ingredient = client.get(ingredientObject.key)
			if ingredient != None:
				ingredient.categoryKey = categoryKey
				client.set(ingredientObject.key, ingredient)
			client.set(categoryKey, categoryObject)


def getIngredient(key):
	client = memcache.Client()
	ingredient = client.get(key)
	if ingredient == None:
		ingredientDb = Ingredient.get(key)
		if ingredientDb != None:
			ingredient = createIngredientDb(ingredientDb)
			client.set(key, ingredient)
	return client.get(key)


def getIngredients():
	client = memcache.Client()
	ingredients = client.get(INGREDIENTS_KEY)
	if ingredients == None:
		ingredients = []
		ingredientsDb = Ingredient.gql("ORDER BY name")
		if ingredientsDb != None:
			for ingredientDb in ingredientsDb:
				ingredient = createIngredientDb(ingredientDb)
				ingredients.append(ingredient)
			client.set(INGREDIENTS_KEY, ingredients)
	return ingredient


# Modify dish
def modifyIngredient(ingredientDb):
	client = memcache.Client()
	key = str(ingredientDb.key())
	# Update dishes old category
	ingredientObject = getIngredient(key)
	categoryKey = str(ingredientDb.category.key())
	if ingredientObject != None and ingredientObject.category.key != categoryKey:
		# Update category objects in cacge
		removeIngredientFromCategory(ingredientObject.category.key, key)
	# Create object
	newIngredientObject=createIngredientDb(ingredientDb)
	if ingredientObject == None or ingredientObject["categoryKey"] != categoryKey:
		addIngredientToCategory(categoryKey, newIngredientObject)
	else:
		# Modify ingredientDb in category
		category = client.get(categoryKey)
		if category != None:
			newIngredients = []
			for ingredient in category.ingredients:
				if ingredient.key == key:
					ingredient = newIngredientObject
				newIngredients.append(ingredient)
			category.ingredients = newIngredients
			client.set(categoryKey, category)
	# Adds ingredient
	client.set(key, newIngredientObject)
	# Adds ingredient to ingredient list
	ingredients = client.get(INGREDIENTS_KEY)
	if ingredients != None:
		newIngredients = []
		for ingredientDb in ingredients:
			if ingredientDb.key == key:
				ingredientDb = newIngredientObject
			newIngredients.append(ingredientDb)
		client.set(INGREDIENTS_KEY, newIngredients)


# Adds a dish to the cache
def addIngredient(ingredient):
	client = memcache.Client()
	key = str(ingredient.key())
	categoryKey = str(ingredient.category.key())
	newIngredientObject={
		'key':key,
		'name':ingredient.name,
		'categoryKey':categoryKey,
		'price':ingredient.price,
		'energy':ingredient.energy,
		'carbs':ingredient.carbs,
		'protein':ingredient.protein,
		'fat':ingredient.fat,
		'fiber':ingredient.fiber,
		'glucozeFree':ingredient.glucozeFree
	}
	addIngredientToCategory(categoryKey, key)
	client.set(key, newIngredientObject)
	ingredients = client.get(INGREDIENTS_KEY)
	if ingredients != None:
		newIngredients = []
		found = False
		for ingredient in ingredients:
			if ingredient.key == key:
				found = True
			newIngredients.append(ingredient)
		if not found:
			newIngredients.append(newIngredientObject)
		client.set(INGREDIENTS_KEY, newIngredients)

# Delete dish from cache
def deleteIngredient(key):
	client = memcache.Client()
	ingredientObject = client.get(key)
	if ingredientObject != None:
		removeIngredientFromCategory(ingredientObject.categoryKey, key)
		client.delete(key)
		ingredients = client.get(INGREDIENTS_KEY)
	if ingredients != None:
		newIngredients = []
		for ingredient in ingredients:
			if ingredient.key != key:
				newIngredients.append(ingredient)
		client.set(INGREDIENTS_KEY, newIngredients)
