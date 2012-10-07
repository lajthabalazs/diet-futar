#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler, getBaseDate, getFormDate
import datetime
from model import MenuItem, DishCategory, Dish, Composit,\
	CompositMenuItemListItem
from user_management import isUserCook
from order import dayNames
from cache import getDaysMenuItems
#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MenuWeekEditPage(BaseHandler):
	def get(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		day = getBaseDate(self)
		#Determine the week
		calendar=day.isocalendar()
		#Organize into days
		menu=[]
		dishCategories=DishCategory.gql("ORDER BY index")
		monday=day+datetime.timedelta(days=-calendar[2]+1)
		sunday=day+datetime.timedelta(days=-calendar[2]+7)
		days=[]
		for i in range(0,5):
			actualDay=monday+datetime.timedelta(days=i)
			actualDayObject={}
			actualDayObject["day"]=dayNames[i]
			actualDayObject["date"]=monday+datetime.timedelta(days=i)
			menuItems = getDaysMenuItems()
			actualDayObject["availableMenuItems"]=menuItems
			days.append(actualDayObject)
		for category in dishCategories:
			actualCategoryObject={}
			actualCategoryObject['category']=category
			categoryKey=str(category.key())
			availableDishes=sorted(category.dishes, key=lambda dish: dish.title)
			actualCategoryObject['availableDishes']=availableDishes
			menu.append(actualCategoryObject)
			items=[]
			for i in range(0,5):
				actualDay=monday+datetime.timedelta(days=i)
				actualDayObject={}
				actualDayObject["day"]=dayNames[i]
				actualDayObject["date"]=actualDay
				menuItems = MenuItem.all().filter("categoryKey = ", categoryKey).filter("day = ", actualDay).filter("containingMenuItem = ", None)
				composits=Composit.all().filter("categoryKey = ", categoryKey).filter("day = ", actualDay)
				#Filter menu items
				actualMenuItems=[]
				actualComposits=[]
				availableMenuItems=days[i]["availableMenuItems"]
				for menuItem in menuItems:
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
				#Get every menu item for the day
				actualDayObject["menuItems"]=actualMenuItems
				actualDayObject["composits"]=actualComposits
				actualDayObject["availableMenuItems"]=availableMenuItems
				items.append(actualDayObject)
			actualCategoryObject["days"]=items
		# A single dish with editable ingredient list
		prevMonday=day+datetime.timedelta(days=-calendar[2]+1-7)
		nextMonday=day+datetime.timedelta(days=-calendar[2]+1+7)
		today=datetime.date.today()
		todayCalendat=today.isocalendar()
		actualMonday=today+datetime.timedelta(days=-todayCalendat[2]+1)
		allDishes=Dish.gql("ORDER BY title")
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
				dish=db.get(dishKey)
				menuItem=MenuItem()
				menuItem.day=day
				menuItem.dish=dish
				menuItem.price = dish.price
				menuItem.sumprice = dish.price
				menuItem.categoryKey=str(dish.category.key())
				menuItem.put()
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
		menu=[]
		dishCategories=DishCategory.gql("ORDER BY index")
		dayIndex=nextCalendar[2]-1
		days=[]
		actualDay=day
		actualDayObject={}
		actualDayObject["day"]=dayNames[dayIndex]
		actualDayObject["date"]=day
		menuItems = MenuItem.all().filter("day = ", actualDay).filter("containingMenuItem = ", None)
		actualDayObject["availableMenuItems"]=menuItems
		days.append(actualDayObject)
		for category in dishCategories:
			actualCategoryObject={}
			actualCategoryObject['category']=category
			categoryKey=str(category.key())
			availableDishes=sorted(category.dishes, key=lambda dish: dish.title)
			actualCategoryObject['availableDishes']=availableDishes
			menu.append(actualCategoryObject)
			items=[]
			actualDay=day
			actualDayObject={}
			actualDayObject["day"]=dayNames[dayIndex]
			actualDayObject["date"]=actualDay
			menuItems = MenuItem.all().filter("categoryKey = ", categoryKey).filter("day = ", actualDay).filter("containingMenuItem = ", None)
			composits=Composit.all().filter("categoryKey = ", categoryKey).filter("day = ", actualDay)
			#Filter menu items
			actualMenuItems=[]
			actualComposits=[]
			availableMenuItems=days[0]["availableMenuItems"]
			for menuItem in menuItems:
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
			#Get every menu item for the day
			actualDayObject["menuItems"]=actualMenuItems
			actualDayObject["composits"]=actualComposits
			actualDayObject["availableMenuItems"]=availableMenuItems
			items.append(actualDayObject)
			actualCategoryObject["days"]=items
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
		allDishes=Dish.gql("ORDER BY title")
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
				dish=db.get(dishKey)
				menuItem=MenuItem()
				menuItem.day=day
				menuItem.dish=dish
				menuItem.price = dish.price
				menuItem.sumprice = dish.price
				menuItem.categoryKey=str(dish.category.key())
				menuItem.put()
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
			composit = Composit()
			composit.day=day
			composit.category=DishCategory.get(categoryKey)
			composit.categoryKey=str(categoryKey)
			composit.put()
			self.redirect("/menuEdit?day="+str(day))

class AddItemToComposit(BaseHandler):
	def post(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		else:
			#Adds an item to composit
			day = getFormDate(self)
			composit = Composit.get(self.request.get("compositKey"))
			if composit.occurrences.count()==0:
				menuItem = MenuItem.get(self.request.get("menuItem"))
				compositItem = CompositMenuItemListItem()
				compositItem.menuItem = menuItem
				compositItem.composit = composit
				compositItem.put()
			self.redirect("/menuEdit?day="+str(day))

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
					composit.delete()
				else:
					composit.active = False
					composit.put()
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
					#Get the dish
					dishKey = self.request.get('componentDishKey')
					dish = db.get(dishKey)
					#Create a menu item for the dish
					componentItem = MenuItem()
					componentItem.dish = dish
					componentItem.day = menuItem.day
					#Add the menu item to the current MenuItem
					componentItem.containingMenuItem = menuItem
					componentItem.put()
					for component in menuItem.components:
						if (component.dish.price != None):
							sumprice = sumprice + component.dish.price
					menuItem.sumprice = sumprice
					menuItem.put()
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
					if menuItem.containingMenuItem != None:
						sumprice = menuItem.containingMenuItem.dish.price
						for component in menuItem.containingMenuItem.components:
							if (component.dish.price != None):
								sumprice = sumprice + component.dish.price
						if menuItem.dish.price != None:
							sumprice = sumprice - menuItem.dish.price
						menuItem.containingMenuItem.sumprice = sumprice
						menuItem.containingMenuItem.put()
					menuItem.delete()
				else:
					menuItem.active = False
					menuItem.put()
			self.redirect("/menuEdit?day="+str(day))

















