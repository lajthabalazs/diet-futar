#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
import datetime
from model import MenuItem, DishCategory
from user_management import isUserAdmin
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
				for menuItem in menuItems:
					if (menuItem.dish.category.key()==category.key()):
						if (menuItem.day==actualDay):
							actualMenuItems.append(menuItem)
				actualDayObject["menuItems"]=actualMenuItems
				items.append(actualDayObject)
			actualCategoryObject["days"]=items
		days=[]
		for i in range(0,5):
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
		template_values = {
			'days':days,
			'prev':prevMonday,
			'next':nextMonday,
			'actual':actualMonday,
			'menu':menu
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
				menuItem.put()
			self.redirect("/menuEdit?day="+str(day))
			
class MenuDeleteDishPage(BaseHandler):
	def post(self):
		if(not isUserAdmin):
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
					menuItem.delete()
			self.redirect("/menuEdit?day="+str(day))
			
			
			
			
			
			
			
			
			
			
			
			
			