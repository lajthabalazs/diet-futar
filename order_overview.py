#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
import datetime
from model import MenuItem, DishCategory
#from user_management import getUserBox

ACTUAL_ORDER="actualOrder"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

#An accumulated overview of every ordered item
class ChefReviewOrdersPage(BaseHandler):
	def get(self):
		day=datetime.date.today()
		requestDay=self.request.get('day')
		if ((requestDay != None) and (requestDay != "")):
			parts=requestDay.rsplit("-")
			day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
		#Determine the week
		calendar=day.isocalendar()
		#Organize into days
		menu=[] #Contains menu items
		dayNames=["Hetfo","Kedd","Szerda","Csutortok","Pentek","Szombat","Vasarnap"]
		dishCategories=DishCategory.gql("ORDER BY index")
		monday=day+datetime.timedelta(days=-calendar[2]+1)
		sunday=day+datetime.timedelta(days=-calendar[2]+7)
		originalItems=MenuItem.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
		menuItems=sorted(originalItems, key=lambda item:item.dish.title)
		for category in dishCategories:
			actualCategoryObject={}
			actualCategoryObject['category']=category
			items=[]
			itemsInRows=0
			for i in range(0,5):
				actualDay=monday+datetime.timedelta(days=i)
				actualDayObject={}
				actualDayObject["day"]=dayNames[i]
				actualDayObject["date"]=actualDay
				#Filter menu items
				actualMenuItems=[]
				for menuItem in menuItems:
					if (menuItem.dish.category.key()==category.key()) and (menuItem.day==actualDay) and (menuItem.containingMenuItem == None):
						menuItem.orderedQuantity = 0
						for order in menuItem.occurrences:
							menuItem.orderedQuantity = menuItem.orderedQuantity + order.itemCount
						if menuItem.orderedQuantity > 0:
							itemsInRows = itemsInRows + 1
							actualMenuItems.append(menuItem)
				actualDayObject["menuItems"]=actualMenuItems
				items.append(actualDayObject)
			actualCategoryObject["days"]=items
			if (itemsInRows > 0):
				menu.append(actualCategoryObject)
		days=[]
		for i in range(0,5):
			actualDayObject={}
			actualDayObject["day"]=dayNames[i]
			actualDayObject["date"]=monday+datetime.timedelta(days=i)
			days.append(actualDayObject)
		prevMonday=day+datetime.timedelta(days=-calendar[2]+1-7)
		nextMonday=day+datetime.timedelta(days=-calendar[2]+1+7)
		today=datetime.date.today()
		todayCalendat=today.isocalendar()
		actualMonday=today+datetime.timedelta(days=-todayCalendat[2]+1)
		template_values = {
			'days':days,
			'next':nextMonday,
			'actual':actualMonday,
			'menu':menu
		}
		template_values['prev'] = prevMonday
		# A single dish with editable ingredient list
		template = jinja_environment.get_template('templates/chefReviewOrders.html')
		self.printPage(str(day), template.render(template_values), True)
		
#An accumulated overview of every ordered item
class ChefReviewToMakePage(BaseHandler):
	def get(self):
		day=datetime.date.today()
		requestDay=self.request.get('day')
		if ((requestDay != None) and (requestDay != "")):
			parts=requestDay.rsplit("-")
			day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
		#Determine the week
		calendar=day.isocalendar()
		#Organize into days
		menu=[] #Contains menu items
		dayNames=["Hetfo","Kedd","Szerda","Csutortok","Pentek","Szombat","Vasarnap"]
		dishCategories=DishCategory.gql("ORDER BY index")
		monday=day+datetime.timedelta(days=-calendar[2]+1)
		sunday=day+datetime.timedelta(days=-calendar[2]+7)
		originalItems=MenuItem.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
		menuItems=sorted(originalItems, key=lambda item:item.dish.title)
		for category in dishCategories:
			actualCategoryObject={}
			actualCategoryObject['category']=category
			items=[]
			dishes={}
			itemsInRows=0
			for i in range(0,5):
				actualDay=monday+datetime.timedelta(days=i)
				actualDayObject={}
				actualDayObject["day"]=dayNames[i]
				actualDayObject["date"]=actualDay
				#Filter menu items
				actualMenuItems=[]
				actualDishes={}
				for menuItem in menuItems:
					if (menuItem.dish.category.key()==category.key()) and (menuItem.day==actualDay):
						menuItem.orderedQuantity = 0
						for order in menuItem.occurrences:
							menuItem.orderedQuantity = menuItem.orderedQuantity + order.itemCount
						if menuItem.containingMenuItem != None:
							for order in menuItem.containingMenuItem.occurrences:
								menuItem.orderedQuantity = menuItem.orderedQuantity + order.itemCount
						if menuItem.orderedQuantity > 0:
							itemsInRows = itemsInRows + 1
							actualMenuItems.append(menuItem)
				actualDayObject["menuItems"]=actualMenuItems
				items.append(actualDayObject)
			actualCategoryObject["days"]=items
			if (itemsInRows > 0):
				menu.append(actualCategoryObject)
		days=[]
		for i in range(0,5):
			actualDayObject={}
			actualDayObject["day"]=dayNames[i]
			actualDayObject["date"]=monday+datetime.timedelta(days=i)
			days.append(actualDayObject)
		prevMonday=day+datetime.timedelta(days=-calendar[2]+1-7)
		nextMonday=day+datetime.timedelta(days=-calendar[2]+1+7)
		today=datetime.date.today()
		todayCalendat=today.isocalendar()
		actualMonday=today+datetime.timedelta(days=-todayCalendat[2]+1)
		template_values = {
			'days':days,
			'next':nextMonday,
			'actual':actualMonday,
			'menu':menu
		}
		template_values['prev'] = prevMonday
		# A single dish with editable ingredient list
		template = jinja_environment.get_template('templates/chefReviewOrders.html')
		self.printPage(str(day), template.render(template_values), True)