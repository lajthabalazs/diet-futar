from google.appengine.ext import db
from model import DishCategory
import jinja2
import os
from base_handler import BaseHandler
from keys import DISH_CATEGORY_KEY, DISH_KEY, DISH_CATEGORY_URL, DISH_CATEGORY_NAME,\
	DISH_CATEGORY_DELETE_URL, DISH_CATEGORY_ADD_URL, DISH_CATEGORY_INDEX,\
	DISH_CATEGORY_ABBREVIATION
from user_management import isUserCook
from cache_dish_category import getDishCategories, getCategoryWithDishes,\
	modifyCategory, deleteCategory, addCategory
from cache_dish import modifyDish

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class CategoryDishDeletePage(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		category = db.get(self.request.get(DISH_CATEGORY_KEY))
		dish = db.get(self.request.get(DISH_KEY))
		dish.category = None
		modifyDish(dish);
		dish.put()
		self.redirect(DISH_CATEGORY_URL+'?'+DISH_CATEGORY_KEY+'=%s' % category.key())

class DishCategoryPage(BaseHandler):
	URL = DISH_CATEGORY_URL
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		dishCategoryKey = self.request.get("dishCategoryKey")
		if ((dishCategoryKey != None) and (dishCategoryKey != "")):
			dishCategory=db.get(self.request.get(DISH_CATEGORY_KEY))
		else:
			dishCategory = DishCategory()
			dishCategory.name = self.request.get(DISH_CATEGORY_NAME)
		dishCategory.abbreviation = self.request.get(DISH_CATEGORY_ABBREVIATION)
		try:
			dishCategory.index = int(self.request.get(DISH_CATEGORY_INDEX))
		except ValueError:
			dishCategory.index = 0
		try:
			dishCategory.basePrice = int(self.request.get('basePrice'))
		except ValueError:
			dishCategory.basePrice = 0
		dishCategory.isExtra = self.request.get('isExtra', default_value="no")=='yes'
		dishCategory.isMenu = self.request.get('isMenuCategory', default_value="no")=='yes'
		dishCategory.canBeTopLevel = self.request.get('canBeTopLevel', default_value="no")=='yes'
		dishCategory.put()
		if (dishCategoryKey != None and dishCategoryKey != ""):
			modifyCategory(dishCategory);
		else:
			addCategory(dishCategory);
		self.redirect(DISH_CATEGORY_URL)
	def get(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		dishCategoryKey=self.request.get("dishCategoryKey")
		if ((dishCategoryKey != None) and (dishCategoryKey != "")):
		# List every ingredient in the category
			dishCategory = getCategoryWithDishes(dishCategoryKey);
			template_values = {
				'dishCategory': dishCategory,
				'add_url':DISH_CATEGORY_ADD_URL,
				'delete_url':DISH_CATEGORY_DELETE_URL
			}
			template = jinja_environment.get_template('templates/dishCategory/dish_category.html')
			self.printPage(dishCategory['name'], template.render(template_values), False, False)
		else:
		# All categories
			dishCategories=getDishCategories()
			template_values = {
				'dishCategories': dishCategories,
				'delete_url':DISH_CATEGORY_DELETE_URL
			}
			template = jinja_environment.get_template('templates/dishCategory/dish_category_list.html')
			self.printPage("Etel kategoriak", template.render(template_values), False, False)

class DishCategoryDeletePage(BaseHandler):
	URL = DISH_CATEGORY_DELETE_URL
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		dishCategoryKey = self.request.get('dishCategoryKey');
		dishCategory = db.get(dishCategoryKey)
		deleteCategory(dishCategoryKey);
		dishCategory.delete()
		self.redirect(DISH_CATEGORY_URL)
























