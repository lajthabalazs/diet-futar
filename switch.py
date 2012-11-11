#!/usr/bin/env python

import jinja2
import os

import webapp2

from ingredient import IngredientDeletePage, IngredientAddPage, IngredientPage
from dish import DishPage, DeleteDishPage, DishIngredientAddPage, DishIngredientDeletePage
from wish import WishPage, DeleteWishPage
from user_forms import LoginPage, RegisterPage, LogoutPage, UserProfilePage,\
	ActivatePage, AddressPage, ChangePasswordPage, ActivationPendingPage, Referals
from menu import MenuEditPage, AddMenuItemComponent,\
	ModifyMenuItem, CreateComposit, AddItemToComposit, DeleteItemFromComposit,\
	ModifyComposit, DeleteMenuItem, DeleteComposit, MenuWeekEditPage
from order import MenuOrderPage, ClearOrderPage, ReviewPendingOrderPage,\
	ConfirmOrder, PreviousOrders, PreviousOrder, ReviewOrderedMenuPage
from ingredientCategory import CategoryIngredientDeletePage,\
	IngredientCategoryPage, IngredientCategoryDeletePage
from keys import DISH_CATEGORY_URL, DISH_CATEGORY_DELETE_URL
from dishCategory import DishCategoryPage, DishCategoryDeletePage
from order_overview import ChefReviewOrdersPage, ChefReviewToMakePage,\
	DeliveryReviewOrdersPage, DeliveryPage
from user_admin import UserListPage
from index import AboutPage

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key',
												}
#app = webapp2.WSGIApplication([('/', TmpMainPage)],
#										debug=True, config=config)


app = webapp2.WSGIApplication([('/', MenuOrderPage),
										('/login', LoginPage),
										('/logout', LogoutPage),
										('/registration', RegisterPage),
										('/referred', Referals),
										('/activate', ActivatePage),
										('/activationPending', ActivationPendingPage),
										('/changePassword', ChangePasswordPage),
										('/profile', UserProfilePage),
										('/address', AddressPage),
										('/dish', DishPage),
										('/about', AboutPage),
										(DISH_CATEGORY_URL, DishCategoryPage),
										(DISH_CATEGORY_DELETE_URL, DishCategoryDeletePage),
										('/wish', WishPage),
										('/menuEdit', MenuEditPage),
										('/menuWeekEdit', MenuWeekEditPage),
										('/modifyMenuItem', ModifyMenuItem),
										('/addMenuItemComponent',AddMenuItemComponent),
										('/deleteMenuItem', DeleteMenuItem),
										('/createComposit',CreateComposit),
										('/deleteItemFromComposit',DeleteItemFromComposit),
										('/addItemToComposit',AddItemToComposit),
										('/modifyComposit',ModifyComposit),
										('/deleteComposit',DeleteComposit),
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
										('/userList', UserListPage),
										('/user', UserListPage),
										('/confirmOrder', ConfirmOrder),
										('/previousOrders', PreviousOrders),
										('/previousOrder', PreviousOrder),
										('/ingredientCategory', IngredientCategoryPage),
										('/chefReviewToMake', ChefReviewToMakePage),
										('/deliveryReviewOrders', DeliveryReviewOrdersPage),
										('/deliverable', DeliveryPage),
										('/chefReviewOrders', ChefReviewOrdersPage)],
										debug=True, config=config)