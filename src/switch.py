#!/usr/bin/env python

import jinja2
import os

import webapp2

from ingredient import IngredientDeletePage, IngredientAddPage, IngredientPage
from dish import DishPage, DeleteDishPage, DishIngredientAddPage, DishIngredientDeletePage
from wish import WishPage, DeleteWishPage
from user_forms import LoginPage, RegisterPage, LogoutPage, UserProfilePage,\
	ActivatePage, AddressPage, ChangePasswordPage, ActivationPendingPage, Referals,\
	ForgotPassword, DeleteAddressPage
from menu import MenuEditPage, AddMenuItemComponent,\
	ModifyMenuItem, CreateComposit, AddItemToComposit, DeleteItemFromComposit,\
	ModifyComposit, DeleteMenuItem, DeleteComposit, MenuWeekEditPage
from order import MenuOrderPage, ClearOrderPage, ReviewPendingOrderPage,\
	ConfirmOrder, ReviewOrderedMenuPage
from ingredientCategory import CategoryIngredientDeletePage,\
	IngredientCategoryPage, IngredientCategoryDeletePage
from keys import DISH_CATEGORY_URL, DISH_CATEGORY_DELETE_URL
from dishCategory import DishCategoryPage, DishCategoryDeletePage
from order_overview import ChefReviewOrdersPage, DeliveryReviewOrdersPage, DeliveryPage
from user_admin import UserListPage, UserOverviewPage, SwitchToUserPage
from index import CaloryCalculator, GooglePage, AboutPage,\
	ContactsPage, NewYearPage
from siteAdmin import SetupPage, AdminConsolePage,\
	ScheduleMainenencePage, EndMainenencePage, EveryUsersOrderPage,\
	ZipCodeEditorPage
from userWeeks import WeeksListPage
from maintenence import MaintenencePage
from christmasLunch import ChristmasLunchPage, InitChristmasLunchPage
from webshopAdmin import ItemListPage, UsersOrdersPage
from webshopUser import UserWebshopOrderListPage, UserWebshopOrderDetailsPage, UserWebshopPostMessagePage,\
	WebshopItemDetailsPage
from migrateAddresses import MigrateZipCodesToNumberFormat
from deliveryCosts import AboutDeliveryPage

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key'}
# Check if site is under maintenence
app = webapp2.WSGIApplication([
										('/', MenuOrderPage),
										('/setup', SetupPage),
										('/siteAdmin', AdminConsolePage),
										('/maintenence', MaintenencePage),
										('/scheduleMainenence', ScheduleMainenencePage),
										('/endMaintenence', EndMainenencePage),
										('/everyUsersOrder', EveryUsersOrderPage),
										('/initChristmasLunch', InitChristmasLunchPage),
										('/editZipCodes', ZipCodeEditorPage),
										('/migrateAddresses', MigrateZipCodesToNumberFormat),
										
										
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
										('/deleteAddress', DeleteAddressPage),

										('/confirmOrder', ConfirmOrder),
										('/order', MenuOrderPage),
										('/clearOrder', ClearOrderPage),
										('/pendingOrder', ReviewPendingOrderPage),
										('/personalMenu', ReviewOrderedMenuPage),
										('/christmasLunch', ChristmasLunchPage),
										('/userOrderList', UserWebshopOrderListPage),
										
										('/webshopItem', WebshopItemDetailsPage),
										('/webshopUserOrder', UserWebshopOrderDetailsPage),
										('/usersOrders', UsersOrdersPage),
										('/postOrderComment', UserWebshopPostMessagePage),

										('/about', AboutPage),
										('/contacts', ContactsPage),
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
										('/ingredientCategory', IngredientCategoryPage),
										('/deliveryReviewOrders', DeliveryReviewOrdersPage),
										('/deliverable', DeliveryPage),
										('/chefReviewOrders', ChefReviewOrdersPage),
										('/wish', WishPage),
										
										('/itemList', ItemListPage),

										('/userList', UserListPage),
										('/weeksList', WeeksListPage),
										('/userOverview', UserOverviewPage),
										('/switchToUser', SwitchToUserPage),
										],
										debug=True, config=config)