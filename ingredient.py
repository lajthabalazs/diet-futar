from google.appengine.ext import db
from model import Ingredient, IngredientCategory
import jinja2
import os
from base_handler import BaseHandler, PAGE_TITLE

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class IngredientPage(BaseHandler):
	def post(self):
		#Check if ingredient exists
		ingredientKey=self.request.get('ingredientKey')
		if ((ingredientKey != None) and (ingredientKey != "")):
			#Ingredient must exist
			ingredient = db.get(ingredientKey)
			ingredientCategoryKey=self.request.get('ingredientCategoryKey')
			if ((ingredientCategoryKey != None) and (ingredientCategoryKey != "")):
				category = db.get(ingredientCategoryKey)
				ingredient.category = category
			else:
				ingredient.category = None
			energy=self.request.get('energy')
			protein=self.request.get('protein')
			carbs=self.request.get('carbs')
			fat=self.request.get('fat')
			fiber=self.request.get('fiber')
			if ((energy != None) and (energy != "")):
				ingredient.energy = float(energy)
			if ((protein != None) and (protein != "")):
				ingredient.protein = float(protein)
			if ((carbs != None) and (carbs != "")):
				ingredient.carbs = float(carbs)
			if ((fat != None) and (fat != "")):
				ingredient.fat = float(fat)
			if ((fiber != None) and (fiber != "")):
				ingredient.fiber = float(self.request.get('fiber'))
			ingredient.put()
			sourceKey=self.request.get('source')
			if ((sourceKey == ingredientCategoryKey) and (sourceKey!=None) and (sourceKey != "")):
				self.redirect('/ingredientCategory?ingredientCategoryKey=%s' % category.key())
			else:
				self.redirect('/ingredient')
		else:
			ingredient = Ingredient()
			ingredient.name = self.request.get('ingredient_name')
			ingredient.put()
			self.redirect('/ingredient?ingredientKey=%s' % ingredient.key())
	def get(self):
		ingredientKey=self.request.get('ingredientKey')
		sourceKey=self.request.get('source')
		if ((ingredientKey != None) and (ingredientKey != "")):
			ingredient = db.get(ingredientKey)
			availableCategories = IngredientCategory.gql("ORDER BY name")
			template_values = {
				'ingredient': ingredient,
				'availableCategories':availableCategories,
				'source':sourceKey
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
		#self.redirect('/ingredientCategory?ingredientCategoryKey=%s' % category.key())
		self.redirect('/ingredient?ingredientKey=%s&source=%s' % (ingredient.key(), category.key()))

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
