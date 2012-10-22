'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import Ingredient

INGREDIENTS_KEY = "Ingredients"

def createCategoryDb(categoryDb):
	if categoryDb == None:
		return None
	else:
		category = {
			'key': str(categoryDb.key()),
			'name': categoryDb.name
		}
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
		ingredient['category'] = None
		client.set(ingredientKey, ingredient)
		if category != None:
			ingredients=[]
			for ingredient in category['ingredients']:
				if ingredient['key'] != ingredientKey:
					ingredients.append(ingredient)
			categoryObject={
				'key':category['key'],
				'name':category['name'],
				'ingredients':ingredients
			}		
			client.set(categoryKey, categoryObject)


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
			print ingredient
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
				print ingredient
				ingredients.append(ingredient)
			client.set(INGREDIENTS_KEY, ingredients)
	return ingredients


# Modify dish
def modifyIngredient(ingredientDb):
	client = memcache.Client()
	key = str(ingredientDb.key())
	# Update dishes old category
	ingredientObject = getIngredient(key)
	#print "Hello"
	#print ingredientObject
	#print "<br/>"
	#print "Bello"
	#print createIngredientDb(ingredientDb)
	#print "<br/>"
	categoryKey = None
	if ingredientDb.category != None:
		categoryKey = str(ingredientDb.category.key())
	if ingredientObject != None and ingredientObject['category']!=None and ingredientObject['category']['key'] != categoryKey:
		# Update category objects in cacge
		removeIngredientFromCategory(ingredientObject['category']['key'], key)
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
		for ingredient in ingredients:
			if ingredient['key'] == key:
				found = True
			newIngredients.append(ingredient)
		if not found:
			newIngredients.append(ingredient)
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
			if ingredient['key'] != key:
				newIngredients.append(ingredient)
		client.set(INGREDIENTS_KEY, newIngredients)
