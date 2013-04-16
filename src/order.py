#!/usr/bin/env python
import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler, getFormDate,\
	getFirstOrderableDate, getMonday, logInfo, timeZone,\
	getBasketBaseDate, dayNames
import datetime
from model import MenuItem, User, UserWeekOrder, Address, UserOrderEvent
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
from user_management import USER_KEY, getUser, isUserLoggedIn
from cache_menu_item import getDaysMenuItems, getMenuItem
from cache_composit import getDaysComposits, getComposit
from google.appengine.api import mail
from cache_dish_category import getDishCategories
from orderHelper import getUserOrdersForWeek, getOrderedItemsFromWeekData,\
	getOrderAddress, isMenuItem, getOrderComment, getZipBasedDeliveryCost,\
	getZipBasedDeliveryLimit
from cacheWeek import updateUser
from base_handler import getOrderBaseDate
#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

ACTUAL_ORDER="actualOrder"
FURTHEST_DAY_DISPLAYED=14

class MenuOrderPage(BaseHandler):
	URL = '/order'
	def get(self):
		#Determine the week
		day = getOrderBaseDate(self)
		firstOrderableDay = getFirstOrderableDate(self)
		monday = getMonday(day)
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
		logInfo(self, self.URL, "DISPLAY_MENU")
		self.printPage(str(day), template.render(template_values), True)
	def post(self):
		actualOrder = self.session.get(ACTUAL_ORDER,{})
		day=getFormDate(self)
		# Add order
		for field in self.request.arguments():
			if (field[:3]=="MIC"):
				actualOrder[field[3:]]=self.request.get(field)
		self.session[ACTUAL_ORDER]=actualOrder
		logInfo(self, self.URL, "SAVED_ORDER")
		self.redirect("/order?day="+str(day))

class ClearOrderPage(BaseHandler):
	URL = '/clearOrder'
	def get(self):
		day=getFormDate(self)
		self.session[ACTUAL_ORDER]={}
		self.redirect("/order?day="+str(day))
	def post(self):
		day=getFormDate(self)
		self.session[ACTUAL_ORDER]={}
		logInfo(self, self.URL, "CLEAR_ORDER")
		self.redirect("/order?day="+str(day))

class ReviewPendingOrderPage(BaseHandler):
	URL = '/pendingOrder'
	def get(self):
		actualOrder=self.session.get(ACTUAL_ORDER,{})
		day=getBasketBaseDate(actualOrder, self)
		monday = getMonday(day)
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
			#Organize into days
			menu=[]
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
			logInfo(self, self.URL, "DISPLAY_BASKET")
			self.printPage(None, template.render(), True)
	def post(self):
		actualOrder = self.session.get(ACTUAL_ORDER,{})
		day=getFirstOrderableDate(self)
		# Add order
		for field in self.request.arguments():
			if (field[:3]=="MIC"):
				actualOrder[field[3:]]=self.request.get(field)
		self.session[ACTUAL_ORDER]=actualOrder
		# Get addresses and save them to the proper date
		logInfo(self, self.URL, "MODIFIED_ADDRESS")
		self.redirect("/pendingOrder?day="+str(day))

class ReviewOrderedMenuPage(BaseHandler):
	URL = '/personalMenu'
	def get(self):
		if(not isUserLoggedIn(self)):
			self.redirect("/")
			return
		day = getOrderBaseDate(self)
		monday = getMonday(day)
		firstOrderableDay = getFirstOrderableDate(self);
		user = getUser(self)
		weeks = user.weeks.filter("monday = ", monday)
		days=[]
		for i in range(0,5):
			actualDayObject={}
			orderedPrice = 0
			actualDay=monday+datetime.timedelta(days=i)
			if actualDay < firstOrderableDay:
				actualDayObject["changable"] = False
			else:
				actualDayObject["changable"] = True
			daysOrderItems = getOrderedItemsFromWeekData(weeks, actualDay)
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
				if (weeks.count() > 0):
					week = weeks.get()
				else:
					week = UserWeekOrder()
				address = getOrderAddress(week, actualDay)
				comment = getOrderComment(week, actualDay)
				if address == None:
					address = user.addresses.get()
				actualDayObject['address'] = address
				actualDayObject['comment'] = comment
				actualDayObject["deliveryCost"] = getZipBasedDeliveryCost(address.zipNumCode, orderedPrice)
			days.append(actualDayObject)
		# A single dish with editable ingredient list
		prevMonday=monday + datetime.timedelta(days=-7)
		nextMonday=monday + datetime.timedelta(days=7)
		today=datetime.date.today()
		actualMonday = getMonday(today)
		availableAddresses = []
		for address in user.addresses:
			address.deliveryCost = getZipBasedDeliveryCost(address.zipNumCode, 0)
			address.deliveryLimit = getZipBasedDeliveryLimit(address.zipNumCode)
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
		logInfo(self, self.URL, "REVIEW_PERSONAL_MENU")
		self.printPage(str(day), template.render(template_values), False, True)
	def post(self):
		# Get addresses and comments and save them to the proper day
		# Works only for a singe week view
		if(not isUserLoggedIn(self)):
			self.redirect("/")
			return
		firstOrderableDay=getFirstOrderableDate(self);
		week = None
		for field in self.request.arguments():
			if ((field[:8]=="address_") or (field[:8]=="comment_")):
				day=datetime.datetime.strptime(field[8:], "%Y-%m-%d").date()
				if day < firstOrderableDay:
					continue
				if week == None:
					user = getUser(self)
					monday = getMonday(day)
					weeks = user.weeks.filter("monday = ", monday)
					if weeks.count() == 1:
						week = weeks.get()
				# If no week was determined, continue, nothing to save here
				if week == None:
					continue
				if field[:8]=="address_":
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
	
				if (field[:8]=="comment_"):
					comment = self.request.get(field)
					if day.weekday() == 0:
						week.mondayComment = comment
					elif day.weekday() == 1:
						week.tuesdayComment = comment
					elif day.weekday() == 2:
						week.wednesdayComment = comment
					elif day.weekday() == 3:
						week.thursdayComment = comment
					elif day.weekday() == 4:
						week.fridayComment = comment
					elif day.weekday() == 5:
						week.saturdayComment = comment
					elif day.weekday() == 6:
						week.sundayComment = comment

		if week != None:
			week.put()

		logInfo(self, self.URL, "MODIFY_ADDRESS_ON_PERSONAL_MENU")
		self.redirect("/personalMenu")

class ConfirmOrder(BaseHandler):
	URL = '/confirmOrder'
	def post(self):
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
		orderTotal = 0
		orderedItems = []
		if (len(actualOrder) > 0):
			# Organize actual order into weeks
			ordersInWeeks = {} # A map holding ordered items with ordered quantiy
			for orderKey in actualOrder.keys():
				orderItemCount = int(actualOrder[orderKey])
				if (orderItemCount != 0):
					item = db.get(orderKey)
					day = item.day
					if day < firstOrderableDay:
						continue
					monday = getMonday(day)
					if ordersInWeeks.has_key(monday):
						weekHolder = ordersInWeeks.get(monday)
					else:
						weekHolder = []
					orderItem = {
						'key' : orderKey,
						'quantity' : orderItemCount
					}
					weekHolder.append(orderItem)
					ordersInWeeks[monday] = weekHolder
			# Go through order week by week
			if len(ordersInWeeks) > 0:
				orderedItemsForMail = {}
				for monday in ordersInWeeks.keys():
					weekHolder = ordersInWeeks.get(monday)
					alreadyOrdered = getUserOrdersForWeek(user, monday)
					# Merge orders for the week
					for item in weekHolder:
						orderedQuantity = item['quantity']
						orderItemKey = item['key']
						# Order should not remove more items than already ordered
						if alreadyOrdered.has_key(orderItemKey):
							alreadyOrderedQuantity = alreadyOrdered.get(orderItemKey)
							if alreadyOrderedQuantity + orderedQuantity < 0:
								orderedQuantity = 0 - alreadyOrderedQuantity
						if isMenuItem(orderItemKey):
							menuItem = getMenuItem(orderItemKey)
							day = menuItem['day']
							menuItem['quantity'] = orderedQuantity
							menuItem['totalPrice'] = orderedQuantity * menuItem['price']
							menuItem['isMenuItem'] = True
							orderTotal = orderTotal + orderedQuantity * menuItem['price']
							orderedItems.append(str(day) + " " + str(orderItemKey) + " " + str(orderedQuantity) + " " + str(menuItem['price']))
							if orderedItemsForMail.has_key(day):
								daysItems = orderedItemsForMail.get(day)
								daysItems.append(menuItem)
							else:
								daysItems = []
								daysItems.append(menuItem)
							orderedItemsForMail[day] = daysItems
						else:
							composit = getComposit(orderItemKey)
							day = composit['day']
							composit['quantity'] = orderedQuantity
							composit['totalPrice'] = orderedQuantity * composit['price']
							composit['isMenuItem'] = False
							orderTotal = orderTotal + orderedQuantity * composit['price']
							orderedItems.append(str(day) + " " + str(orderItemKey) + " " + str(orderedQuantity) + " " + str(composit['price']))
							if orderedItemsForMail.has_key(day):
								daysItems = orderedItemsForMail.get(day)
								daysItems.append(composit)
							else:
								daysItems = []
								daysItems.append(composit)
							orderedItemsForMail[day] = daysItems
						if alreadyOrdered.has_key(orderItemKey):
							orderedQuantity = orderedQuantity + alreadyOrdered.get(orderItemKey)
						if (orderedQuantity > 0):
							alreadyOrdered[orderItemKey] = orderedQuantity
						else:
							alreadyOrdered.pop(orderItemKey, 0)
					# Add stuff to the first week the user created
					daysForMail = orderedItemsForMail.keys()
					sortedDays = sorted(daysForMail)
					sortedItemsForMail = []
					for day in sortedDays:
						sortedItemsForMail.append(
							{'day':day,
							'orders':orderedItemsForMail.get(day)}
						)
					weeks = user.weeks.filter("monday = ", monday)
					if (weeks.count() > 0):
						week = weeks.get()
					else:
						week = UserWeekOrder()
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
					
					orderedMenuItems = []
					orderedComposits = []
					for itemKey in alreadyOrdered.keys():
							newItem = str(alreadyOrdered.get(itemKey)) + " " + itemKey
							if isMenuItem(itemKey):
								orderedMenuItems.append(newItem)
							else:
								orderedComposits.append(newItem)
					week.orderedMenuItems = orderedMenuItems
					week.orderedComposits = orderedComposits
					week.put()
					user.lastOrder = datetime.datetime.now(timeZone).date()
					user.lastOrderFlag = True
					user.put()
				updateUser(user)
				template_values = {
					"user":user,
					'userOrder':sortedItemsForMail,
				}
				logInfo(self, self.URL, "ORDER_POSTED")
				event = UserOrderEvent()
				event.orderDate = datetime.datetime.now(timeZone)
				event.user = user
				event.price = orderTotal
				event.orderedItems = orderedItems
				event.put()
				# Send email notification to the user
				messageTxtTemplate = jinja_environment.get_template('templates/orderNotificationMail.txt')
				messageHtmlTemplate = jinja_environment.get_template('templates/orderNotificationMail.html')
				message = mail.EmailMessage(sender="Diet Futar <dietfutar@dietfutar.hu>")
				message.subject="Diet-futar, rendeles visszaigazolasa"
				message.to = user.email
				message.bcc = "diet-futar@diet-futar.hu"
				message.body = messageTxtTemplate.render(template_values)
				message.html = messageHtmlTemplate.render(template_values)
				message.send()


				self.session[ACTUAL_ORDER]={}
				#self.response.out.write(messageTemplate.render(template_values));
				self.redirect("/personalMenu")
			else:
				print "Error #100: Can't process orders."
		else:
				print "Error #100: Can't process orders."
