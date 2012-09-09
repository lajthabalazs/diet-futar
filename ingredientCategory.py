from google.appengine.ext import db
from model import IngredientCategory
import jinja2
import os
from base_handler import BaseHandler

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class CategoryIngredientDeletePage(BaseHandler):
	def post(self):
		category = db.get(self.request.get('ingredientCategoryKey'))
		ingredient = db.get(self.request.get('ingredientKey'))
		ingredient.category=None
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
			self.printPage(ingredientCategory.name, template.render(template_values), False, False)
		else:
		# All categories
			ingredientCategories = IngredientCategory.gql("ORDER BY name")
			template_values = {
				'ingredientCategories': ingredientCategories,
				'delete_url':"/deleteIngredientCategory"
			}
			template = jinja_environment.get_template('templates/ingredient_category_list.html')
			self.printPage("Alapanyag kategoriak", template.render(template_values), False, False)

class IngredientCategoryDeletePage(BaseHandler):
	def post(self):
		ingredientCategory = db.get(self.request.get('ingredientCategoryKey'))	  
		ingredientCategory.delete()
		self.redirect('/ingredientCategory')

























