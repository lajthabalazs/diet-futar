#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db
from model import Dish, Ingredient, IngredientListItem

from base_handler import BaseHandler, PAGE_TITLE
from user_management import isUserAdmin
#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class DeleteDishPage(BaseHandler):
	def post(self):
		if(not isUserAdmin):
			self.redirect("/dish")	
		dish = db.get(self.request.get('dishKey'))
		dish.delete()
		self.redirect('/dish')
	
class DishPage(BaseHandler):
	def post(self):
		if(not isUserAdmin):
			self.redirect("/dish")	
		else:
			if ((self.request.get('dishKey') != None) and (self.request.get('dishKey') != "")):
			#Modification of basic data
				dish = db.get(self.request.get('dishKey'))
				dish.title = self.request.get('title')
				dish.subTitle = self.request.get('subTitle')
				dish.description = self.request.get('description')
				dish.put()
				self.redirect('/dish?dishKey=%s' % self.request.get('dishKey'))
			else:
				dish = Dish()
				dish.title = self.request.get('title')
				dish.subTitle = self.request.get('subTitle')
				dish.description = self.request.get('description')
				dish.put()
				self.redirect('/dish?dishKey=%s' % dish.key())
	def get(self):
		dishKey=self.request.get('dishKey')
		if ((dishKey != None) and (dishKey != "")):
		# A single dish with editable ingredient list
			dish=db.get(dishKey)
			ingredients = dish.ingredients
			dish.energy = 0
			for ingredient in ingredients:
				dish.energy = dish.energy + ingredient.quantity * ingredient.ingredient.energy / 100.0
			availableIngredients = Ingredient.gql("ORDER BY name")
			template_values = {
				'dish': dish,
				'availableIngredients':availableIngredients,
				'add_url':"/addIngredientToDish",
				'delete_url':"/deleteIngredientFromDish"
			}
			template = jinja_environment.get_template('templates/dish.html')
			self.printPage(PAGE_TITLE + " - " + dish.title, template.render(template_values), False, False)
		else:
		# All the dishes
			dishes = Dish.gql("ORDER BY title")
			template_values = {
			  'dishes': dishes,
			}
			template = jinja_environment.get_template('templates/dish_list.html')
			self.printPage(PAGE_TITLE + " - Receptek", template.render(template_values), False, False)

class DishIngredientDeletePage(BaseHandler):
	def post(self):
		if(not isUserAdmin):
			self.redirect("/dish")	
		# Retrieve the dish
		dish = db.get(self.request.get('dishKey'))
		ingredientToDish = db.get(self.request.get('dishIngredientKey'))
		ingredientToDish.delete()
		self.redirect('/dish?dishKey=%s' % dish.key())

class DishIngredientAddPage(BaseHandler):
	def post(self):
		if(not isUserAdmin):
			self.redirect("/dish")	
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
























