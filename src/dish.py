#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db
from model import Dish, IngredientListItem, DishCategory

from base_handler import BaseHandler, logInfo
from user_management import isUserCook, LOGIN_NEXT_PAGE_KEY
from keys import DISH_CATEGORY_KEY
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
from cache_dish import getDish, deleteDish, modifyDish, addDish
from cache_dish_category import getDishCategories
from cache_ingredient import getIngredients
import datetime

#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class DeleteDishPage(BaseHandler):
	URL = '/deleteDish'
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		dishKey = self.request.get('dishKey')
		dish = db.get(dishKey)
		if dish != None:
			dish.delete()
			deleteDish(dishKey)
		self.redirect('/dish')
	
class DishPage(BaseHandler):
	URL = '/dish'
	def post(self):
		if not isUserCook(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		dishKey=self.request.get('dishKey')
		if ((dishKey != None) and (dishKey != "")):
		#Modification of basic data
			title = self.request.get('title')
			subtitle = self.request.get('subtitle')
			description = self.request.get('description')
			eggFree = (self.request.get('eggFree') == "yes")
			milkFree = (self.request.get('milkFree') == "yes")
			dishCategoryKey=self.request.get(DISH_CATEGORY_KEY)
			dishCategory=None
			if ((dishCategoryKey != None) and (dishCategoryKey != "")):
				dishCategory = db.get(dishCategoryKey)
			modifyDish(dishKey, title, subtitle, description, dishCategory, eggFree, milkFree)
			self.redirect('/dish?dishKey=%s' % self.request.get('dishKey'))
			return
		else:
			dish = Dish()
			dish.creationDate = datetime.datetime.today()
			dish.title = self.request.get('title')
			dish.subtitle = self.request.get('subtitle')
			dish.description = self.request.get('description')
			dish.category = DishCategory.get(self.request.get('dishCategoryKey'))
			eggFree = (self.request.get('eggFree') == "yes")
			milkFree = (self.request.get('milkFree') == "yes")
			dish.milkFree = milkFree
			dish.eggFree = eggFree
			dish.put()
			addDish(dish)
			self.redirect('/dish?dishKey=%s' % str(dish.key()))
	def get(self):
		if not isUserCook(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		dishKey=self.request.get('dishKey')
		if ((dishKey != None) and (dishKey != "")):
		# A single dish with editable ingredient list
			dish=getDish(dishKey)
			#Check if category exists
			ingredients = dish['ingredients']
			dish['energy'] = 0
			for ingredient in ingredients:
				dish['energy'] = dish['energy'] + ingredient['quantity'] * ingredient['energy'] / 100.0
			gotIngredients = getIngredients()
			availableIngredients = sorted(gotIngredients, key=lambda ingredient:ingredient['name'])
			gotCategories = getDishCategories()
			availableCategories = sorted(gotCategories, key=lambda category:category['name'])
			template_values = {
				'dish': dish,
				'availableCategories':availableCategories,
				'availableIngredients':availableIngredients,
				'add_url':"/addIngredientToDish",
				'delete_url':"/deleteIngredientFromDish"
			}
			template = jinja_environment.get_template('templates/dish.html')
			self.printPage(dish['title'], template.render(template_values), False, False)
		else:
		# All the dishes
			unprocessedDishes = Dish.gql("ORDER BY title")
			dishes = []
			for dish in unprocessedDishes:
				try:
					dish.category
				except ReferencePropertyResolveError:
					dish.category = None
				dishes.append(dish)
			availableCategories = DishCategory.gql("WHERE isMenu = False ORDER BY index")
			template_values = {
			  'dishes': dishes,
			  'availableCategories': availableCategories
			}
			template = jinja_environment.get_template('templates/dish_list.html')
			self.printPage("Receptek", template.render(template_values), False, False)

class DishIngredientDeletePage(BaseHandler):
	URL = '/deleteIngredientFromDish'
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		# Retrieve the dish
		dish = db.get(self.request.get('dishKey'))
		ingredientToDish = db.get(self.request.get('dishIngredientKey'))
		ingredientToDish.delete()
		modifyDish(str(dish.key()), dish.title, dish.subtitle, dish.description, dish.category, dish.eggFree, dish.milkFree)
		self.redirect('/dish?dishKey=%s' % str(dish.key()))

class DishIngredientAddPage(BaseHandler):
	URL = '/addIngredientToDish'
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		# Retrieve the dish
		dish = db.get(self.request.get('dishKey'))
		if ((self.request.get('dishIngredientKey') != None) and (self.request.get('dishIngredientKey') != "")):
		# If its a modification
			ingredientToDish = db.get(self.request.get('dishIngredientKey'))
			ingredientToDish.quantity = float(self.request.get('quantity'))
			ingredientToDish.put()
			#Modification of basic data
			modifyDish(str(dish.key()), dish.title, dish.subtitle, dish.description, dish.category, dish.eggFree, dish.milkFree)
		else:
			# Retrieve the ingredient
			ingredientKey = self.request.get('ingredientKey')
			ingredient = db.get(ingredientKey)
			quantity = float(self.request.get('quantity'))
			ingredientListItem = IngredientListItem()
			ingredientListItem.quantity = quantity
			ingredientListItem.dish = dish
			ingredientListItem.ingredient = ingredient
			ingredientListItem.put()
			modifyDish(str(dish.key()), dish.title, dish.subtitle, dish.description, dish.category, dish.eggFree, dish.milkFree)
		self.redirect('/dish?dishKey=%s' % str(dish.key()))
























