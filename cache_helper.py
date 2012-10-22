'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import Ingredient

INGREDIENTS_KEY = "Ingredients"

def createDishCategoryObjectDb(categoryDb):
	if categoryDb == None:
		return None
	else:
		categoryObject={
			'key':categoryDb.key,
			'name':categoryDb.name,
			'isMenu':categoryDb.isMenu,
			'index':categoryDb.index,
			'disheKeys': []
		}
		return categoryObject


def createDishObjectDb(dishDb):
	if dishDb == None:
		return None
	else:
		dish={
			'key':str(dishDb.key()),
			'title':dishDb.title,
			'categoryKey':str(dishDb.category.key()),
			'price':dishDb.price
		}
		# TDOO ingredients
		return dish

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