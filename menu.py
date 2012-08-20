#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler, PAGE_TITLE
import datetime
from model import Dish, MenuItem
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
		for i in range(1, 8):
			actualDay=day+datetime.timedelta(days=-calendar[2]+i)
			actualDayItems=MenuItem.gql("WHERE day=DATE(:1,:2,:3)", actualDay.year, actualDay.month, actualDay.day)
			actualDayObject={}
			actualDayObject["day"]=dayNames[i-1]
			actualDayObject["date"]=actualDay
			actualDayObject["menuItems"]=actualDayItems
			days.append(actualDayObject)
		# A single dish with editable ingredient list
		dishes=Dish.gql("ORDER BY title")
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
			'availableDishes':dishes
		}
		template = jinja_environment.get_template('templates/menuEdit.html')
		self.printPage(PAGE_TITLE + " - " + str(day), template.render(template_values), False, False)
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
			
			
			
			
			
			
			
			
			
			
			
			
			