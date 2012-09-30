#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
import datetime
from model import MenuItem, DishCategory, Dish, Composit,\
	CompositMenuItemListItem
from user_management import isUserAdmin
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
class MenuEditPage(BaseHandler):
	def get(self):
		day=datetime.date.today()
		requestDay=self.request.get('day')
		if ((requestDay != None) and (requestDay != "")):
			parts=requestDay.rsplit("-")
			day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
		#Determine the week
		calendar=day.isocalendar()
		#Organize into days
		menu=[]
		dayNames=["Hetfo","Kedd","Szerda","Csutortok","Pentek","Szombat","Vasarnap"]
		dishCategories=DishCategory.gql("ORDER BY index")
		monday=day+datetime.timedelta(days=-calendar[2]+1)
		sunday=day+datetime.timedelta(days=-calendar[2]+7)
		originalItems=MenuItem.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
		menuItems=sorted(originalItems, key=lambda item:item.dish.title)
		composits=Composit.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
		for category in dishCategories:
			actualCategoryObject={}
			actualCategoryObject['category']=category
			availableDishes=sorted(category.dishes, key=lambda dish: dish.title)
			actualCategoryObject['availableDishes']=availableDishes
			menu.append(actualCategoryObject)
			items=[]
			for i in range(0,5):
				actualDay=monday+datetime.timedelta(days=i)
				actualDayObject={}
				actualDayObject["day"]=dayNames[i]
				actualDayObject["date"]=actualDay
				#Filter menu items
				actualMenuItems=[]
				actualComposits=[]
				availableMenuItems=[]
				for menuItem in menuItems:
					try:
						menuItem.dish.category
					except ReferencePropertyResolveError:
						continue
					if (menuItem.dish.category.key()==category.key()):
						try:
							menuItem.containingMenuItem
						# If menu item's parent is deleted, delete the menu item too
						except ReferencePropertyResolveError:
							menuItem.delete()
							continue
						if menuItem.day==actualDay and menuItem.containingMenuItem == None:
							actualMenuItems.append(menuItem)
				for composit in composits:
					try:
						composit.category
					except ReferencePropertyResolveError:
						continue
					if composit.category.key()==category.key():
						if composit.day==actualDay:
							actualComposits.append(composit)
				#Get every menu item for the day
				for menuItem in menuItems:
					try:
						menuItem.containingMenuItem
					# If menu item's parent is deleted, delete the menu item too
					except ReferencePropertyResolveError:
						menuItem.delete()
						continue
					if menuItem.day==actualDay and menuItem.containingMenuItem==None:
						availableMenuItems.append(menuItem)
				actualDayObject['availableMenuItems']=availableMenuItems
				actualDayObject["menuItems"]=actualMenuItems
				actualDayObject["composits"]=actualComposits
				items.append(actualDayObject)
			actualCategoryObject["days"]=items
		days=[]
		for i in range(0,5):
			actualDay=monday+datetime.timedelta(days=i)
			actualDayObject={}
			actualDayObject["day"]=dayNames[i]
			actualDayObject["date"]=monday+datetime.timedelta(days=i)
			days.append(actualDayObject)
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
		if(not isUserAdmin):
			self.redirect("/menuEdit")	
		else:
			#Adds a dish to current days menu
			day=datetime.date.today()
			requestDay=self.request.get('formDay')
			if ((requestDay != None) and (requestDay != "")):
				parts=requestDay.rsplit("-")
				day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
			dishKey=self.request.get('dishKey')
			if ((dishKey != None) and (dishKey != "")):
				dish=db.get(dishKey)
				menuItem=MenuItem()
				menuItem.day=day
				menuItem.dish=dish
				menuItem.price = dish.price
				menuItem.sumprice = dish.price
				menuItem.put()
			self.redirect("/menuEdit?day="+str(day))
			
class CreateComposit(BaseHandler):
	def post(self):
		if(not isUserAdmin):
			self.redirect("/menuEdit")	
		else:
			#Adds a composit to current days menu
			day=datetime.date.today()
			requestDay=self.request.get('formDay')
			if ((requestDay != None) and (requestDay != "")):
				parts=requestDay.rsplit("-")
				day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
			categoryKey = self.request.get('dishCategoryKey')
			composit = Composit()
			composit.day=day
			composit.category=DishCategory.get(categoryKey)
			composit.put()
			self.redirect("/menuEdit?day="+str(day))

class AddItemToComposit(BaseHandler):
	def post(self):
		if(not isUserAdmin):
			self.redirect("/menuEdit")	
		else:
			#Adds an item to composit
			day=datetime.date.today()
			requestDay=self.request.get('formDay')
			if ((requestDay != None) and (requestDay != "")):
				parts=requestDay.rsplit("-")
				day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
			composit = Composit.get(self.request.get("compositKey"))
			menuItem = MenuItem.get(self.request.get("menuItem"))
			compositItem = CompositMenuItemListItem()
			compositItem.menuItem = menuItem
			compositItem.composit = composit
			compositItem.put()
			self.redirect("/menuEdit?day="+str(day))

class DeleteItemFromComposit(BaseHandler):
	def post(self):
		if(not isUserAdmin):
			self.redirect("/menuEdit")	
		else:
			#Adds an item to composit
			day=datetime.date.today()
			requestDay=self.request.get('formDay')
			if ((requestDay != None) and (requestDay != "")):
				parts=requestDay.rsplit("-")
				day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
			compositItem = CompositMenuItemListItem.get(self.request.get("componentKey"))
			compositItem.delete()
			self.redirect("/menuEdit?day="+str(day))
			
class ModifyComposit(BaseHandler):
	def post(self):
		if(not isUserAdmin(self)):
			self.redirect("/menuEdit")
		else:
			dayStr=""
			requestDay=self.request.get('formDay')
			if ((requestDay != None) and (requestDay != "")):
				dayStr = requestDay
			compositKey=self.request.get('compositKey')
			if ((compositKey != None) and (compositKey != "")):
				composit=Composit.get(compositKey)
				if (composit != None):
					#Save new price
					composit.price = int(self.request.get('price'))
					composit.put()
			self.redirect("/menuEdit?day="+dayStr)
			
class DeleteComposit(BaseHandler):
	def post(self):
		if(not isUserAdmin(self)):
			self.redirect("/menuEdit")
		else:
			day=datetime.date.today()
			requestDay=self.request.get('formDay')
			if ((requestDay != None) and (requestDay != "")):
				parts=requestDay.rsplit("-")
				day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
			#Deletes a dish from current days menu
			compositKey=self.request.get('compositKey')
			if ((compositKey != None) and (compositKey != "")):
				composit=Composit.get(compositKey)
				if (composit != None):
					composit.delete()
			self.redirect("/menuEdit?day="+str(day))

class ModifyMenuItem(BaseHandler):
	def post(self):
		if(not isUserAdmin(self)):
			self.redirect("/menuEdit")
		else:
			dayStr=""
			requestDay=self.request.get('formDay')
			if ((requestDay != None) and (requestDay != "")):
				dayStr = requestDay
			menuItemKey=self.request.get('menuItemKey')
			if ((menuItemKey != None) and (menuItemKey != "")):
				menuItem=db.get(menuItemKey)
				if (menuItem != None):
					#Save new price
					menuItem.price = int(self.request.get('price'))
					menuItem.put()
			self.redirect("/menuEdit?day="+dayStr)

class AddMenuItemComponent(BaseHandler):
	def post(self):
		if(not isUserAdmin(self)):
			self.redirect("/menuEdit")
		else:
			sumprice = 0
			day=datetime.date.today()
			requestDay=self.request.get('formDay')
			if ((requestDay != None) and (requestDay != "")):
				parts=requestDay.rsplit("-")
				day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
			#Adds a dish to menu item
			menuItemKey=self.request.get('menuItemKey')
			if ((menuItemKey != None) and (menuItemKey != "")):
				menuItem=db.get(menuItemKey)
				if (menuItem != None):
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
		if(not isUserAdmin(self)):
			self.redirect("/menuEdit")
		else:
			day=datetime.date.today()
			requestDay=self.request.get('formDay')
			if ((requestDay != None) and (requestDay != "")):
				parts=requestDay.rsplit("-")
				day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
			#Deletes a dish from current days menu
			menuItemKey=self.request.get('menuItemKey')
			if ((menuItemKey != None) and (menuItemKey != "")):
				menuItem=db.get(menuItemKey)
				if (menuItem != None):
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
			self.redirect("/menuEdit?day="+str(day))

















