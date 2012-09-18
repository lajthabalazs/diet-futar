#!/usr/bin/env python

import jinja2
import os

import webapp2

from ingredient import IngredientDeletePage, IngredientAddPage, IngredientPage
from dish import DishPage, DeleteDishPage, DishIngredientAddPage, DishIngredientDeletePage
from wish import WishPage, DeleteWishPage
from user_forms import LoginPage, RegisterPage, LogoutPage
from main import MainPage
from menu import MenuEditPage,MenuDeleteDishPage, AddMenuItemComponent,\
	ModifyMenuItem
from order import MenuOrderPage, ClearOrderPage, ReviewPendingOrderPage,\
	ConfirmOrder, PreviousOrders, PreviousOrder, ReviewOrderedMenuPage
from ingredientCategory import CategoryIngredientDeletePage,\
	IngredientCategoryPage, IngredientCategoryDeletePage
from keys import DISH_CATEGORY_URL, DISH_CATEGORY_DELETE_URL
from dishCategory import DishCategoryPage, DishCategoryDeletePage

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key',
												}
app = webapp2.WSGIApplication([('/', MainPage),
										('/login', LoginPage),
										('/logout', LogoutPage),
										('/registration', RegisterPage),
										('/dish', DishPage),
										(DISH_CATEGORY_URL, DishCategoryPage),
										(DISH_CATEGORY_DELETE_URL, DishCategoryDeletePage),
										('/wish', WishPage),
										('/menuEdit', MenuEditPage),
										('/modifyMenuItem', ModifyMenuItem),
										('/addMenuItemComponent',AddMenuItemComponent),
										('/deleteMenuItem', MenuDeleteDishPage),
										('/order', MenuOrderPage),
										('/clearOrder', ClearOrderPage),
										('/pendingOrder', ReviewPendingOrderPage),
										('/personalMenu', ReviewOrderedMenuPage),
										('/clearOrder', ClearOrderPage),
										('/deleteDish', DeleteDishPage),
										('/deleteWish', DeleteWishPage),
										('/addIngredientToDish', DishIngredientAddPage),
										('/deleteIngredientFromDish', DishIngredientDeletePage),
										('/deleteIngredientFromCategory', CategoryIngredientDeletePage),
										('/deleteIngredient', IngredientDeletePage),
										('/addIngredientToCategory', IngredientAddPage),
										('/ingredient', IngredientPage),
										('/deleteIngredientCategory', IngredientCategoryDeletePage),
										('/confirmOrder', ConfirmOrder),
										('/previousOrders', PreviousOrders),
										('/previousOrder', PreviousOrder),
										('/ingredientCategory', IngredientCategoryPage)],
										debug=True, config=config)
























