from google.appengine.ext import db
from model import DishCategory
import jinja2
import os
from base_handler import BaseHandler
from keys import DISH_CATEGORY_KEY, DISH_KEY, DISH_CATEGORY_URL, DISH_CATEGORY_NAME,\
	DISH_CATEGORY_DELETE_URL, DISH_CATEGORY_ADD_URL, DISH_CATEGORY_INDEX
from user_management import isUserAdmin

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class CategoryDishDeletePage(BaseHandler):
	def post(self):
		if(not isUserAdmin(self)):
			self.redirect("/")	
		category = db.get(self.request.get(DISH_CATEGORY_KEY))
		dish = db.get(self.request.get(DISH_KEY))
		dish.category=None
		dish.put()
		self.redirect(DISH_CATEGORY_URL+'?'+DISH_CATEGORY_KEY+'=%s' % category.key())

class DishCategoryPage(BaseHandler):
	def post(self):
		dishCategoryKey=self.request.get(DISH_CATEGORY_KEY)
		if ((dishCategoryKey != None) and (dishCategoryKey != "")):
			dishCategory=db.get(self.request.get(DISH_CATEGORY_KEY))
		else:
			dishCategory = DishCategory()
			dishCategory.name = self.request.get(DISH_CATEGORY_NAME)
		try:
			dishCategory.index = int(self.request.get(DISH_CATEGORY_INDEX))
			dishCategory.isMenu = self.request.get('isMenuCategory', default_value="no")=='yes'
		except ValueError:
			dishCategory.index=0
		dishCategory.put()
		self.redirect(DISH_CATEGORY_URL)
	def get(self):
		dishCategoryKey=self.request.get(DISH_CATEGORY_KEY)
		if ((dishCategoryKey != None) and (dishCategoryKey != "")):
		# List every ingredient in the category
			dishCategory = db.get(self.request.get(DISH_CATEGORY_KEY))
			template_values = {
				'dishCategory': dishCategory,
				'add_url':DISH_CATEGORY_ADD_URL,
				'delete_url':DISH_CATEGORY_DELETE_URL
			}
			template = jinja_environment.get_template('templates/dish_category.html')
			self.printPage(dishCategory.name, template.render(template_values), False, False)
		else:
		# All categories
			ingredientCategories =DishCategory.gql("ORDER BY index")
			template_values = {
				'dishCategories': ingredientCategories,
				'delete_url':DISH_CATEGORY_DELETE_URL
			}
			template = jinja_environment.get_template('templates/dish_category_list.html')
			self.printPage("Etel kategoriak", template.render(template_values), False, False)

class DishCategoryDeletePage(BaseHandler):
	def post(self):
		dishCategory = db.get(self.request.get('dishCategoryKey'))	  
		dishCategory.delete()
		self.redirect(DISH_CATEGORY_URL+'?'+DISH_CATEGORY_KEY+'=%s' % self.request.get('ingredientCategoryKey'))
























