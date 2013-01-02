#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler, getBaseDate, getFormDate, getMonday
import datetime
from model import Composit, CompositMenuItemListItem
from user_management import isUserCook
from order import dayNames
from cache_menu_item import addMenuItem, modifyMenuItem, deleteMenuItem,\
	getDaysMenuItems, getDaysAvailableMenuItems
from cache_composit import addComposit, addMenuItemToComposit, modifyComposit,\
	deleteComposit, getDaysComposits
from cache_dish_category import getCategoryWithDishes, getDishCategories
from cache_dish import getDishes
#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def getDay(day, dayIndex, availableMenuItems):
	dayObject={}
	dayObject["day"]=dayNames[dayIndex]
	dayObject["date"]=day
	dayObject["availableMenuItems"]=availableMenuItems
	return dayObject

def getDaysItemsForCategory(categoryKey, actualDay, dayIndex, availableMenuItems):
	actualDayObject={}
	actualDayObject["day"]=dayNames[dayIndex]
	actualDayObject["date"]=actualDay
	menuItems = getDaysMenuItems(actualDay, categoryKey)
	composits = getDaysComposits(actualDay, categoryKey)
	#Filter menu items
	actualMenuItems=[]
	actualComposits=[]
	"""for menuItem in menuItems:
		try:
			menuItem.occurrences[0]
			menuItem.alterable = False
		except IndexError:
			menuItem.alterable = True
		actualMenuItems.append(menuItem)
	for composit in composits:
		if composit.occurrences.count() > 0:
			composit.alterable = False
		else:
			composit.alterable = True
		actualComposits.append(composit)
	"""
	actualDayObject["menuItems"]=menuItems
	actualDayObject["composits"]=composits
	actualDayObject["availableMenuItems"]=availableMenuItems
	return actualDayObject

def getMenu(day, dayIndex, availableMenuItems):
	dishCategories=getDishCategories()
	menu=[]
	for category in dishCategories:
		if not category['canBeTopLevel']:
			continue
		actualCategoryObject={}
		actualCategoryObject['category']=category
		categoryKey=category['key']
		dishes = getCategoryWithDishes(category['key'])['dishes']
		availableDishes=sorted(dishes, key=lambda dish: dish['title'])
		actualCategoryObject['availableDishes']=availableDishes
		items=[]
		items.append(getDaysItemsForCategory(categoryKey, day, 0, availableMenuItems))
		actualCategoryObject["days"]=items
		menu.append(actualCategoryObject)
	return menu

class MenuWeekEditPage(BaseHandler):
	def get(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		day = getBaseDate(self)
		#Organize into days
		menu=[]
		dishCategories=getDishCategories()
		monday = getMonday(day)
		days=[]
		for i in range(0,5):
			actualDay=monday+datetime.timedelta(days=i)
			days.append(getDay(actualDay, i, getDaysAvailableMenuItems(actualDay)))
		for category in dishCategories:
			if not category['canBeTopLevel']:
				continue
			actualCategoryObject={}
			actualCategoryObject['category']=category
			categoryKey=category['key']
			dishes = getCategoryWithDishes(category['key'])['dishes']
			availableDishes=sorted(dishes, key=lambda dish: dish['title'])
			actualCategoryObject['availableDishes']=availableDishes
			items=[]
			for i in range(0,5):
				actualDay=monday+datetime.timedelta(days=i)
				items.append(getDaysItemsForCategory(categoryKey, actualDay, i, days[i]["availableMenuItems"]))
			actualCategoryObject["days"]=items
			menu.append(actualCategoryObject)
		# A single dish with editable ingredient list
		prevMonday=monday+datetime.timedelta(days = -7)
		nextMonday=monday+datetime.timedelta(days = 7)
		today=datetime.date.today()
		actualMonday = getMonday(today)
		allDishes=getDishes()
		template_values = {
			'days':days,
			'prev':prevMonday,
			'next':nextMonday,
			'actual':actualMonday,
			'menu':menu,
			'allDishes':allDishes
		}
		template = jinja_environment.get_template('templates/menuEdit.html')
		self.printPage(str(day), template.render(template_values), False, False)
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		else:
			#Adds a dish to current days menu
			day=getFormDate(self)
			dishKey=self.request.get('dishKey')
			if ((dishKey != None) and (dishKey != "")):
				addMenuItem(dishKey, day)
			self.redirect("/menuWeekEdit?day="+str(day))

class MenuEditPage(BaseHandler):
	def get(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		day = getBaseDate(self)
		#Determine the week
		nextCalendar=day.isocalendar()
		#Organize into days
		dayIndex=nextCalendar[2]-1
		availableMenuItems = getDaysAvailableMenuItems(day)
		days = []
		days.append(getDay(day, dayIndex, availableMenuItems))
		menu = getMenu(day, dayIndex, availableMenuItems)
		# A single dish with editable ingredient list
		prevDay=day+datetime.timedelta(days=-1)
		nextDay=day+datetime.timedelta(days=1)
		nextCalendar=nextDay.isocalendar()
		#Organize into days
		if nextCalendar[2]==6:
			nextDay=nextDay+datetime.timedelta(days=2)
		elif nextCalendar[2]==7:
			nextDay=nextDay+datetime.timedelta(days=1)
		prevCalendar=prevDay.isocalendar()
		#Organize into days
		if prevCalendar[2]==6:
			prevDay=prevDay+datetime.timedelta(days=-1)
		elif prevCalendar[2]==7:
			prevDay=prevDay+datetime.timedelta(days=-2)
		allDishes=getDishes()
		template_values = {
			'days':days,
			'prev':prevDay,
			'next':nextDay,
			'menu':menu,
			'allDishes':allDishes
		}
		template = jinja_environment.get_template('templates/menuEdit.html')
		self.printPage(str(day), template.render(template_values), False, False)
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		else:
			#Adds a dish to current days menu
			day=getFormDate(self)
			dishKey=self.request.get('dishKey')
			if ((dishKey != None) and (dishKey != "")):
				addMenuItem(dishKey, day)
			self.redirect("/menuEdit?day="+str(day))
			
class CreateComposit(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		else:
			#Adds a composit to current days menu
			day = getFormDate(self)
			categoryKey = self.request.get('dishCategoryKey')
			addComposit(categoryKey, day)
			self.redirect("/menuEdit?day="+str(day))

class AddItemToComposit(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		else:
			#Adds an item to composit
			day = getFormDate(self)
			compositKey = self.request.get("compositKey")
			menuItemKey = self.request.get("menuItem")
			addMenuItemToComposit(compositKey, menuItemKey)
			self.redirect("/menuEdit?day="+ str(day))

class DeleteItemFromComposit(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		else:
			#Adds an item to composit
			day = getFormDate(self)
			compositItem = CompositMenuItemListItem.get(self.request.get("componentKey"))
			if compositItem.composit.occurrences.count()==0:
				compositItem.delete()
				modifyComposit(compositItem.composit)
			self.redirect("/menuEdit?day="+str(day))
			
class ModifyComposit(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		else:
			day = getFormDate(self)
			compositKey=self.request.get('compositKey')
			if ((compositKey != None) and (compositKey != "")):
				composit=Composit.get(compositKey)
				if (composit != None):
					if composit.occurrences.count()==0:
						#Save new price
						composit.price = int(self.request.get('price'))
						composit.put()
						modifyComposit(composit)
			self.redirect("/menuEdit?day="+str(day))
			
class DeleteComposit(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		else:
			day = getFormDate(self)
			#Deletes a dish from current days menu
			compositKey=self.request.get('compositKey')
			if ((compositKey != None) and (compositKey != "")):
				composit=Composit.get(compositKey)
				if composit != None and composit.occurrences.count() == 0:
					for component in composit.components:
						component.delete()
					composit.delete()
					deleteComposit(composit)
				else:
					composit.active = False
					composit.put()
					modifyComposit(composit)
			self.redirect("/menuEdit?day="+str(day))

class ModifyMenuItem(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		else:
			day = getFormDate(self)
			menuItemKey=self.request.get('menuItemKey')
			if ((menuItemKey != None) and (menuItemKey != "")):
				menuItem=db.get(menuItemKey)
				if (menuItem != None) and menuItem.occurrences.count()==0:
					#Save new price
					menuItem.price = int(self.request.get('price'))
					menuItem.put()
					modifyMenuItem(menuItem)
			self.redirect("/menuEdit?day="+str(day))

class AddMenuItemComponent(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		else:
			sumprice = 0
			day = getFormDate(self)
			#Adds a dish to menu item
			menuItemKey=self.request.get('menuItemKey')
			if ((menuItemKey != None) and (menuItemKey != "")):
				menuItem=db.get(menuItemKey)
				if (menuItem != None) and menuItem.occurrences.count()==0:
					sumprice = menuItem.dish.price
					if sumprice == None:
						sumprice = 0
					#Get the dish
					dishKey = self.request.get('componentDishKey')
					#Create a menu item for the dish
					addMenuItem(dishKey, day, menuItem)
					#Add the menu item to the current MenuItem
					for component in menuItem.components:
						if (component.dish.price != None):
							sumprice = sumprice + component.dish.price
					menuItem.sumprice = sumprice
					menuItem.put()
					modifyMenuItem(menuItem)
			self.redirect("/menuEdit?day="+str(day))
			
class DeleteMenuItem(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		else:
			day = getFormDate(self)
			#Deletes a dish from current days menu
			menuItemKey=self.request.get('menuItemKey')
			if ((menuItemKey != None) and (menuItemKey != "")):
				menuItem=db.get(menuItemKey)
				if menuItem != None and menuItem.occurrences.count() == 0 and menuItem.composits.count() == 0:
					containingMenuItem = menuItem.containingMenuItem
					if containingMenuItem != None:
						#"Deleting sub item"
						sumprice = menuItem.containingMenuItem.dish.price
						if sumprice == None:
							sumprice = 0
						for component in menuItem.containingMenuItem.components:
							if component.dish.price != None:
								sumprice = sumprice + component.dish.price
						if menuItem.dish.price != None:
							sumprice = sumprice - menuItem.dish.price
						menuItem.containingMenuItem.sumprice = sumprice
						menuItem.containingMenuItem.put()
					if menuItem.components != None:
						for component in menuItem.components:
							component.delete()
							deleteMenuItem(component)
					menuItem.delete()
					deleteMenuItem(menuItem)
					if containingMenuItem != None:
						modifyMenuItem(menuItem.containingMenuItem)
				else:
					menuItem.active = False
					menuItem.put()
					modifyMenuItem(menuItem)
			self.redirect("/menuEdit?day="+str(day))

















