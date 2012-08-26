#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
import datetime
from model import Dish, MenuItem
#from user_management import getUserBox

ACTUAL_ORDER="actualOrder"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MenuOrderPage(BaseHandler):
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
		actualOrder=self.session.get(ACTUAL_ORDER,[])
		for i in range(0, 5):
			actualDay=day+datetime.timedelta(days=-calendar[2]+i)
			actualDayItems=MenuItem.gql("WHERE day=DATE(:1,:2,:3)", actualDay.year, actualDay.month, actualDay.day)
			refreshedItems=[]
			#del self.session[ACTUAL_ORDER]
			# Set actual item's order state based on checkboxes
			for actualDayItem in actualDayItems:
				#Check if db has order for menu item and user
				#Check if session contains menu item
				if (actualOrder!=None) and (str(actualDayItem.key()) in actualOrder):
					actualDayItem.inCurrentOrder=True
				else:
					actualDayItem.inCurrentOrder=False
				refreshedItems.append(actualDayItem)
			actualDayObject={}
			actualDayObject["day"]=dayNames[i-1]
			actualDayObject["date"]=actualDay
			actualDayObject["menuItems"]=refreshedItems
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
		template = jinja_environment.get_template('templates/menuOrder.html')
		self.printPage(str(day), template.render(template_values), True)
	def post(self):
		actualOrder = self.session.get(ACTUAL_ORDER,[])
		#Adds a dish to current days menu
		day=datetime.date.today()
		requestDay=self.request.get('formDay')
		if ((requestDay != None) and (requestDay != "")):
			parts=requestDay.rsplit("-")
			day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
		# Remove orders
		for field in self.request.arguments():
			if (field[:3]=="MIH"):
				#If field is a menu item
				menuItemKey=field[3:]
				try:
					actualOrder.remove(menuItemKey)
				except ValueError:
					#do nothing
					menuItemKey=""
		# Add order
		for field in self.request.arguments():
			if (field[:3]=="MIC"):
				#If field is a menu item
				menuItemKey=field[3:]
				if (not (menuItemKey in actualOrder)):
					actualOrder.append(menuItemKey)
		self.session[ACTUAL_ORDER]=actualOrder
		self.redirect("/order?day="+str(day))

class ClearOrderPage(BaseHandler):
	def post(self):
		day=datetime.date.today()
		requestDay=self.request.get('formDay')
		if ((requestDay != None) and (requestDay != "")):
			parts=requestDay.rsplit("-")
			day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
		self.session[ACTUAL_ORDER]=[]
		self.redirect("/order?day="+str(day))
		
class ReviewPendingOrderPage(BaseHandler):
	def get(self):
		actualOrder=self.session.get(ACTUAL_ORDER,[])
		dayIndex={}
		days=[]
		if (len(actualOrder) > 0):
			menuItems=db.get(actualOrder)
			for menuItem in menuItems:
				index=dayIndex.get(menuItem.day,-1)
				day={}
				if (index != -1):
					day=days[index]
				else:
					day['name']="Hetfo"
					day['date']=str(menuItem.day)
					day['menuItems']=[]
					days.append(day)
					dayIndex[menuItem.day]=len(days)-1
				day['menuItems'].append(menuItem)
		template_values = {
			'days':days
		}
		template = jinja_environment.get_template('templates/reviewPendingOrder.html')
		self.printPage("Aktualis rendeles", template.render(template_values), True)





















	