from google.appengine.ext import db
from model import Ingredient, IngredientCategory
import jinja2
import os
from base_handler import BaseHandler
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
from user_management import isUserCook
from cache_ingredient import getIngredient, modifyIngredient, addIngredient,\
	getIngredients, deleteIngredient
from cache_ingredient_category import getIngredientCategories,\
	getIngredientCategoryWithIngredients

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class IngredientPage(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return	
		#Check if ingredient exists
		ingredientKey=self.request.get('ingredientKey')
		if ((ingredientKey != None) and (ingredientKey != "")):
			#Ingredient must exist
			ingredient = Ingredient.get(ingredientKey)
			ingredientCategoryKey=self.request.get('ingredientCategoryKey')
			if ((ingredientCategoryKey != None) and (ingredientCategoryKey != "")):
				ingredient.category = IngredientCategory.get(ingredientCategoryKey)
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
			modifyIngredient(ingredient)
			sourceKey=self.request.get('source')
			if ((sourceKey == ingredientCategoryKey) and (sourceKey!=None) and (sourceKey != "")):
				if ingredient.category != None:
					self.redirect('/ingredientCategory?ingredientCategoryKey=%s' % ingredient.category.key())
					return
				else:
					self.redirect('/ingredient')
					return
			else:
				self.redirect('/ingredient')
				return
		else:
			ingredient = Ingredient()
			ingredient.name = self.request.get('ingredient_name')
			ingredient.put()
			addIngredient(ingredient)
			self.redirect('/ingredient?ingredientKey=%s' % ingredient.key())
	def get(self):
		if not isUserCook(self):
			self.redirect("/")
			return	
		ingredientKey=self.request.get('ingredientKey')
		sourceKey=self.request.get('source')
		if ((ingredientKey != None) and (ingredientKey != "")):
			ingredient = getIngredient(ingredientKey)
			availableCategories = getIngredientCategories()
			template_values = {
				'ingredient': ingredient,
				'availableCategories':availableCategories,
				'source':sourceKey
			}
			template = jinja_environment.get_template('templates/ingredient.html')
			self.printPage(ingredient['name'], template.render(template_values), False, False)
		else:
			template_values = {
				'ingredients': getIngredients(),
				'delete_url':"/deleteIngredient"
			}
			template = jinja_environment.get_template('templates/ingredient_list.html')
			self.printPage("Alapanyagok", template.render(template_values), False, False)

class IngredientDeletePage(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return	
		ingredient = db.get(self.request.get('ingredientKey'))
		#Delete all instances of the ingredient association
		if ingredient!= None:
			if ingredient.dishes != None:
				for dishIngredient in ingredient.dishes:
					dishIngredient.delete()
			ingredient.delete()
		# Remove from cache
		deleteIngredient(self.request.get('ingredientKey'))
		self.redirect('/ingredient')

class IngredientAddPage(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		category = db.get(self.request.get('ingredientCategoryKey'))
		ingredient = Ingredient()
		ingredient.name = self.request.get('ingredient_name')
		ingredient.category = category
		ingredient.put()
		addIngredient(ingredient)
		self.redirect('/ingredient?ingredientKey=%s&source=%s' % (ingredient.key(), category.key()))


















