#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler, getBaseDate
import datetime
from model import MenuItem, DishCategory, Composit, UserOrderAddress, User,\
	ROLE_ADMIN, Role, ROLE_DELIVERY_GUY
from order import dayNames
from user_management import isUserAdmin, isUserCook, isUserDelivery
#from user_management import getUserBox

ACTUAL_ORDER="actualOrder"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

#An accumulated overview of every ordered item
class ChefReviewOrdersPage(BaseHandler):
	def get(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		day=getBaseDate(self)
		#Determine the week
		calendar=day.isocalendar()
		#Organize into days
		menu=[] #Contains menu items
		dishCategories=DishCategory.gql("ORDER BY index")
		monday=day+datetime.timedelta(days=-calendar[2]+1)
		sunday=day+datetime.timedelta(days=-calendar[2]+7)
		originalItems=MenuItem.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
		composits=Composit.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
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
					if menuItem.dish.category.key()==category.key() and menuItem.day==actualDay and menuItem.containingMenuItem == None:
						menuItem.orderedQuantity = 0
						for order in menuItem.occurrences:
							menuItem.orderedQuantity = menuItem.orderedQuantity + order.itemCount
						if menuItem.orderedQuantity > 0:
							itemsInRows = itemsInRows + 1
							actualMenuItems.append(menuItem)
				actualComposits=[]
				for composit in composits:
					if composit.category.key()==category.key() and composit.day==actualDay:
						composit.orderedQuantity = 0
						for order in composit.occurrences:
							composit.orderedQuantity = composit.orderedQuantity + order.itemCount
						if composit.orderedQuantity > 0:
							itemsInRows = itemsInRows + 1
							actualComposits.append(composit)
				actualDayObject["menuItems"]=actualMenuItems
				actualDayObject["composits"]=actualComposits
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
		self.printPage(str(day), template.render(template_values), False, False)
		
#An accumulated overview of every ordered item
class ChefReviewToMakePage(BaseHandler):
	def get(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		day=getBaseDate(self)
		#Determine the week
		calendar=day.isocalendar()
		#Organize into days
		dishCategories=DishCategory.gql("ORDER BY index")
		monday=day+datetime.timedelta(days=-calendar[2]+1)
		sunday=day+datetime.timedelta(days=-calendar[2]+7)
		menuItems=MenuItem.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
		composits=Composit.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
		# Build matrix, categories and days in categories
		menuData={} #Contains menu items
		for category in dishCategories:
			# Skip menu categories
			if category.isMenu:
				continue
			actualCategoryObject={}
			actualCategoryObject['category']=category
			actualCategoryObject["days"] = []
			for i in range(0,5):
				actualDay=monday+datetime.timedelta(days=i)
				actualDayObject={}
				actualDayObject["day"]=dayNames[i]
				actualDayObject["date"]=actualDay
				actualDayObject["dishes"]={}
				actualCategoryObject["days"].append(actualDayObject)
			menuData[category.key()] = actualCategoryObject
		# Goes through orders
		for menuItem in menuItems:
			for orderItem in menuItem.occurrences:
			# Extract order items
				itemCount = orderItem.itemCount
				# Check if its a menu item, or a composit
				if orderItem.orderedItem != None and (itemCount != None):
					# Ordered menu item, extract dishes
					orderedItem = orderItem.orderedItem
					dayIndex = (orderedItem.day - monday).days
					# Increment for main item
					slot=menuData[orderedItem.dish.category.key()]["days"][dayIndex]["dishes"]
					itemKey = orderedItem.dish.key()
					itemQuantity = 0
					if slot.has_key(itemKey):
						itemQuantity = int(slot.get(itemKey)["itemQuantity"])
					else:
						slot[itemKey] = {} 
						slot[itemKey]["dish"]=orderedItem.dish
					slot[itemKey]["itemQuantity"] = itemQuantity + itemCount
					# Increment for sub items
					for subItem in orderedItem.components:
						slot=menuData[subItem.dish.category.key()]["days"][dayIndex]["dishes"]
						itemKey = subItem.dish.key()
						itemQuantity = 0
						if slot.has_key(itemKey):
							itemQuantity = int(slot.get(itemKey)["itemQuantity"])
						else:
							slot[itemKey] = {} 
							slot[itemKey]["dish"]=subItem.dish
						slot[itemKey]["itemQuantity"] = itemQuantity + itemCount
		for composit in composits:
			for orderItem in composit.occurrences:
				itemCount =orderItem.itemCount
				if orderItem.orderedComposit != None and (itemCount != None):
					# Ordered menu composit, extract dishes
					orderedComposit = orderItem.orderedComposit
					dayIndex = (orderedComposit.day - monday).days
					for linker in orderedComposit.components:
						orderedItem = linker.menuItem
						# Increment for main item
						slot=menuData[orderedItem.dish.category.key()]["days"][dayIndex]["dishes"]
						itemKey = orderedItem.dish.key()
						itemQuantity = 0
						if slot.has_key(itemKey):
							itemQuantity = int(slot.get(itemKey)["itemQuantity"])
						else:
							slot[itemKey] = {} 
							slot[itemKey]["dish"]=orderedItem.dish
						slot[itemKey]["itemQuantity"] = itemQuantity + itemCount
						# Increment for sub items
						for subItem in orderedItem.components:
							slot=menuData[subItem.dish.category.key()]["days"][dayIndex]["dishes"]
							itemKey = subItem.dish.key()
							itemQuantity = 0
							if slot.has_key(itemKey):
								itemQuantity = int(slot.get(itemKey)["itemQuantity"])
							else:
								slot[itemKey] = {} 
								slot[itemKey]["dish"]=subItem.dish
							slot[itemKey]["itemQuantity"] = itemQuantity + itemCount
		# Shape data
		menu=[]
		for category in dishCategories:
			# Skip menu categories
			if category.isMenu:
				continue
			menu.append(menuData[category.key()])
		
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
		template = jinja_environment.get_template('templates/chefReviewDishes.html')
		self.printPage(str(day), template.render(template_values), False, False)
		
		
#An accumulated overview of every ordered item
class DeliveryReviewOrdersPage(BaseHandler):
	def get(self):
		if not isUserDelivery(self):
			self.redirect("/")
			return
		day=getBaseDate(self)
		prevDay=day+datetime.timedelta(days=-1)
		nextDay=day+datetime.timedelta(days=1)
		today=datetime.date.today()
		orders=UserOrderAddress.gql("WHERE day=DATE(:1,:2,:3)", day.year, day.month, day.day)
		sortedDeliveries=sorted(orders, key=lambda item:item.address.zipCode)
		admins=Role.all().filter("name = ", ROLE_ADMIN)[0].users
		delivereryGuys=Role.all().filter("name = ", ROLE_DELIVERY_GUY)[0].users
		deliverers=[]
		for admin in admins:
			deliverers.append(admin)
		for guy in delivereryGuys:
			deliverers.append(guy)
		template_values = {
			'next':nextDay,
			'actual':today,
			'orders':sortedDeliveries,
			'day':day,
			'deliverers':deliverers
		}
		template_values['prev'] = prevDay
		# A single dish with editable ingredient list
		template = jinja_environment.get_template('templates/deliveryReviewOrders.html')
		self.printPage(str(day), template.render(template_values), False, False)
	def post(self):
		if not isUserDelivery(self):
			self.redirect("/")
			return
		# Save row
		deliveryKey = self.request.get("odrerKey")
		if deliveryKey!=None and deliveryKey != "":
			delivery = UserOrderAddress.get(deliveryKey)
			if delivery!=None:
				delivery.delivered = self.request.get("delivered")=="on"
				delivererKey=self.request.get("deliverer")
				if delivererKey!=None and delivererKey != "":
					delivery.deliverer=User.get(delivererKey)
				else:
					delivery.deliverer=None
				delivery.put()
		self.redirect('/deliveryReviewOrders')
		
class DeliveryPage(BaseHandler):
	def get(self):
		if not isUserDelivery(self):
			self.redirect("/")
			return	
		orderAddressKey=self.request.get("orderAddressKey")
		orderAddress=UserOrderAddress.get(orderAddressKey)
		day=orderAddress.day
		filteredSet = orderAddress.user.orderedItems.filter("day = ", day)
		# Aggregate filtered set
		menuItemIndexes={}
		menuItemOrders=[]
		for orderedItem in filteredSet:
			if orderedItem.orderedComposit == None:
				menuItem=orderedItem.orderedItem
				actualOrder=0
				if menuItemIndexes.has_key(menuItem.key()):
					itemIndex=menuItemIndexes.get(menuItem.key())
					actualOrder=menuItemOrders[itemIndex].itemCount
					menuItemOrders[itemIndex].itemCount=actualOrder+orderedItem.itemCount
				else:
					menuItem.itemCount=orderedItem.itemCount
					menuItemIndexes[menuItem.key()]=len(menuItemOrders)
					menuItemOrders.append(menuItem)
			else:
				actualOrder=0
				for compositItem in orderedItem.orderedComposit.components:
					menuItem = compositItem.menuItem;
					actualOrder=0
					if menuItemIndexes.has_key(menuItem.key()):
						itemIndex=menuItemIndexes.get(menuItem.key())
						actualOrder=menuItemOrders[itemIndex].itemCount
						menuItemOrders[itemIndex].itemCount=actualOrder+orderedItem.itemCount
					else:
						menuItem.itemCount=orderedItem.itemCount
						menuItemIndexes[menuItem.key()]=len(menuItemOrders)
						menuItemOrders.append(menuItem)
		template_values = {
			'order':orderAddress,
			'items':menuItemOrders
		}
		# A single dish with editable ingredient list
		template = jinja_environment.get_template('templates/delivery.html')
		self.printPage(str(day), template.render(template_values), False, False)
