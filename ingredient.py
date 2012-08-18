from google.appengine.ext import db
from model import Ingredient, IngredientCategory
import jinja2
import os
from base_handler import BaseHandler, PAGE_TITLE

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class IngredientPage(BaseHandler):
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
			self.printPage(PAGE_TITLE + " - " + ingredient.name, template.render(template_values), False, False)
		else:
			ingredients = Ingredient.gql("ORDER BY name")
			template_values = {
				'ingredients': ingredients,
				'delete_url':"/deleteIngredient"
			}
			template = jinja_environment.get_template('templates/ingredient_list.html')
			self.printPage(PAGE_TITLE + " - Alapanyagok", template.render(template_values), False, False)

class CategoryIngredientDeletePage(BaseHandler):
	def post(self):
		category = db.get(self.request.get('ingredientCategoryKey'))
		ingredient = db.get(self.request.get('ingredientKey'))
		ingredient.category=None
		ingredient.put()
		self.redirect('/ingredientCategory?ingredientCategoryKey=%s' % category.key())

class IngredientDeletePage(BaseHandler):
	def post(self):
		ingredient = db.get(self.request.get('ingredientKey'))
		#Delete all instances of the ingredient association
		for dishIngredient in ingredient.dishes:
			dishIngredient.delete()
		ingredient.delete()
		self.redirect('/ingredient')

class IngredientAddPage(BaseHandler):
	def post(self):
		category = db.get(self.request.get('ingredientCategoryKey'))
		ingredient = Ingredient()
		ingredient.name = self.request.get('ingredient_name')
		ingredient.category = category
		ingredient.put()
		self.redirect('/ingredientCategory?ingredientCategoryKey=%s' % category.key())

class IngredientCategoryPage(BaseHandler):
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
			self.printPage(PAGE_TITLE + " - " + ingredientCategory.name, template.render(template_values), False, False)
		else:
		# All categories
			ingredientCategories = IngredientCategory.gql("ORDER BY name")
			template_values = {
				'ingredientCategories': ingredientCategories,
				'delete_url':"/deleteIngredientCategory"
			}
			template = jinja_environment.get_template('templates/ingredient_category_list.html')
			self.printPage(PAGE_TITLE + " - Alapanyag kategoriak", template.render(template_values), False, False)

class IngredientCategoryDeletePage(BaseHandler):
	def post(self):
		ingredientCategory = db.get(self.request.get('ingredientCategoryKey'))	  
		ingredientCategory.delete()
		self.redirect('/ingredientCategory?ingredientCategoryKey=%s' % self.request.get('ingredientCategoryKey'))
