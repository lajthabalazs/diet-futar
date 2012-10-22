'''
Created on Aug 11, 2012

@author: lajthabalazs
'''

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
		ingredients = []
		for ingredientDb in dishDb.ingredients:
			ingredients.append(createIngredientDb(ingredientDb.ingredient))
		dish={
			'key':str(dishDb.key()),
			'title':dishDb.title,
			'category':createDishCategoryObjectDb(dishDb.category),
			'price':dishDb.price,
			'ingredients':ingredients
		}
		return dish