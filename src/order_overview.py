#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler, getBaseDate, getMonday, getZipBasedDeliveryCost
import datetime
from model import ROLE_ADMIN, Role, ROLE_DELIVERY_GUY, UserWeekOrder,\
	User
from order import dayNames, getOrderAddress, getOrderedItemsFromWeekData
from user_management import isUserCook, isUserDelivery, LOGIN_NEXT_PAGE_KEY
from cache_dish_category import getDishCategories
from cache_menu_item import getDaysMenuItems
from cache_composit import getDaysComposits
from orderHelper import getOrdersForWeek

ACTUAL_ORDER="actualOrder"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

#An accumulated overview of every ordered item
class ChefReviewOrdersPage(BaseHandler):
	URL = '/chefReviewOrders'
	def get(self):
		if not isUserCook(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
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
					orderedPrice[i] = orderedPrice[i] + composit['price'] * int(orders[itemKeyStr])
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
	URL = '/deliveryReviewOrders'
	def get(self):
		if not isUserDelivery(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		day=getBaseDate(self)
		calendar=day.isocalendar()
		#Organize into days
		dayTotal = 0
		dayCount = 0
		dayQuantity = 0
		dayObject={}
		dayObject["day"]=dayNames[calendar[2]-1]
		dayObject["date"]=day
		prevDay=day+datetime.timedelta(days=-1)
		nextDay=day+datetime.timedelta(days=1)
		today=datetime.date.today()
		monday = getMonday(day)
		weeks = UserWeekOrder.all().filter('monday = ', monday)
		deliveries = []
		for week in weeks:
			items = getOrderedItemsFromWeekData([week], day)
			dailyUserTotal = 0
			if len(items) > 0:
				for item in items:
					dayCount = dayCount + 1
					dayQuantity = dayQuantity + item['orderedQuantity']
					dayTotal = dayTotal + item['orderedQuantity'] * item['price']
					dailyUserTotal = dailyUserTotal + item['orderedQuantity'] * item['price']
				orderAddress = getOrderAddress(week, day)
				if orderAddress == None:
					orderAddress = week.user.addresses.get(0)
				orderAddress.orderedItems = items
				orderAddress.week = week
				orderAddress.dailyUserTotal = dailyUserTotal
				deliveries.append(orderAddress)
		sortedDeliveries = sorted(deliveries, key=lambda item:item.zipNumCode)
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
			'deliverers':deliverers,
			'dayTotal': dayTotal,
			'dayCount' : dayCount,
			'dayQuantity' : dayQuantity
		}
		template_values['prev'] = prevDay
		template = jinja_environment.get_template('templates/deliveryReviewOrders.html')
		self.printPage(str(day), template.render(template_values), False, False)

class DeliveryPage(BaseHandler):
	URL = '/deliverable'
	def get(self):
		if not isUserDelivery(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return	
		userKey = self.request.get("userKey")
		mondayString = self.request.get("monday")
		monday = datetime.datetime.strptime(mondayString, "%Y-%m-%d").date()
		user = User.get(userKey)
		if user == None:
			print "No user!"
			return
		weeks = user.weeks.filter("monday = ", monday)
		referenceWeek = weeks.get()
		days = []
		weekOrderTotal = 0
		weekDeliveryTotal = 0
		for i in range(0,5):
			day = {}
			actualDay = monday + datetime.timedelta(days=i)
			daysOrderItems = getOrderedItemsFromWeekData(weeks, actualDay)
			address=getOrderAddress(referenceWeek, actualDay)
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
				deliveryCost = 0
				if address != None:
					deliveryCost = getZipBasedDeliveryCost(address.zipNumCode, orderedPrice)
				day["deliveryCost"] = 0
				weekDeliveryTotal = weekDeliveryTotal + deliveryCost
			days.append(day)
		template_values = {
			'user':user,
			'days':days,
			'week':referenceWeek,
			'deliveryTotal':weekDeliveryTotal,
			'orderTotal':weekOrderTotal,
			'total':weekOrderTotal + weekDeliveryTotal,
		}
		prevMonday = monday + datetime.timedelta(days= -7)
		template_values['prev'] = prevMonday
		nextMonday = monday + datetime.timedelta(days= 7)
		template_values['next'] = nextMonday
		template = jinja_environment.get_template('templates/delivery.html')
		self.printPage(str(day), template.render(template_values), False, False)
