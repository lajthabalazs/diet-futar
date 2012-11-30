#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler, getBaseDate, getMonday
import datetime
from model import MenuItem, DishCategory, Composit, ROLE_ADMIN, Role, ROLE_DELIVERY_GUY, UserWeekOrder,\
	Address
from order import dayNames, getOrderAddress, getOrderedItemsFromWeekData
from user_management import isUserCook, isUserDelivery
from cache_dish_category import getDishCategories
from cache_menu_item import getDaysMenuItems
from cache_composit import getDaysComposits

ACTUAL_ORDER="actualOrder"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

#An accumulated overview of every ordered item
class ChefReviewOrdersPage(BaseHandler):
	def get(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		day=getBaseDate(self)
		#Organize into days
		menu=[] #Contains menu items
		dishCategories=getDishCategories()
		monday = getMonday(day)
		for category in dishCategories:
			actualCategoryObject={}
			actualCategoryObject['category']=category
			categoryKey=category['key']
			items=[]
			itemsInRows=0
			for i in range(0,5):
				actualDay=monday+datetime.timedelta(days=i)
				actualDayObject={}
				actualDayObject["day"]=dayNames[i]
				actualDayObject["date"]=actualDay
				menuItems = getDaysMenuItems(actualDay, categoryKey)
				composits = getDaysComposits(actualDay, categoryKey)
				#Filter menu items
				actualMenuItems=[]
				actualComposits=[]
				for menuItem in menuItems:
					menuItem['orderedQuantity']= 0
					for order in menuItem.occurrences:
						menuItem.orderedQuantity = menuItem.orderedQuantity + order.itemCount
					if menuItem.orderedQuantity > 0:
						itemsInRows = itemsInRows + 1
						actualMenuItems.append(menuItem)
				for composit in composits:
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
		prevMonday=monday + datetime.timedelta(days = -7)
		nextMonday=monday + datetime.timedelta(days = 7)
		today=datetime.date.today()
		actualMonday= getMonday(today)
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
				
class DeliveryReviewOrdersPage(BaseHandler):
	def get(self):
		if not isUserDelivery(self):
			self.redirect("/")
			return
		day=getBaseDate(self)
		calendar=day.isocalendar()
		#Organize into days
		dayObject={}
		dayObject["day"]=dayNames[calendar[2]-1]
		dayObject["date"]=day
		prevDay=day+datetime.timedelta(days=-1)
		nextDay=day+datetime.timedelta(days=1)
		today=datetime.date.today()
		monday = getMonday(day)
		weeks = UserWeekOrder.gql("WHERE monday=DATE(:1,:2,:3)", monday.year, monday.month, monday.day)
		deliveries = []
		for week in weeks:
			orderAddress = getOrderAddress(week, day)
			if orderAddress == None:
				orderAddress = Address()
				orderAddress.zipCode = "0000"
				orderAddress.street = "Ismeretlen"
				orderAddress.streetNumber = "x."
			items = getOrderedItemsFromWeekData(week, day)
			orderAddress.orderedItems = items
			orderAddress.week = week
			deliveries.append(orderAddress)
		sortedDeliveries = sorted(deliveries, key=lambda item:item.zipCode)
		admins=Role.all().filter("name = ", ROLE_ADMIN)[0].users
		delivereryGuys=Role.all().filter("name = ", ROLE_DELIVERY_GUY)[0].users
		deliverers=[]
		deliverers.extend(admins)
		deliverers.extend(delivereryGuys)
		template_values = {
			'next':nextDay,
			'actual':today,
			'orders':sortedDeliveries,
			'day':dayObject,
			'deliverers':deliverers
		}
		template_values['prev'] = prevDay
		template = jinja_environment.get_template('templates/deliveryReviewOrders.html')
		self.printPage(str(day), template.render(template_values), False, False)

class DeliveryPage(BaseHandler):
	def get(self):
		if not isUserDelivery(self):
			self.redirect("/")
			return	
		weekKey=self.request.get("weekKey")
		week=UserWeekOrder.get(weekKey)
		days = []
		for i in range(0,5):
			day = {}
			actualDay = week.monday + datetime.timedelta(days=i)
			day['orderedItems'] = getOrderedItemsFromWeekData(week, actualDay)
			day['address'] = getOrderAddress(week, actualDay)
			day['day']=dayNames[i]
			day['date'] = actualDay
			days.append(day)
		template_values = {
			'days':days,
			'week':week
		}
		template = jinja_environment.get_template('templates/delivery.html')
		self.printPage(str(day), template.render(template_values), False, False)
