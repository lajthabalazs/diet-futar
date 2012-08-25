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
		days=[]
		dayNames=["Hetfo","Kedd","Szerda","Csutortok","Pentek","Szombat","Vasarnap"]
		for i in range(1, 6):
			actualDay=day+datetime.timedelta(days=-calendar[2]+i)
			actualDayItems=MenuItem.gql("WHERE day=DATE(:1,:2,:3)", actualDay.year, actualDay.month, actualDay.day)
			actualDayObject={}
			actualDayObject["day"]=dayNames[i-1]
			actualDayObject["date"]=actualDay
			actualDayObject["menuItems"]=actualDayItems
			days.append(actualDayObject)
		# A single dish with editable ingredient list
		prevMonday=day+datetime.timedelta(days=-calendar[2]+1-7)
		nextMonday=day+datetime.timedelta(days=-calendar[2]+1+7)
		today=datetime.date.today()
		todayCalendat=today.isocalendar()
		actualMonday=today+datetime.timedelta(days=-todayCalendat[2]+1)
		dishCategories=DishCategory.gql("ORDER BY index")
		templateCategories=[]
		for dishCategory in dishCategories:
			dishes=sorted(dishCategory.dishes, key=lambda dish: dish.title)
			templateCategory={
				'category':dishCategory,
				'dishes':dishes
			}
			templateCategories.append(templateCategory)
		template_values = {
			'days':days,
			'prev':prevMonday,
			'next':nextMonday,
			'actual':actualMonday,
			'availableDishes':templateCategories
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
			
			
			
			
			
			
			
			
			
			
			
			
			