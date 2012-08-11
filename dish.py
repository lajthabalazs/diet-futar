#!/usr/bin/env python

import cgi
import datetime
import urllib
import webapp2
import jinja2
import os

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Dish(db.Model):
	title = db.StringProperty()
	subTitle = db.StringProperty()
	description = db.StringProperty(multiline=True)

class IngredientCategory(db.Model):
	name = db.StringProperty()

class Ingredient(db.Model):
	name = db.StringProperty()
	category = db.ReferenceProperty(IngredientCategory, collection_name='ingredients')
	energy = db.FloatProperty(default=0.0)
	carbs = db.FloatProperty(default=0.0)
	protein = db.FloatProperty(default=0.0)
	fat = db.FloatProperty(default=0.0)
	fiber = db.FloatProperty(default=0.0)

class IngredientListItem(db.Model):
    dish = db.ReferenceProperty(Dish, collection_name='ingredients')
    ingredient = db.ReferenceProperty(Ingredient, collection_name='dishes')
    #ingredient type
    quantity = db.FloatProperty()

class MainPage(webapp2.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>' + jinja_environment.get_template('templates/header.html').render() + '</body></html>');

class DeleteDishPage(webapp2.RequestHandler):
	def post(self):
		dish = db.get(self.request.get('dishKey'))
		dish.delete()
		self.redirect('/dish')
	
class DishPage(webapp2.RequestHandler):
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

class DishIngredientDeletePage(webapp2.RequestHandler):
	def post(self):
		# Retrieve the dish
		dish = db.get(self.request.get('dishKey'))
		ingredientToDish = db.get(self.request.get('dishIngredientKey'))
		ingredientToDish.delete()
		self.redirect('/dish?dishKey=%s' % dish.key())

class DishIngredientAddPage(webapp2.RequestHandler):
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

class IngredientPage(webapp2.RequestHandler):
	def post(self):
	#Check if ingredient exists
		if ((self.request.get('ingredientKey') != None) and (self.request.get('ingredientKey') != "")):
			#Ingredient must exist
			ingredient = db.get(self.request.get('ingredientKey'))
			if ((self.request.get('ingredientCategoryKey') != None) and (self.request.get('ingredientCategoryKey') != "")):
				category = db.get(self.request.get('ingredientCategoryKey'))
				ingredient.category = category
			else:
				ingredient.category = None
			if ((self.request.get('energy') != None) and (self.request.get('energy') != "")):
				ingredient.energy = float(self.request.get('energy'))
			if ((self.request.get('protein') != None) and (self.request.get('protein') != "")):
				ingredient.protein = float(self.request.get('protein'))
			if ((self.request.get('carbs') != None) and (self.request.get('carbs') != "")):
				ingredient.carbs = float(self.request.get('carbs'))
			if ((self.request.get('fat') != None) and (self.request.get('fat') != "")):
				ingredient.fat = float(self.request.get('fat'))
			if ((self.request.get('fiber') != None) and (self.request.get('fiber') != "")):
				ingredient.fiber = float(self.request.get('fiber'))
			ingredient.put()
			self.redirect('/ingredient?ingredientKey=%s' % ingredient.key())
		else:
			ingredient = Ingredient()
			ingredient.name = self.request.get('ingredient_name')
			ingredient.put()
			self.redirect('/ingredient')
	def get(self):
		if ((self.request.get('ingredientKey') != None) and (self.request.get('ingredientKey') != "")):
			ingredient = db.get(self.request.get('ingredientKey'))
			availableCategories = IngredientCategory.gql("ORDER BY name")
			template_values = {
				'ingredient': ingredient,
				'availableCategories':availableCategories
			}
			template = jinja_environment.get_template('templates/ingredient.html')
			self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render(template_values))
		else:
			ingredients = Ingredient.gql("ORDER BY name")
			template_values = {
				'ingredients': ingredients,
				'delete_url':"/deleteIngredient"
			}
			template = jinja_environment.get_template('templates/ingredient_list.html')
			self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render(template_values))

class CategoryIngredientDeletePage(webapp2.RequestHandler):
	def post(self):
		category = db.get(self.request.get('ingredientCategoryKey'))
		ingredient = db.get(self.request.get('ingredientKey'))
		ingredient.category=None
		ingredient.put()
		self.redirect('/ingredientCategory?ingredientCategoryKey=%s' % category.key())

class IngredientDeletePage(webapp2.RequestHandler):
	def post(self):
		ingredient = db.get(self.request.get('ingredientKey'))
		ingredient.delete()
		self.redirect('/ingredient')

class IngredientAddPage(webapp2.RequestHandler):
	def post(self):
		category = db.get(self.request.get('ingredientCategoryKey'))
		ingredient = Ingredient()
		ingredient.name = self.request.get('ingredient_name')
		ingredient.category = category
		ingredient.put()
		self.redirect('/ingredientCategory?ingredientCategoryKey=%s' % category.key())
	  
class IngredientCategoryPage(webapp2.RequestHandler):
	def post(self):
		ingredientCategory = IngredientCategory()
		ingredientCategory.name = self.request.get('ingredient_category_name')
		ingredientCategory.put()
		self.redirect('/ingredientCategory')
	def get(self):
		if ((self.request.get('ingredientCategoryKey') != None) and (self.request.get('ingredientCategoryKey') != "")):
		# List every ingredient in the category
			ingredientCategory = db.get(self.request.get('ingredientCategoryKey'))
			template_values = {
				'ingredientCategory': ingredientCategory,
				'add_url':"/addIngredientToCategory",
				'delete_url':"/deleteIngredientFromCategory"
			}
			template = jinja_environment.get_template('templates/ingredient_category.html')
			self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render(template_values))
		else:
		# All categories
			ingredientCategories = IngredientCategory.gql("ORDER BY name")
			template_values = {
				'ingredientCategories': ingredientCategories,
				'delete_url':"/deleteIngredientCategory"
			}
			template = jinja_environment.get_template('templates/ingredient_category_list.html')
			self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render(template_values))

class IngredientCategoryDeletePage(webapp2.RequestHandler):
  def post(self):
      ingredientCategory = db.get(self.request.get('ingredientCategoryKey'))	  
      ingredientCategory.delete()
      self.redirect('/ingredientCategory?ingredientCategoryKey=%s' % self.request.get('ingredientCategoryKey'))
			
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/dish', DishPage),
                               ('/deleteDish', DeleteDishPage),
                               ('/addIngredientToDish', DishIngredientAddPage),
                               ('/deleteIngredientFromDish', DishIngredientDeletePage),
                               ('/deleteIngredientFromCategory', CategoryIngredientDeletePage),
                               ('/deleteIngredient', IngredientDeletePage),
                               ('/addIngredientToCategory', IngredientAddPage),
                               ('/ingredient', IngredientPage),
                               ('/deleteIngredientCategory', IngredientCategoryDeletePage),
                               ('/ingredientCategory', IngredientCategoryPage)],
                              debug=True)
























