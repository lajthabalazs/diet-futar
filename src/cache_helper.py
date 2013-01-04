'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import ZipCodes

def getZipCodeEntry(code):
	client = memcache.Client()
	costs = client.get("zip_code_cost_" + str(code))
	# If not in memcache, does nothing
	if costs != None:
		return costs
	else:
		rawCodes = ZipCodes.all().get()
		if (rawCodes == None):
			return None
		ret = None
		for code in rawCodes.deliveryCosts:
			parts=code.rsplit(" ")
			key = "zip_code_cost_" + parts[0]
			costs = {
					'cost':int(parts[1]),
					'limit':int(parts[2])
				}
			client.add(key, costs)
			if parts[0] == str(code):
				ret = costs
		return ret

def updateZipCodeEntry(code, cost, limit):
	client = memcache.Client()
	key = "zip_code_cost_" + str(code)
	client.add(key, {
					'cost':cost,
					'limit':limit
				})

def createIngredientCategoryDb(categoryDb):
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
		'category':createIngredientCategoryDb(ingredientDb.category),
		'price':ingredientDb.price,
		'energy':ingredientDb.energy,
		'carbs':ingredientDb.carbs,
		'protein':ingredientDb.protein,
		'fat':ingredientDb.fat,
		'fiber':ingredientDb.fiber,
		'glucozeFree':ingredientDb.glucozeFree
	}
	return ingredient


def createDishIngredientDb (ingredientDb):
	ingredient={
		'key':str(ingredientDb.key()),
		'ingredient_key':str(ingredientDb.ingredient.key()),
		'name':ingredientDb.ingredient.name,
		'category':createIngredientCategoryDb(ingredientDb.ingredient.category),
		'price':ingredientDb.ingredient.price,
		'energy':ingredientDb.ingredient.energy,
		'carbs':ingredientDb.ingredient.carbs,
		'protein':ingredientDb.ingredient.protein,
		'fat':ingredientDb.ingredient.fat,
		'fiber':ingredientDb.ingredient.fiber,
		'glucozeFree':ingredientDb.ingredient.glucozeFree,
		'quantity':ingredientDb.quantity
	}
	return ingredient

def createDishCategoryObjectDb(categoryDb):
	if categoryDb == None:
		return None
	else:
		categoryObject={
			'key':str(categoryDb.key()),
			'name':categoryDb.name,
			'isMenu':categoryDb.isMenu,
			'index':categoryDb.index,
			'dishKeys': []
		}
		return categoryObject


def createDishObjectDb(dishDb):
	if dishDb == None:
		return None
	else:
		price = 0
		energy = 0
		fat = 0
		carbs = 0
		fiber = 0
		protein = 0
		ingredients = []
		for ingredientDb in dishDb.ingredients:
			ingredient = createDishIngredientDb(ingredientDb)
			if ingredientDb.ingredient.price != None and ingredientDb.quantity != None:
				price = price + ingredientDb.quantity * ingredientDb.ingredient.price
				energy = energy + ingredientDb.quantity * ingredientDb.ingredient.energy
				fat = fat + ingredientDb.quantity * ingredientDb.ingredient.fat
				carbs = carbs + ingredientDb.quantity * ingredientDb.ingredient.carbs
				fiber = fiber + ingredientDb.quantity * ingredientDb.ingredient.fiber
				protein = protein + ingredientDb.quantity * ingredientDb.ingredient.protein
			ingredients.append(ingredient)
		dish={
			'key':str(dishDb.key()),
			'title':dishDb.title,
			'subtitle':dishDb.subtitle,
			'description':dishDb.description,
			'category':createDishCategoryObjectDb(dishDb.category),
			'price':int(price / 100),
			'energy':int(energy/100),
			'fat':int(fat/100),
			'carbs':int(carbs/100),
			'fiber':int(fiber/100),
			'protein':int(protein/100),
			'ingredients':ingredients,
			'eggFree':dishDb.eggFree,
			'milkFree':dishDb.milkFree
		}
		return dish