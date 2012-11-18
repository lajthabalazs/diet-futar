#!/usr/bin/env python

import jinja2
import os

import webapp2

from ingredient import IngredientDeletePage, IngredientAddPage, IngredientPage
from dish import DishPage, DeleteDishPage, DishIngredientAddPage, DishIngredientDeletePage
from wish import WishPage, DeleteWishPage
from user_forms import LoginPage, RegisterPage, LogoutPage, UserProfilePage,\
	ActivatePage, AddressPage, ChangePasswordPage, ActivationPendingPage, Referals,\
	ForgotPassword
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
from user_admin import UserListPage, UserOverviewPage
from index import AboutDeliveryPage, CaloryCalculator, GooglePage

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key',
												}
#app = webapp2.WSGIApplication([('/', TmpMainPage)],
#										debug=True, config=config)


app = webapp2.WSGIApplication([('/', MenuOrderPage),
										('/google24f0feb13afae7e0.html', GooglePage),
										('/login', LoginPage),
										('/logout', LogoutPage),
										('/registration', RegisterPage),
										('/referred', Referals),
										('/activate', ActivatePage),
										('/activationPending', ActivationPendingPage),
										('/changePassword', ChangePasswordPage),
										('/forgotPassword', ForgotPassword),
										('/profile', UserProfilePage),
										('/address', AddressPage),

										('/confirmOrder', ConfirmOrder),
										('/previousOrders', PreviousOrders),
										('/previousOrder', PreviousOrder),
										('/order', MenuOrderPage),
										('/clearOrder', ClearOrderPage),
										('/pendingOrder', ReviewPendingOrderPage),
										('/personalMenu', ReviewOrderedMenuPage),

										('/aboutDelivery', AboutDeliveryPage),
										('/caloryCalculator', CaloryCalculator),

										('/dish', DishPage),
										(DISH_CATEGORY_URL, DishCategoryPage),
										(DISH_CATEGORY_DELETE_URL, DishCategoryDeletePage),
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
										('/userOverview', UserOverviewPage),
										('/ingredientCategory', IngredientCategoryPage),
										('/chefReviewToMake', ChefReviewToMakePage),
										('/deliveryReviewOrders', DeliveryReviewOrdersPage),
										('/deliverable', DeliveryPage),
										('/chefReviewOrders', ChefReviewOrdersPage),
										('/wish', WishPage),
										],
										debug=True, config=config)