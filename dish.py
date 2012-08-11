#!/usr/bin/env python

import webapp2
import jinja2
import os

from google.appengine.ext import db
from model import Dish, Ingredient, IngredientListItem
from ingredient import CategoryIngredientDeletePage, IngredientDeletePage,IngredientAddPage, IngredientPage, IngredientCategoryPage,\
	IngredientCategoryDeletePage
from base_handler import BaseHandler

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(BaseHandler):
	def get(self):
		self.response.out.write('<html><body>' + jinja_environment.get_template('templates/header.html').render() + '</body></html>');
		
class DeleteDishPage(BaseHandler):
	def post(self):
		dish = db.get(self.request.get('dishKey'))
		dish.delete()
		self.redirect('/dish')
	
class DishPage(BaseHandler):
	def post(self):
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
		if ((self.request.get('dishKey') != None) and (self.request.get('dishKey') != "")):
		# A single dish with editable ingredient list
			dish = db.get(self.request.get('dishKey'))
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
			self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render(template_values))
		else:
		# All the dishes
			dishes = Dish.gql("ORDER BY title")
			template_values = {
			  'dishes': dishes,
			}
			template = jinja_environment.get_template('templates/dish_list.html')
			self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render(template_values))

class DishIngredientDeletePage(BaseHandler):
	def post(self):
		# Retrieve the dish
		dish = db.get(self.request.get('dishKey'))
		ingredientToDish = db.get(self.request.get('dishIngredientKey'))
		ingredientToDish.delete()
		self.redirect('/dish?dishKey=%s' % dish.key())

class DishIngredientAddPage(BaseHandler):
	def post(self):
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
























