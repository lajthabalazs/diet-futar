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
from dishCategory import DishCategoryPage, DishCategoryDeletePage
from order_overview import ChefReviewOrdersPage, DeliveryReviewOrdersPage, DeliveryPage
from user_admin import UserListPage, UserOverviewPage, SwitchToUserPage
from index import CaloryCalculator, GooglePage, AboutPage,\
	ContactsPage
from siteAdmin import SetupPage, AdminConsolePage,\
	ScheduleMainenencePage, EndMainenencePage, EveryUsersOrderPage,\
	ZipCodeEditorPage
from userWeeks import WeeksListPage
from maintenence import MaintenencePage
from christmasLunch import ChristmasLunchPage, InitChristmasLunchPage
from webshopAdmin import ItemListPage, UsersOrdersPage
from webshopUser import UserWebshopOrderListPage, UserWebshopOrderDetailsPage, UserWebshopPostMessagePage,\
	WebshopItemDetailsPage
from deliveryCosts import AboutDeliveryPage
from logViewer import ViewLogs
from userMap import UserMapPage

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key'}
# Check if site is under maintenence
app = webapp2.WSGIApplication([
										("/", MenuOrderPage),
										(SetupPage.URL, SetupPage),
										(AdminConsolePage.URL, AdminConsolePage),
										(MaintenencePage.URL, MaintenencePage),
										(ScheduleMainenencePage.URL, ScheduleMainenencePage),
										(EndMainenencePage.URL, EndMainenencePage),
										(EveryUsersOrderPage.URL, EveryUsersOrderPage),
										(InitChristmasLunchPage.URL, InitChristmasLunchPage),
										(ZipCodeEditorPage.URL, ZipCodeEditorPage),
										(ViewLogs.URL, ViewLogs),
										(UserMapPage.URL, UserMapPage),
										
										
										('/google24f0feb13afae7e0.html', GooglePage),
										(LoginPage.URL, LoginPage),
										(LogoutPage.URL, LogoutPage),
										(RegisterPage.URL, RegisterPage),
										(Referals.URL, Referals),
										(ActivatePage.URL, ActivatePage),
										(ActivationPendingPage.URL, ActivationPendingPage),
										(ChangePasswordPage.URL, ChangePasswordPage),
										(ForgotPassword.URL, ForgotPassword),
										(UserProfilePage.URL, UserProfilePage),
										(AddressPage.URL, AddressPage),
										(DeleteAddressPage.URL, DeleteAddressPage),

										(ConfirmOrder.URL, ConfirmOrder),
										(MenuOrderPage.URL, MenuOrderPage),
										(ClearOrderPage.URL, ClearOrderPage),
										(ReviewPendingOrderPage.URL, ReviewPendingOrderPage),
										(ReviewOrderedMenuPage.URL, ReviewOrderedMenuPage),
										(ChristmasLunchPage.URL, ChristmasLunchPage),
										(UserWebshopOrderListPage.URL, UserWebshopOrderListPage),
										
										(WebshopItemDetailsPage.URL, WebshopItemDetailsPage),
										(UserWebshopOrderDetailsPage.URL, UserWebshopOrderDetailsPage),
										(UsersOrdersPage.URL, UsersOrdersPage),
										(UserWebshopPostMessagePage.URL, UserWebshopPostMessagePage),

										(AboutPage.URL, AboutPage),
										(ContactsPage.URL, ContactsPage),
										(AboutDeliveryPage.URL, AboutDeliveryPage),
										(CaloryCalculator.URL, CaloryCalculator),

										(DishPage.URL, DishPage),
										(DishCategoryPage.URL, DishCategoryPage),
										(DishCategoryDeletePage.URL, DishCategoryDeletePage),
										(MenuEditPage.URL, MenuEditPage),
										(MenuWeekEditPage.URL, MenuWeekEditPage),
										(ModifyMenuItem.URL, ModifyMenuItem),
										(AddMenuItemComponent.URL, AddMenuItemComponent),
										(DeleteMenuItem.URL, DeleteMenuItem),
										(CreateComposit.URL,CreateComposit),
										(DeleteItemFromComposit.URL,DeleteItemFromComposit),
										(AddItemToComposit.URL, AddItemToComposit),
										(ModifyComposit.URL,ModifyComposit),
										(DeleteComposit.URL,DeleteComposit),
										
										(DeleteDishPage.URL, DeleteDishPage),
										(DeleteWishPage.URL, DeleteWishPage),
										(DishIngredientAddPage.URL, DishIngredientAddPage),
										(DishIngredientDeletePage.URL, DishIngredientDeletePage),
										(CategoryIngredientDeletePage.URL, CategoryIngredientDeletePage),
										(IngredientDeletePage.URL, IngredientDeletePage),
										(IngredientAddPage.URL, IngredientAddPage),
										(IngredientPage.URL, IngredientPage),
										(IngredientCategoryDeletePage.URL, IngredientCategoryDeletePage),
										(IngredientCategoryPage.URL, IngredientCategoryPage),
										(DeliveryReviewOrdersPage.URL, DeliveryReviewOrdersPage),
										(DeliveryPage.URL, DeliveryPage),
										(ChefReviewOrdersPage.URL, ChefReviewOrdersPage),
										(WishPage.URL, WishPage),
										
										(ItemListPage.URL, ItemListPage),

										(UserListPage.URL, UserListPage),
										(WeeksListPage.URL, WeeksListPage),
										(UserOverviewPage.URL, UserOverviewPage),
										(SwitchToUserPage.URL, SwitchToUserPage),
										],
										debug=True, config=config)