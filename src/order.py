#!/usr/bin/env python
import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler, getOrderBaseDate, getFormDate,\
	getFirstOrderableDate, getDeliveryCost, getDeliveryLimit, getMonday
import datetime
from model import MenuItem, User, UserWeekOrder, Address
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
from user_management import USER_KEY, getUser, isUserLoggedIn
from cache_menu_item import getDaysMenuItems, getMenuItem
from cache_composit import getDaysComposits, getComposit
from google.appengine.api import mail
from cache_dish_category import getDishCategories
#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

ACTUAL_ORDER="actualOrder"
FURTHEST_DAY_DISPLAYED=14
dayNames=["H&#233;tf&#337;","Kedd","Szerda","Cs&#252;t&#246;rt&#246;k","P&#233;ntek","Szombat","Vas&#225;rnap"]

def getOrderedItemsFromWeekData (week, day):
	orderedMenuItems=[]
	orderedComposits=[]
	for menuItemString in week.orderedMenuItems:
		parts = menuItemString.split(" ")
		orderedQuantity = int(parts[0])
		menuItemKey = parts[1]
		menuItem = getMenuItem(menuItemKey)
		if menuItem != None and menuItem['day'] == day:
			menuItem['orderedQuantity'] = orderedQuantity
			menuItem['isMenuItem'] = True
			orderedMenuItems.append(menuItem)
	for compositString in week.orderedComposits:
		parts = compositString.split(" ")
		orderedQuantity = int(parts[0])
		compositKey = parts[1]
		composit = getComposit(compositKey)
		if composit != None and composit['day'] == day:
			composit['orderedQuantity'] = orderedQuantity
			composit['isMenuItem'] = False
			orderedComposits.append(composit)
	orderedItems = []
	orderedItems.extend(orderedComposits)
	orderedItems.extend(orderedMenuItems)
	return orderedItems

def getOrderAddress (week, day):
	if day.weekday() == 0:
		return week.mondayAddress
	elif day.weekday() == 1:
		return week.tuesdayAddress
	elif day.weekday() == 2:
		return week.wednesdayAddress
	elif day.weekday() == 3:
		return week.thursdayAddress
	elif day.weekday() == 4:
		return week.fridayAddress
	elif day.weekday() == 5:
		return week.saturdayAddress
	elif day.weekday() == 6:
		return week.sundayAddress

def getUserOrdersForWeek(user, monday):
	userOrders={}
	weeks = user.weeks.filter("monday = ", monday)
	if (weeks.count() == 1):
		week = weeks.get()
		for orderedComposit in week.orderedComposits:
			parts = orderedComposit.split(" ")
			orderedQuantity = int(parts[0])
			orderedItemKey = parts[1]
			userOrders[orderedItemKey] = orderedQuantity
		for orderedMenuItem in week.orderedMenuItems:
			parts = orderedMenuItem.split(" ")
			orderedQuantity = int(parts[0])
			orderedItemKey = parts[1]
			userOrders[orderedItemKey] = orderedQuantity
	return userOrders

def getOrderTotal(week):
	orderTotal = 0
	for orderedComposit in week.orderedComposits:
		parts = orderedComposit.split(" ")
		orderedQuantity = int(parts[0])
		orderedItemKey = parts[1]
		composit = getComposit(orderedItemKey)
		if composit['price'] != 0:
			orderTotal = orderTotal + composit['price'] * orderedQuantity
	for orderedMenuItem in week.orderedMenuItems:
		parts = orderedMenuItem.split(" ")
		orderedQuantity = int(parts[0])
		orderedItemKey = parts[1]
		menuItem = getMenuItem(orderedItemKey)
		if menuItem['price'] != 0:
			orderTotal = orderTotal + menuItem['price'] * orderedQuantity
	return orderTotal

class MenuOrderPage(BaseHandler):
	def get(self):
		firstOrderableDay=getFirstOrderableDate(self)
		day=getOrderBaseDate(self)
		monday = getMonday(day)
		#Determine the week
		#Organize into days
		menu=[] #Contains menu items
		actualOrder=self.session.get(ACTUAL_ORDER,[])
		dishCategories=getDishCategories()
		orderedPrice = [0,0,0,0,0]
		basketPrice = [0,0,0,0,0]
		userKey = self.session.get(USER_KEY,None)
		userOrders={}
		if (userKey != None):
			user = User.get(userKey)
			userOrders = getUserOrdersForWeek(user, monday)
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
				composits=getDaysComposits(actualDay, categoryKey)
				#Filter menu items
				actualMenuItems=[]
				actualComposits=[]
				for menuItem in menuItems:
					itemKeyStr=menuItem['key']
					try:
						if (actualOrder!=None) and (itemKeyStr in actualOrder):
							menuItem['inCurrentOrder']=actualOrder[itemKeyStr]
							try:
								basketPrice[i] = basketPrice[i] + menuItem['price'] * int(actualOrder[itemKeyStr])
							except:
								pass
						else:
							menuItem['inCurrentOrder']=0
						try:
							menuItem['orderedQuantity'] = userOrders[itemKeyStr]
							try:
								orderedPrice[i] = orderedPrice[i] + menuItem['price'] * int(userOrders[itemKeyStr])
							except:
								pass
						except KeyError:
							menuItem['orderedQuantity'] = 0
						if actualDay < firstOrderableDay or (menuItem['active'] == False):
							menuItem['orderable']=False
						else:
							menuItem['orderable']=True
						#if (menuItem.orderable or menuItem.orderedQuantity > 0):
						actualMenuItems.append(menuItem)
						itemsInRows=itemsInRows+1
					except ReferencePropertyResolveError:
						continue
				for composit in composits:
					if (actualOrder!=None) and (composit['key'] in actualOrder):
						composit['inCurrentOrder']=actualOrder[composit['key']]
						try:
							basketPrice[i] = basketPrice[i] + composit['price'] * int(actualOrder[composit['key']])
						except:
							pass
					else:
						composit['inCurrentOrder']=0
					try:
						composit['orderedQuantity'] = userOrders[composit['key']]
						try:
							orderedPrice[i] = orderedPrice[i] +  composit['price'] * int(userOrders[composit['key']])
						except:
							pass
					except KeyError:
						composit['orderedQuantity'] = 0
					if composit['day'] < firstOrderableDay or (composit['active'] == False):
						composit['orderable']=False
					else:
						composit['orderable']=True
					actualComposits.append(composit)
					itemsInRows=itemsInRows + 1
				actualDayObject["menuItems"]=actualMenuItems
				actualDayObject["composits"]=actualComposits
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
		prevMonday=monday + datetime.timedelta(days=-7)
		nextMonday=monday + datetime.timedelta(days=7)
		today=datetime.date.today()
		actualMonday = getMonday(today)
		template_values = {
			'days':days,
			'menu':menu
		}
		if nextMonday <= actualMonday + datetime.timedelta(days=FURTHEST_DAY_DISPLAYED):
			template_values['next'] = nextMonday
		if prevMonday >= actualMonday:
			template_values['prev'] = prevMonday
		# A single dish with editable ingredient list
		template = jinja_environment.get_template('templates/menuOrder.html')
		self.printPage(str(day), template.render(template_values), True)
	def post(self):
		actualOrder = self.session.get(ACTUAL_ORDER,{})
		day=getFormDate(self)
		# Add order
		for field in self.request.arguments():
			if (field[:3]=="MIC"):
				actualOrder[field[3:]]=self.request.get(field)
		self.session[ACTUAL_ORDER]=actualOrder
		self.redirect("/order?day="+str(day))

class ClearOrderPage(BaseHandler):
	def get(self):
		day=getFormDate(self)
		self.session[ACTUAL_ORDER]={}
		self.redirect("/order?day="+str(day))
	def post(self):
		day=getFormDate(self)
		self.session[ACTUAL_ORDER]={}
		self.redirect("/order?day="+str(day))

class ReviewPendingOrderPage(BaseHandler):
	def get(self):
		day=getOrderBaseDate(self)
		monday = getMonday(day)
		actualOrder=self.session.get(ACTUAL_ORDER,{})
		if (len(actualOrder) > 0):
			orderedMenuItemKeys=[]
			for key in actualOrder.keys():
				orderedMenuItemKeys.append(key)
			mayBeNullOrderedItems=db.get(orderedMenuItemKeys)
			orderedItems=[]
			composits=[]
			for item in mayBeNullOrderedItems:
				if item != None:
					if type(item) == MenuItem:
						orderedItems.append(item)
					else:
						composits.append(item)
			userOrders={}
			userKey = self.session.get(USER_KEY,None)
			if (userKey != None):
				user = User.get(userKey)
				getUserOrdersForWeek(user, monday)
			#Organize into days
			menu=[] #Contains menu items
			actualOrder=self.session.get(ACTUAL_ORDER,[])
			dishCategories=getDishCategories()
			dayTotal = [0,0,0,0,0]
			menuItems=sorted(orderedItems, key=lambda item:item.dish.title)
			for category in dishCategories:
				actualCategoryObject={}
				actualCategoryObject['category']=category
				items=[]
				orderedPrice=[0,0,0,0,0,0,0]
				itemsInRows=0
				for i in range(0,5):
					actualDay=monday+datetime.timedelta(days=i)
					actualDayObject={}
					actualDayObject["day"]=dayNames[i]
					actualDayObject["date"]=actualDay
					#Filter menu items
					actualMenuItems=[]
					actualComposits=[]
					for menuItem in menuItems:
						try:
							menuItem.dish.category
						except ReferencePropertyResolveError:
							continue
						if str(menuItem.dish.category.key())==category['key'] and menuItem.day==actualDay:
							try:
								if (actualOrder!=None) and (str(menuItem.key()) in actualOrder) and int(actualOrder[str(menuItem.key())]) != 0:
									# Create an object to append to the UI
									menuItemObject = getMenuItem(str(menuItem.key()))
									menuItemObject['inCurrentOrder']=actualOrder[menuItemObject['key']]
									try:
										menuItemObject['basketprice'] = int(menuItemObject['inCurrentOrder']) * menuItemObject['price']
									except TypeError:
										menuItemObject['basketprice'] = 0
									try:
										menuItemObject['orderedQuantity'] = userOrders[menuItemObject['key']]
										try:
											orderedPrice[i] = orderedPrice[i] + menuItem['price'] * int(userOrders[menuItemObject['key']])
										except:
											pass
									except:
										menuItemObject['orderedQuantity'] = 0
									dayTotal[i] = dayTotal[i] + menuItemObject['basketprice']
									menuItemObject['orderable']=True
									actualMenuItems.append(menuItemObject)
									itemsInRows=itemsInRows+1
							except ValueError:
								pass	
					for composit in composits:
						if str(composit.category.key())==category['key'] and composit.day==actualDay:
							try:
								if (actualOrder!=None) and (str(composit.key()) in actualOrder) and int(actualOrder[str(composit.key())]) != 0:
									# Create an object to append to the UI
									compositObject = getComposit(str(composit.key()))
									compositObject['inCurrentOrder']=actualOrder[compositObject['key']]
									try:
										compositObject['basketprice'] = int(compositObject['inCurrentOrder']) * compositObject['price']
									except TypeError:
										compositObject['basketprice'] = 0
									dayTotal[i] = dayTotal[i] + compositObject['basketprice']
									compositObject['orderable']=True
									try:
										compositObject['orderedQuantity'] = userOrders[compositObject['key']]
										try:
											orderedPrice[i] = orderedPrice[i] + menuItem['price'] * int(userOrders[compositObject['key']])
										except:
											pass
									except:
										compositObject['orderedQuantity'] = 0
									
									actualComposits.append(compositObject)
									itemsInRows=itemsInRows+1
							except ValueError:
								pass
					actualDayObject["menuItems"]=actualMenuItems
					actualDayObject["composits"]=actualComposits
					items.append(actualDayObject)
				actualCategoryObject["days"]=items
				if (itemsInRows > 0):
					menu.append(actualCategoryObject)
			days=[]
			# Adds header information
			user = getUser(self)
			for i in range(0,5):
				actualDayObject={}
				actualDate=monday+datetime.timedelta(days=i)
				actualDayObject["day"] = dayNames[i]
				actualDayObject["date"] = actualDate
				actualDayObject["total"] = dayTotal[i]
				days.append(actualDayObject)
			# Add addresses
			
			# A single dish with editable ingredient list
			prevMonday=monday + datetime.timedelta(days=-7)
			nextMonday=monday + datetime.timedelta(days=7)
			today=datetime.date.today()
			actualMonday = getMonday(today)
			template_values = {
				'days':days,
				'user':user,
				'menu':menu
			}
			if nextMonday <= actualMonday + datetime.timedelta(days=FURTHEST_DAY_DISPLAYED):
				template_values['next'] = nextMonday
			if prevMonday >= actualMonday:
				template_values['prev'] = prevMonday
			# A single dish with editable ingredient list
			template = jinja_environment.get_template('templates/reviewPendingOrder.html')
			self.printPage(str(day), template.render(template_values), True)
		else:
			template = jinja_environment.get_template('templates/noOrder.html')
			self.printPage(None, template.render(), True)
	def post(self):
		actualOrder = self.session.get(ACTUAL_ORDER,{})
		day=getOrderBaseDate(self)
		# Add order
		for field in self.request.arguments():
			if (field[:3]=="MIC"):
				actualOrder[field[3:]]=self.request.get(field)
		self.session[ACTUAL_ORDER]=actualOrder
		# Get addresses and save them to the proper date
		self.redirect("/pendingOrder?day="+str(day))

class ReviewOrderedMenuPage(BaseHandler):
	def get(self):
		if(not isUserLoggedIn(self)):
			self.redirect("/")
			return
		day = getOrderBaseDate(self)
		monday = getMonday(day)
		firstOrderableDay=getFirstOrderableDate(self);
		user = getUser(self)
		weeks = user.weeks.filter("monday = ", monday)
		if (weeks.count() == 1):
			week = weeks.get()
		else:
			week = UserWeekOrder()
		days=[]
		for i in range(0,5):
			actualDayObject={}
			orderedPrice = 0
			actualDay=monday+datetime.timedelta(days=i)
			if actualDay < firstOrderableDay:
				actualDayObject["changable"] = False
			else:
				actualDayObject["changable"] = True
			daysOrderItems=getOrderedItemsFromWeekData(week, actualDay)
			actualDayObject['orderedItems'] = daysOrderItems
			for orderedItem in daysOrderItems:
				try:
					orderedPrice = orderedPrice + orderedItem['price'] * orderedItem['orderedQuantity']
				except:
					pass
			actualDayObject['day']=dayNames[i]
			actualDayObject['date'] = actualDay
			actualDayObject["orderedPrice"] = orderedPrice
			if daysOrderItems != None and len(daysOrderItems)>0:
				address = getOrderAddress(week, actualDay)
				if address == None:
					address = user.addresses.get()
				actualDayObject['address'] = address
				actualDayObject["deliveryCost"] = getDeliveryCost(address.district, orderedPrice) 
			days.append(actualDayObject)
		# A single dish with editable ingredient list
		prevMonday=monday + datetime.timedelta(days=-7)
		nextMonday=monday + datetime.timedelta(days=7)
		today=datetime.date.today()
		actualMonday = getMonday(today)
		availableAddresses = []
		for address in user.addresses.filter('active = ', True):
			address.deliveryCost = getDeliveryCost(address.district,0)
			address.deliveryLimit = getDeliveryLimit(address.district)
			availableAddresses.append(address)
		template_values = {
			'days':days,
			'addresses':availableAddresses,
		}
		if nextMonday <= actualMonday + datetime.timedelta(days=FURTHEST_DAY_DISPLAYED):
			template_values['next'] = nextMonday
		if prevMonday >= actualMonday:
			template_values['prev'] = prevMonday
		# A single dish with editable ingredient list
		template = jinja_environment.get_template('templates/reviewOrderedMenu.html')
		self.printPage(str(day), template.render(template_values), False, True)
	def post(self):
		# Get addresses and save them to the proper day
		if(not isUserLoggedIn(self)):
			self.redirect("/")
			return
		firstOrderableDay=getFirstOrderableDate(self);
		for field in self.request.arguments():
			if (field[:8]=="address_"):
				day=datetime.datetime.strptime(field[8:], "%Y-%m-%d").date()
				if day < firstOrderableDay:
					continue
				user = getUser(self)
				monday = getMonday(day)
				firstOrderableDay=getFirstOrderableDate(self);
				if day >= firstOrderableDay:
					weeks = user.weeks.filter("monday = ", monday)
					if weeks.count() == 1:
						week = weeks.get()
						address=Address.get(self.request.get(field))
						if day.weekday() == 0:
							week.mondayAddress = address
						elif day.weekday() == 1:
							week.tuesdayAddress = address
						elif day.weekday() == 2:
							week.wednesdayAddress = address
						elif day.weekday() == 3:
							week.thursdayAddress = address
						elif day.weekday() == 4:
							week.fridayAddress = address
						elif day.weekday() == 5:
							week.saturdayAddress = address
						elif day.weekday() == 6:
							week.sundayAddress = address
						week.put()
		self.redirect("/personalMenu")

class ConfirmOrder(BaseHandler):
	def post(self):
		#One step ordering
		if(not isUserLoggedIn(self)):
			self.redirect("/registration")
			return
		userKey = self.session.get(USER_KEY,None)
		user=None
		if (userKey != None):
			user = User.get(userKey)
		addresses = user.addresses.filter("active = ", True)
		if addresses.count()==0:
			template = jinja_environment.get_template('templates/no_address.html')
			self.printPage('Rendelesek', template.render(), True)
			return
		actualOrder = self.session.get(ACTUAL_ORDER,{})
		firstOrderableDay = getFirstOrderableDate(self)
		if (len(actualOrder) > 0):
			for orderKey in actualOrder.keys():
				orderItemCount = int(actualOrder[orderKey])
				if (orderItemCount != 0):
					item = db.get(orderKey)
					day = item.day
					if day < firstOrderableDay:
						continue
					monday = getMonday(day)
					weeks = user.weeks.filter("monday = ", monday)
					week = None
					alreadyOrdered = 0
					if (weeks.count() == 1):
						week = weeks[0]
						if type(item) == MenuItem:
							newItems = []
							itemExists = False
							for item in week.orderedMenuItems:
								parts = item.split(" ")
								weekItemQuantity = parts[0]
								weekItemKey = parts[1]
								if weekItemKey == orderKey:
									itemExists = True
									alreadyOrdered = int(weekItemQuantity) + orderItemCount
									if (alreadyOrdered > 0):
										newItem = str(alreadyOrdered) + " " + orderKey
										newItems.append(newItem)
								else:
									newItems.append(item)
							if ((not itemExists) and orderItemCount > 0):
								newItem = str(orderItemCount) + " " + orderKey
								newItems.append(newItem)
							week.orderedMenuItems = newItems
						else:
							newItems = []
							itemExists = False
							for item in week.orderedComposits:
								parts = item.split(" ")
								weekItemQuantity = parts[0]
								weekItemKey = parts[1]
								if weekItemKey == orderKey:
									itemExists = True
									alreadyOrdered = int(weekItemQuantity) + orderItemCount
									if (alreadyOrdered > 0):
										newItem = str(alreadyOrdered) + " " + orderKey
										newItems.append(newItem)
								else:
									newItems.append(item)
							if ((not itemExists) and orderItemCount > 0):
								newItem = str(orderItemCount) + " " + orderKey
								newItems.append(newItem)
							week.orderedComposits = newItems
					else:
						week = UserWeekOrder()
						week.user = user
						week.monday = monday
						# Add address for every day
						defaultAddress = user.addresses.filter("active = ", True).get()
						week.mondayAddress = defaultAddress
						week.tuesdayAddress = defaultAddress
						week.wednesdayAddress = defaultAddress
						week.thursdayAddress = defaultAddress
						week.fridayAddress = defaultAddress
						week.saturdayAddress = defaultAddress
						week.sundayAddress = defaultAddress
						if orderItemCount > 0:
							newItems = []
							newItem = str(orderItemCount) + " " + orderKey
							newItems.append(newItem)
							if type(item) == MenuItem:
								week.orderedMenuItems = newItems
							else:
								week.orderedComposits = newItems
					week.put()
			template_values = {
				"user":user
			}
			# Send email notification to the user
			messageTxtTemplate = jinja_environment.get_template('templates/orderNotificationMail.txt')
			messageHtmlTemplate = jinja_environment.get_template('templates/orderNotificationMail.html')
			message = mail.EmailMessage(sender="Diet Futar <dietfutar@dietfutar.hu>")
			message.subject="Diet-futar, rendeles visszaigazolasa"
			message.to = user.email
			message.body = messageTxtTemplate.render(template_values)
			message.html = messageHtmlTemplate.render(template_values)
			message.send()
			self.session[ACTUAL_ORDER]={}
			#self.response.out.write(messageTemplate.render(template_values));
			self.redirect("/personalMenu")
		else:
			print "Nothing to confirm"