#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler, getBaseDate, getMonday, getDeliveryCost
import datetime
from model import ROLE_ADMIN, Role, ROLE_DELIVERY_GUY, UserWeekOrder, Address
from order import dayNames, getOrderAddress, getOrderedItemsFromWeekData
from user_management import isUserCook, isUserDelivery
from cache_dish_category import getDishCategories
from cache_menu_item import getDaysMenuItems
from cache_composit import getDaysComposits

ACTUAL_ORDER="actualOrder"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def getOrdersForWeek(monday):
	orders={}
	weeks = UserWeekOrder.all().filter("monday = ", monday)
	for week in weeks:
		for orderedComposit in week.orderedComposits:
			parts = orderedComposit.split(" ")
			orderedQuantity = int(parts[0])
			orderedItemKey = parts[1]
			oldValue = 0
			try:
				oldValue = int(orders[orderedItemKey])
			except:
				pass
			orders[orderedItemKey] = orderedQuantity + oldValue
		for orderedMenuItem in week.orderedMenuItems:
			parts = orderedMenuItem.split(" ")
			orderedQuantity = int(parts[0])
			orderedItemKey = parts[1]
			oldValue = 0
			try:
				oldValue = int(orders[orderedItemKey])
			except:
				pass
			orders[orderedItemKey] = orderedQuantity + oldValue
	return orders

#An accumulated overview of every ordered item
class ChefReviewOrdersPage(BaseHandler):
	def get(self):
		if not isUserCook(self):
			self.redirect("/")
			return
		day=getBaseDate(self)
		
		monday = getMonday(day)
		menu=[] #Contains menu items
		dishCategories=getDishCategories()
		orderedPrice = [0,0,0,0,0]
		orders = getOrdersForWeek(monday)
		for category in dishCategories:
			actualCategoryObject={}
			actualCategoryObject['category']=category
			categoryKey=category['key']
			items=[]
			for i in range(0,5):
				actualDay=monday+datetime.timedelta(days=i)
				actualDayObject={}
				actualDayObject["day"]=dayNames[i]
				actualDayObject["date"]=actualDay
				menuItems = getDaysMenuItems(actualDay, categoryKey)
				composits=getDaysComposits(actualDay, categoryKey)
				#Filter menu items
				actualMenuItems=[]
				actualComposits=[]
				for menuItem in menuItems:
					itemKeyStr=menuItem['key']
					if not orders.has_key(itemKeyStr):
						continue
					menuItem['orderedQuantity'] = orders[itemKeyStr]
					orderedPrice[i] = orderedPrice[i] + menuItem['price'] * int(orders[itemKeyStr])
					actualMenuItems.append(menuItem)
				for composit in composits:
					itemKeyStr=composit['key']
					if not orders.has_key(itemKeyStr):
						continue
					composit['orderedQuantity'] = orders[itemKeyStr]
					orderedPrice[i] = orderedPrice[i] +  composit['price'] * int(orders[itemKeyStr])
					actualComposits.append(composit)
				actualDayObject["menuItems"]=actualMenuItems
				actualDayObject["composits"]=actualComposits
				items.append(actualDayObject)
			actualCategoryObject["days"]=items
			menu.append(actualCategoryObject)
		days=[]
		for i in range(0,5):
			actualDayObject={}
			actualDayObject["orderedPrice"] = orderedPrice[i]
			actualDayObject["day"]=dayNames[i]
			actualDayObject["date"]=monday+datetime.timedelta(days=i)
			days.append(actualDayObject)
		# A single dish with editable ingredient list
		prevMonday=monday + datetime.timedelta(days=-7)
		nextMonday=monday + datetime.timedelta(days=7)
		template_values = {
			'days':days,
			'menu':menu
		}
		template_values['next'] = nextMonday
		template_values['prev'] = prevMonday
		# A single dish with editable ingredient list
		template = jinja_environment.get_template('templates/chefReviewOrders.html')
		self.printPage(str(day), template.render(template_values), True)

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
		weekOrderTotal = 0
		weekDeliveryTotal = 0
		for i in range(0,5):
			day = {}
			actualDay = week.monday + datetime.timedelta(days=i)
			daysOrderItems = getOrderedItemsFromWeekData(week, actualDay)
			address=getOrderAddress(week, actualDay)
			day['orderedItems'] = daysOrderItems
			day['day']=dayNames[i]
			day['date'] = actualDay
			orderedPrice = 0
			for orderedItem in daysOrderItems:
				try:
					orderedPrice = orderedPrice + orderedItem['price'] * orderedItem['orderedQuantity']
				except:
					pass
			weekOrderTotal = weekOrderTotal + orderedPrice
			day["orderedPrice"] = orderedPrice
			if len(daysOrderItems) > 0:
				day['address'] = address
				deliveryCost = getDeliveryCost(address.district, orderedPrice)
				day["deliveryCost"] = deliveryCost
				weekDeliveryTotal = weekDeliveryTotal + deliveryCost
			days.append(day)
		template_values = {
			'days':days,
			'week':week,
			'deliveryTotal':weekDeliveryTotal,
			'orderTotal':weekOrderTotal,
			'total':weekOrderTotal + weekDeliveryTotal,
		}
		template = jinja_environment.get_template('templates/delivery.html')
		self.printPage(str(day), template.render(template_values), False, False)
