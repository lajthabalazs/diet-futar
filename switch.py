#!/usr/bin/env python

import jinja2
import os

import webapp2

from ingredient import CategoryIngredientDeletePage, IngredientDeletePage,\
	IngredientAddPage, IngredientPage, IngredientCategoryPage,\
	IngredientCategoryDeletePage
from dish import DishPage, DeleteDishPage, DishIngredientAddPage,\
	DishIngredientDeletePage
from wish import WishPage, DeleteWishPage
from user_forms import LoginPage, RegisterPage, LogoutPage
from main import MainPage
from menu import DayMenuPage

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key',
												}
app = webapp2.WSGIApplication([('/', MainPage),
										('/login', LoginPage),
										('/logout', LogoutPage),
										('/registration', RegisterPage),
										('/dish', DishPage),
										('/wish', WishPage),
										('/weekly', DayMenuPage),
										('/deleteDish', DeleteDishPage),
										('/deleteWish', DeleteWishPage),
										('/addIngredientToDish', DishIngredientAddPage),
										('/deleteIngredientFromDish', DishIngredientDeletePage),
										('/deleteIngredientFromCategory', CategoryIngredientDeletePage),
										('/deleteIngredient', IngredientDeletePage),
										('/addIngredientToCategory', IngredientAddPage),
										('/ingredient', IngredientPage),
										('/deleteIngredientCategory', IngredientCategoryDeletePage),
										('/ingredientCategory', IngredientCategoryPage)],
										debug=True, config=config)
























