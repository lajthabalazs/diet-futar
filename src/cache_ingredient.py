'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import Ingredient
from cache_helper import createIngredientDb
from cache_dish import modifyDish

INGREDIENTS_KEY = "Ingredients"

def differenceToPropagate(o, n):
	if (o['name'] != n['name']):
		return True
	if (o['price'] != n['price']):
		return True
	if (o['energy'] != n['energy']):
		return True
	if (o['carbs'] != n['carbs']):
		return True
	if (o['protein'] != n['protein']):
		return True
	if (o['fat'] != n['fat']):
		return True
	if (o['fiber'] != n['fiber']):
		return True
	if (o['glucozeFree'] != n['glucozeFree']):
		return True
	return False

def removeIngredientFromCategory(categoryKey, ingredientKey):
	client = memcache.Client()
	category = client.get(categoryKey)
	ingredient = client.get(ingredientKey)
	# If not in memcache, does nothing
	if ingredient != None:
		ret = "Must remove from category"
		ret = ret + "<br/>"
		ingredient['category'] = None
		if category != None:
			ret = ret + "Category found"
			ret = ret + "<br/>"
			ingredients=[]
			for actualIngredient in category['ingredients']:
				if actualIngredient['key'] != ingredientKey:
					ingredients.append(actualIngredient)
				else:
					ret = ret + "Skipped"
			categoryObject={
				'key':category['key'],
				'name':category['name'],
				'ingredients':ingredients
			}		
			client.set(categoryKey, categoryObject)
		client.set(ingredientKey, ingredient)
	return ret

def addIngredientToCategory(categoryKey, ingredientObject):
	client = memcache.Client()
	category = client.get(categoryKey)
	found = False
	if category != None:
		ingredients=[]
		for ingredient in category['ingredients']:
			if ingredient['key'] == ingredientObject['key']:
				found = True
			ingredients.append(ingredient)
		# Save modified value
		if not found:
			ingredients.append(ingredientObject)
			categoryObject={
				'key':category['key'],
				'name':category['name'],
				'ingredients':ingredients
			}
			if ingredientObject != None:
				ingredientObject['category'] = {
					'key':category['key'],
					'name':category['name']
				}
				client.set(ingredientObject['key'], ingredientObject)
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
	return ingredients

# Modify dish
def modifyIngredient(ingredientDb):
	client = memcache.Client()
	key = str(ingredientDb.key())
	# Update dishes old category
	ingredientObject = getIngredient(key)
	categoryKey = None
	ret = "Modify "
	ret += str(ingredientObject['category'])
	if ingredientDb.category != None:
		ret += "Had category"
		ret = ret + "<br/>"
		categoryKey = str(ingredientDb.category.key())
	if ingredientObject != None and ingredientObject['category']!=None and ingredientObject['category']['key'] != categoryKey:
		# Update category objects in cacge
		ret = ret + "Must remove"
		ret = ret + "<br/>"
		ret = ret + removeIngredientFromCategory(ingredientObject['category']['key'], key)
	# Create object
	newIngredientObject=createIngredientDb(ingredientDb)
	if ingredientObject == None or (categoryKey != None and (ingredientObject["category"] == None or ingredientObject["category"]['key'] != categoryKey)):
		addIngredientToCategory(categoryKey, newIngredientObject)
	else:
		if categoryKey!= None:
			# Modify ingredientDb in category
			category = client.get(categoryKey)
			if category != None:
				newIngredients = []
				for ingredient in category['ingredients']:
					if ingredient['key'] == key:
						ingredient = newIngredientObject
					newIngredients.append(ingredient)
				category['ingredients'] = newIngredients
				client.set(categoryKey, category)
	# Adds ingredient
	# TODO modify dishes containing this ingredient
	if (differenceToPropagate(ingredientObject, newIngredientObject)):
		for dishIngredient in ingredientDb.dishes:
			dishKey = str(dishIngredient.dish.key())
			title = dishIngredient.dish.title
			subtitle = dishIngredient.dish.subtitle
			description = dishIngredient.dish.description
			dishCategory = dishIngredient.dish.category
			modifyDish(dishKey, title, subtitle, description, dishCategory, dishIngredient.dish.eggFree, dishIngredient.dish.milkFree)
	client.set(key, newIngredientObject)
	# Adds ingredient to ingredient list
	ingredients = client.get(INGREDIENTS_KEY)
	if ingredients != None:
		newIngredients = []
		for ingredient in ingredients:
			if ingredient['key'] == key:
				ingredient = newIngredientObject
			newIngredients.append(ingredient)
		client.set(INGREDIENTS_KEY, newIngredients)
	return ret

# Adds a dish to the cache
def addIngredient(ingredientDb):
	client = memcache.Client()
	key = str(ingredientDb.key())
	categoryKey = None
	if ingredientDb.category != None:
		categoryKey = str(ingredientDb.category.key())
	ingredient=createIngredientDb(ingredientDb)
	if categoryKey != None:
		addIngredientToCategory(categoryKey, ingredient)
	client.set(key, ingredient)
	ingredients = client.get(INGREDIENTS_KEY)
	if ingredients != None:
		newIngredients = []
		found = False
		for actualIngredient in ingredients:
			if actualIngredient['key'] == key:
				found = True
			newIngredients.append(actualIngredient)
		if not found:
			newIngredients.append(ingredient)
		client.set(INGREDIENTS_KEY, newIngredients)

# Delete dish from cache
def deleteIngredient(key):
	client = memcache.Client()
	ingredientObject = client.get(key)
	if ingredientObject != None:
		try:
			removeIngredientFromCategory(ingredientObject['categoryKey'], key)
		except KeyError:
			pass
		client.delete(key)
	ingredients = client.get(INGREDIENTS_KEY)
	if ingredients != None:
		newIngredients = []
		for ingredient in ingredients:
			if ingredient['key'] != key:
				newIngredients.append(ingredient)
		client.set(INGREDIENTS_KEY, newIngredients)
