#!/usr/bin/env python

import webapp2
import jinja2
import os

from ingredient import CategoryIngredientDeletePage, IngredientDeletePage,\
	IngredientAddPage, IngredientPage, IngredientCategoryPage,\
	IngredientCategoryDeletePage
from dish import MainPage, DishPage, DeleteDishPage, DishIngredientAddPage,\
	DishIngredientDeletePage
from wishlist import WishPage, DeleteWishPage

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key',
												}
app = webapp2.WSGIApplication([('/', MainPage),
										('/dish', DishPage),
										('/wish', WishPage),
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
























