#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
import datetime
from model import MenuItem, DishCategory, UserOrder, UserOrderItem, User
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
from user_management import USER_KEY
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
		#Fetch user's previous orders. User orders is an object associating menu item keys with quantities
		userOrders={}
		userKey = self.session.get(USER_KEY,None)
		if (userKey != None):
			user = User.get(userKey)
			for userOrder in user.userOrders:
				for orderedItem in userOrder.items:
					itemQuantity = 0
					try: 
						menuItemKey = orderedItem.orderedItem.key()
						if (userOrders.has_key(menuItemKey)):
							itemQuantity = int(userOrders[menuItemKey])
						if (orderedItem.itemCount != None):
							userOrders[menuItemKey] = itemQuantity + orderedItem.itemCount
					except ReferencePropertyResolveError:
						itemQuantity=0
		#Determine the week
		calendar=day.isocalendar()
		#Organize into days
		menu=[] #Contains menu items
		dayNames=["Hetfo","Kedd","Szerda","Csutortok","Pentek","Szombat","Vasarnap"]
		actualOrder=self.session.get(ACTUAL_ORDER,[])
		dishCategories=DishCategory.gql("ORDER BY index")
		monday=day+datetime.timedelta(days=-calendar[2]+1)
		sunday=day+datetime.timedelta(days=-calendar[2]+7)
		originalItems=MenuItem.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
		menuItems=sorted(originalItems, key=lambda item:item.dish.title)
		orderedPrice = [0,0,0,0,0]
		basketPrice = [0,0,0,0,0]
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
					try:
						if (menuItem.dish.category.key()==category.key()) and (menuItem.day==actualDay) and (menuItem.containingMenuItem == None):
							if (actualOrder!=None) and (str(menuItem.key()) in actualOrder):
								menuItem.inCurrentOrder=actualOrder[str(menuItem.key())]
								try:
									basketPrice[i] = basketPrice[i] + menuItem.price * int(actualOrder[str(menuItem.key())])
								except:
									pass
							else:
								menuItem.inCurrentOrder=0
							try:
								menuItem.orderedQuantity = userOrders[menuItem.key()]
								try:
									orderedPrice[i] = orderedPrice[i] +  menuItem.price * int(userOrders[menuItem.key()])
								except:
									pass
							except KeyError:
								menuItem.orderedQuantity = 0
							actualMenuItems.append(menuItem)
							itemsInRows=itemsInRows+1
					except ReferencePropertyResolveError:
						continue
				actualDayObject["menuItems"]=actualMenuItems
				items.append(actualDayObject)
			actualCategoryObject["days"]=items
			if (itemsInRows > 0):
				menu.append(actualCategoryObject)
		days=[]
		for i in range(0,5):
			actualDayObject={}
			actualDayObject["orderedPrice"] = orderedPrice[i]
			actualDayObject["basketPrice"] = basketPrice[i]
			actualDayObject["totalPrice"] = orderedPrice[i] + basketPrice[i]
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
			'next':nextMonday,
			'actual':actualMonday,
			'menu':menu
		}
		if (prevMonday == actualMonday) or (prevMonday > actualMonday):
			template_values['prev'] = prevMonday
		# A single dish with editable ingredient list
		template = jinja_environment.get_template('templates/menuOrder.html')
		self.printPage(str(day), template.render(template_values), True)
	def post(self):
		actualOrder = self.session.get(ACTUAL_ORDER,{})
		day=datetime.date.today()
		requestDay=self.request.get('formDay')
		if ((requestDay != None) and (requestDay != "")):
			parts=requestDay.rsplit("-")
			day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
		# Add order
		for field in self.request.arguments():
			if (field[:3]=="MIC"):
				actualOrder[field[3:]]=self.request.get(field)
		self.session[ACTUAL_ORDER]=actualOrder
		self.redirect("/order?day="+str(day))

class ClearOrderPage(BaseHandler):
	def get(self):
		day=datetime.date.today()
		requestDay=self.request.get('formDay')
		if ((requestDay != None) and (requestDay != "")):
			parts=requestDay.rsplit("-")
			day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
		self.session[ACTUAL_ORDER]={}
		self.redirect("/order?day="+str(day))
	def post(self):
		day=datetime.date.today()
		requestDay=self.request.get('formDay')
		if ((requestDay != None) and (requestDay != "")):
			parts=requestDay.rsplit("-")
			day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
		self.session[ACTUAL_ORDER]={}
		self.redirect("/order?day="+str(day))
		

class ReviewPendingOrderPage(BaseHandler):
	def get(self):
		actualOrder=self.session.get(ACTUAL_ORDER,{})
		if (len(actualOrder) > 0):
			orderedMenuItemKeys=[]
			for key in actualOrder.keys():
				orderedMenuItemKeys.append(key)
			mayBeNullOrderedItems=db.get(orderedMenuItemKeys)
			orderedItems=[]
			for item in mayBeNullOrderedItems:
				if item != None:
					orderedItems.append(item)
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
			actualOrder=self.session.get(ACTUAL_ORDER,[])
			dishCategories=DishCategory.gql("ORDER BY index")
			monday=day+datetime.timedelta(days=-calendar[2]+1)
			sunday=day+datetime.timedelta(days=-calendar[2]+7)
			dayTotal = [0,0,0,0,0]
			menuItems=sorted(orderedItems, key=lambda item:item.dish.title)
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
						try:
							menuItem.dish.category
						except ReferencePropertyResolveError:
							continue
						if (menuItem.dish.category.key()==category.key()) and (menuItem.day==actualDay):
							try:
								if (actualOrder!=None) and (str(menuItem.key()) in actualOrder) and int(actualOrder[str(menuItem.key())]) != 0:
									menuItem.inCurrentOrder=actualOrder[str(menuItem.key())]
									try:
										menuItem.basketprice = int(menuItem.inCurrentOrder) * menuItem.price
									except TypeError:
										menuItem.basketprice = 0
									dayTotal[i] = dayTotal[i] + menuItem.basketprice
									actualMenuItems.append(menuItem)
									itemsInRows=itemsInRows+1
								else:
									menuItem.inCurrentOrder=False
							except ValueError:
								menuItem.inCurrentOrder=False
					actualDayObject["menuItems"]=actualMenuItems
					items.append(actualDayObject)
				actualCategoryObject["days"]=items
				if (itemsInRows > 0):
					menu.append(actualCategoryObject)
			days=[]
			# Adds header information
			for i in range(0,5):
				actualDayObject={}
				actualDayObject["day"] = dayNames[i]
				actualDayObject["date"] = monday+datetime.timedelta(days=i)
				actualDayObject["total"] = dayTotal[i]
				days.append(actualDayObject)
			# A single dish with editable ingredient list
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
			if (prevMonday == actualMonday) or (prevMonday > actualMonday):
				template_values['prev'] = prevMonday
			# A single dish with editable ingredient list
			template = jinja_environment.get_template('templates/reviewPendingOrder.html')
			self.printPage(str(day), template.render(template_values), True)
		else:
			template = jinja_environment.get_template('templates/noOrder.html')
			self.printPage(None, template.render(), True)
	def post(self):
		actualOrder = self.session.get(ACTUAL_ORDER,{})
		day=datetime.date.today()
		requestDay=self.request.get('formDay')
		if ((requestDay != None) and (requestDay != "")):
			parts=requestDay.rsplit("-")
			day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
		# Add order
		for field in self.request.arguments():
			if (field[:3]=="MIC"):
				actualOrder[field[3:]]=self.request.get(field)
		self.session[ACTUAL_ORDER]=actualOrder
		self.redirect("/pendingOrder?day="+str(day))

class ReviewOrderedMenuPage(BaseHandler):
	def get(self):
		day=datetime.date.today()
		requestDay=self.request.get('day')
		if ((requestDay != None) and (requestDay != "")):
			parts=requestDay.rsplit("-")
			day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
		#Fetch user's previous orders. User orders is an object associating menu item keys with quantities
		userOrders={}
		userKey = self.session.get(USER_KEY,None)
		if (userKey != None):
			user = User.get(userKey)
			for userOrder in user.userOrders:
				for orderedItem in userOrder.items:
					itemQuantity = 0
					try: 
						menuItemKey = orderedItem.orderedItem.key()
						if (userOrders.has_key(menuItemKey)):
							itemQuantity = int(userOrders[menuItemKey])
						if (orderedItem.itemCount != None):
							userOrders[menuItemKey] = itemQuantity + orderedItem.itemCount
					except ReferencePropertyResolveError:
						itemQuantity=0
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
		orderedPrice = [0,0,0,0,0]
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
					try:
						if (menuItem.dish.category.key()==category.key()) and (menuItem.day==actualDay) and (menuItem.containingMenuItem == None):
							try:
								menuItem.orderedQuantity = int(userOrders[menuItem.key()])
								orderedPrice[i] = orderedPrice[i] +  menuItem.price * int(userOrders[menuItem.key()])
								itemsInRows=itemsInRows+1
							except KeyError, ValueError:
								menuItem.orderedQuantity = 0
							if menuItem.orderedQuantity > 0:
								actualMenuItems.append(menuItem)
					except ReferencePropertyResolveError:
						continue
				actualDayObject["menuItems"]=actualMenuItems
				items.append(actualDayObject)
			actualCategoryObject["days"]=items
			if (itemsInRows > 0):
				menu.append(actualCategoryObject)
		days=[]
		for i in range(0,5):
			actualDayObject={}
			actualDayObject["orderedPrice"] = orderedPrice[i]
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
			'next':nextMonday,
			'actual':actualMonday,
			'menu':menu
		}
		if (prevMonday == actualMonday) or (prevMonday > actualMonday):
			template_values['prev'] = prevMonday
		# A single dish with editable ingredient list
		template = jinja_environment.get_template('templates/reviewOrderedMenu.html')
		self.printPage(str(day), template.render(template_values), True)

class ConfirmOrder(BaseHandler):
	def get(self):
		#One step ordering - this is a trial
		actualOrder = self.session.get(ACTUAL_ORDER,{})
		orderDate=datetime.datetime.now()
		#Save order
		if (len(actualOrder) > 0):
			userOrder = UserOrder()
			userOrder.canceled = False
			userOrder.orderDate = orderDate
			userOrder.price = 0
			userKey = self.session.get(USER_KEY,None)
			if (userKey != None):
				userOrder.user = User.get(userKey)
			userOrder.put()
			for orderKey in actualOrder.keys():
				try:
					if (int(actualOrder[orderKey]) != 0):
						orderItem = UserOrderItem()
						orderItem.userOrder = userOrder
						orderItem.orderedItem = MenuItem.get(orderKey)
						orderItem.itemCount = int(actualOrder[orderKey])
						try:
							orderItem.price = orderItem.orderedItem.price * int(actualOrder[orderKey])
						except TypeError:
							orderItem.price = 0
						userOrder.price = userOrder.price + orderItem.price
						orderItem.put()
				except ValueError, ReferencePropertyResolveError:
					continue
			userOrder.put()
			self.session[ACTUAL_ORDER]={}
			self.redirect("/order")
		else:
			print "Nothing to confirm"

class PreviousOrders(BaseHandler):
	def get(self):
		userKey = self.session.get(USER_KEY,None)
		if (userKey != None):
			user = User.get(userKey)
			template_values = {
				'userOrders':user.userOrders
			}
			template = jinja_environment.get_template('templates/previousOrders.html')
			self.printPage('Rendelesek', template.render(template_values), True)
			

class PreviousOrder(BaseHandler):
	def get(self):
		orderKey = self.request.get("orderKey")
		userOrder = UserOrder.get(orderKey)
		if (userOrder != None):
			template_values = {
				'userOrder':userOrder
			}
			template = jinja_environment.get_template('templates/previousOrder.html')
			self.printPage('Rendeles', template.render(template_values), True)



















