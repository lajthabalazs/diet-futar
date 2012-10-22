#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db
from model import Dish, Ingredient, IngredientListItem, DishCategory

from base_handler import BaseHandler
from user_management import isUserCook
from keys import DISH_CATEGORY_KEY
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
from cache_dish import getDish, deleteDish, modifyDish

#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class DeleteDishPage(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		dishKey = self.request.get('dishKey')
		dish = db.get(dishKey)
		dish.delete()
		deleteDish(dishKey)
		self.redirect('/dish')
	
class DishPage(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		else:
			dishKey=self.request.get('dishKey')
			if ((dishKey != None) and (dishKey != "")):
			#Modification of basic data
				dish = Dish.get(dishKey)
				dish.title = self.request.get('title')
				dish.subTitle = self.request.get('subTitle')
				dish.description = self.request.get('description')
				if self.request.get('price') != None:
					dish.price = int(self.request.get('price'))
				else:
					dish.price=0
				dishCategoryKey=self.request.get(DISH_CATEGORY_KEY)
				if ((dishCategoryKey != None) and (dishCategoryKey != "")):
					dishCategory = db.get(dishCategoryKey)
					dish.category = dishCategory
				else:
					dish.category = None
				dish.put()
				modifyDish(dish)
				self.redirect('/dish?dishKey=%s' % self.request.get('dishKey'))
				return
			else:
				dish = Dish()
				dish.title = self.request.get('title')
				dish.subTitle = self.request.get('subTitle')
				dish.description = self.request.get('description')
				dish.category = DishCategory.get(self.request.get('dishCategoryKey'))
				dish.put()
				self.redirect('/dish?dishKey=%s' % dish.key())
	def get(self):
		if not isUserCook(self):
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
				dish['energy'] = dish['energy'] + ingredient['quantity'] * ingredient['ingredient']['energy'] / 100.0
			availableIngredients = Ingredient.gql(" ORDER BY name")
			availableCategories = DishCategory.gql("WHERE isMenu = False ORDER BY index")
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
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		# Retrieve the dish
		dish = db.get(self.request.get('dishKey'))
		ingredientToDish = db.get(self.request.get('dishIngredientKey'))
		ingredientToDish.delete()
		modifyDish(dish)
		self.redirect('/dish?dishKey=%s' % dish.key())

class DishIngredientAddPage(BaseHandler):
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
		else:
			# Retrieve the ingredient
			ingredientKey = self.request.get('ingredientKey')
			print "Hello"
			print ingredientKey
			return
			ingredient = db.get()
			quantity = float(self.request.get('quantity'))
			ingredientListItem = IngredientListItem()
			ingredientListItem.quantity = quantity
			ingredientListItem.dish = dish
			ingredientListItem.ingredient = ingredient
			ingredientListItem.put()
			modifyDish(dish)
		self.redirect('/dish?dishKey=%s' % dish.key())
























