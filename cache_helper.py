'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api.datastore_errors import ReferencePropertyResolveError

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
		ingredients = []
		for ingredientDb in dishDb.ingredients:
			ingredient = createDishIngredientDb(ingredientDb)
			if ingredientDb.ingredient.price != None and ingredientDb.quantity != None:
				price = price + ingredientDb.quantity * ingredientDb.ingredient.price
			ingredients.append(ingredient)
		dish={
			'key':str(dishDb.key()),
			'title':dishDb.title,
			'category':createDishCategoryObjectDb(dishDb.category),
			'price':int(price / 100),
			'ingredients':ingredients
		}
		return dish