from google.appengine.ext import db
from model import IngredientCategory
import jinja2
import os
from base_handler import BaseHandler
from user_management import isUserCook
from cache_ingredient import modifyIngredient
from cache_ingredient_category import addIngredientCategory,\
	getIngredientCategoryWithIngredients, getIngredientCategories,\
	deleteIngredientCategory

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class CategoryIngredientDeletePage(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		category = db.get(self.request.get('ingredientCategoryKey'))
		ingredient = db.get(self.request.get('ingredientKey'))
		ingredient.category=None
		ingredient.put()
		modifyIngredient(ingredient)
		self.redirect('/ingredientCategory?ingredientCategoryKey=%s' % category.key())

class IngredientCategoryPage(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		ingredientCategory = IngredientCategory()
		ingredientCategory.name = self.request.get('ingredient_category_name')
		ingredientCategory.put()
		addIngredientCategory(ingredientCategory)
		self.redirect('/ingredientCategory')
	def get(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		ingredientCategoryKey = self.request.get('ingredientCategoryKey') 
		if ingredientCategoryKey!= None and ingredientCategoryKey != "":
		# List every ingredient in the category
			ingredientCategory = getIngredientCategoryWithIngredients(ingredientCategoryKey)
			template_values = {
				'ingredientCategory': ingredientCategory,
				'add_url':"/addIngredientToCategory",
				'delete_url':"/deleteIngredientFromCategory"
			}
			template = jinja_environment.get_template('templates/ingredient_category.html')
			self.printPage(ingredientCategory['name'], template.render(template_values), False, False)
		else:
		# All categories
			ingredientCategories = getIngredientCategories()
			template_values = {
				'ingredientCategories': ingredientCategories,
				'delete_url':"/deleteIngredientCategory"
			}
			template = jinja_environment.get_template('templates/ingredient_category_list.html')
			self.printPage("Alapanyag kategoriak", template.render(template_values), False, False)

class IngredientCategoryDeletePage(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		ingredientCategoryKey = self.request.get('ingredientCategoryKey')
		ingredientCategory = db.get(ingredientCategoryKey)
		ingredientCategory.delete()
		deleteIngredientCategory(ingredientCategoryKey)
		self.redirect('/ingredientCategory')

























