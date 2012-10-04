#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db
from model import Dish, Ingredient, IngredientListItem, DishCategory

from base_handler import BaseHandler
from user_management import isUserAdmin
from keys import DISH_CATEGORY_KEY
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class DeleteDishPage(BaseHandler):
	def post(self):
		if(not isUserAdmin(self)):
			self.redirect("/")
		dish = db.get(self.request.get('dishKey'))
		dish.delete()
		self.redirect('/dish')
	
class DishPage(BaseHandler):
	def post(self):
		print isUserAdmin(self)
		if(not isUserAdmin(self)):
			self.redirect("/")
		else:
			if ((self.request.get('dishKey') != None) and (self.request.get('dishKey') != "")):
			#Modification of basic data
				dish = db.get(self.request.get('dishKey'))
				dish.title = self.request.get('title')
				dish.subTitle = self.request.get('subTitle')
				dish.description = self.request.get('description')
				if self.request.get('price') != None:
					dish.price = int(self.request.get('price'))
				dishCategoryKey=self.request.get(DISH_CATEGORY_KEY)
				if ((dishCategoryKey != None) and (dishCategoryKey != "")):
					dishCategory = db.get(dishCategoryKey)
					dish.category = dishCategory
				else:
					dish.category = None
				dish.put()
				self.redirect('/dish?dishKey=%s' % self.request.get('dishKey'))

			else:
				dish = Dish()
				dish.title = self.request.get('title')
				dish.subTitle = self.request.get('subTitle')
				dish.description = self.request.get('description')
				dish.category = DishCategory.get(self.request.get('dishCategoryKey'))
				dish.put()
				self.redirect('/dish?dishKey=%s' % dish.key())
	def get(self):
		if(not isUserAdmin):
			self.redirect("/")	
		dishKey=self.request.get('dishKey')
		if ((dishKey != None) and (dishKey != "")):
		# A single dish with editable ingredient list
			dish=db.get(dishKey)
			#Check if category exists
			try:
				dish.category
			except ReferencePropertyResolveError:
				dish.category = None
			ingredients = dish.ingredients
			dish.energy = 0
			for ingredient in ingredients:
				dish.energy = dish.energy + ingredient.quantity * ingredient.ingredient.energy / 100.0
			availableIngredients = Ingredient.gql("ORDER BY name")
			availableCategories = DishCategory.gql("ORDER BY index")
			template_values = {
				'dish': dish,
				'availableCategories':availableCategories,
				'availableIngredients':availableIngredients,
				'add_url':"/addIngredientToDish",
				'delete_url':"/deleteIngredientFromDish"
			}
			template = jinja_environment.get_template('templates/dish.html')
			self.printPage(dish.title, template.render(template_values), False, False)
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
			ingredientCategories =DishCategory.gql("ORDER BY index")
			template_values = {
			  'dishes': dishes,
			  'availableCategories': ingredientCategories
			}
			template = jinja_environment.get_template('templates/dish_list.html')
			self.printPage("Receptek", template.render(template_values), False, False)

class DishIngredientDeletePage(BaseHandler):
	def post(self):
		if(not isUserAdmin):
			self.redirect("/")	
		# Retrieve the dish
		dish = db.get(self.request.get('dishKey'))
		ingredientToDish = db.get(self.request.get('dishIngredientKey'))
		ingredientToDish.delete()
		self.redirect('/dish?dishKey=%s' % dish.key())

class DishIngredientAddPage(BaseHandler):
	def post(self):
		if(not isUserAdmin):
			self.redirect("/")	
		# Retrieve the dish
		dish = db.get(self.request.get('dishKey'))
		if ((self.request.get('dishIngredientKey') != None) and (self.request.get('dishIngredientKey') != "")):
		# If its a modification
			ingredientToDish = db.get(self.request.get('dishIngredientKey'))
			ingredientToDish.quantity = float(self.request.get('quantity'))
			ingredientToDish.put()
		else:
			# Retrieve the ingredient
			ingredient = db.get(self.request.get('ingredientKey'))
			quantity = float(self.request.get('quantity'))
			ingredientListItem = IngredientListItem()
			ingredientListItem.quantity = quantity
			ingredientListItem.dish = dish
			ingredientListItem.ingredient = ingredient
			ingredientListItem.put()
		self.redirect('/dish?dishKey=%s' % dish.key())
























