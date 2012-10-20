#!/usr/bin/env python
import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler, getBaseDate, getFormDate
import datetime
from model import MenuItem, UserOrder, UserOrderItem, User,\
	UserOrderAddress, Address
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
from user_management import USER_KEY, getUser, isUserLoggedIn
from timezone import USTimeZone
from cache_category import getCategories
from cache_menu_item import getDaysMenuItems
from cache_composit import getDaysComposits
#from user_management import getUserBox

ACTUAL_ORDER="actualOrder"
LAST_ORDER_HOUR=12
dayNames=["H&#233;tf&#337;","Kedd","Szerda","Cs&#252;t&#246;rt&#246;k","P&#233;ntek","Szombat","Vas&#225;rnap"]
timeZone=USTimeZone(1, "CEST", "CEST", "CEST")

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MenuOrderPage(BaseHandler):
	def get(self):
		today=datetime.date.today()
		now=datetime.datetime.now(timeZone)
		firstOrderableDay=today+datetime.timedelta(days=1)
		if now.hour > LAST_ORDER_HOUR:
			firstOrderableDay=today+datetime.timedelta(days=2)
		day=getBaseDate(self)
		calendar=day.isocalendar()
		monday=day+datetime.timedelta(days=-calendar[2]+1)
		sunday=day+datetime.timedelta(days=-calendar[2]+7)
		#Fetch user's previous orders. User orders is an object associating menu item keys with quantities		
		userOrders={}
		userKey = self.session.get(USER_KEY,None)
		if (userKey != None):
			user = User.get(userKey)
			weekOrderItems=user.orderedItems.filter("day <= ", sunday).filter("day >= ", monday)
			for orderedItem in weekOrderItems:
				itemQuantity = 0
				try:
					orderedItemKey=""
					if orderedItem.orderedItem == None:
						orderedItemKey = str(orderedItem.orderedComposit.key())
					else:
						orderedItemKey = str(orderedItem.orderedItem.key())
					if (userOrders.has_key(orderedItemKey)):
						itemQuantity = int(userOrders[orderedItemKey])
					if (orderedItem.itemCount != None):
						userOrders[orderedItemKey] = itemQuantity + orderedItem.itemCount
				except ReferencePropertyResolveError:
					itemQuantity=0
		#Determine the week
		#Organize into days
		menu=[] #Contains menu items
		actualOrder=self.session.get(ACTUAL_ORDER,[])
		dishCategories=getCategories()
		orderedPrice = [0,0,0,0,0]
		basketPrice = [0,0,0,0,0]
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
					itemKey=menuItem['key']
					itemKeyStr=str(itemKey)
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
							menuItem['orderedQuantity'] = userOrders[itemKey]
							try:
								orderedPrice[i] = orderedPrice[i] + menuItem['price'] * int(userOrders[itemKey])
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
		prevMonday=day+datetime.timedelta(days=-calendar[2]+1-7)
		nextMonday=day+datetime.timedelta(days=-calendar[2]+1+7)
		today=datetime.date.today()
		todayCalendat=today.isocalendar()
		actualMonday=today+datetime.timedelta(days=-todayCalendat[2]+1)
		template_values = {
			'days':days,
			'menu':menu
		}
		if nextMonday <= actualMonday + datetime.timedelta(days=7):
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
			day=getBaseDate(self)
			#Determine the week
			calendar=day.isocalendar()
			#Organize into days
			menu=[] #Contains menu items
			actualOrder=self.session.get(ACTUAL_ORDER,[])
			dishCategories=getCategories()
			monday=day+datetime.timedelta(days=-calendar[2]+1)
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
					actualComposits=[]
					for menuItem in menuItems:
						try:
							menuItem.dish.category
						except ReferencePropertyResolveError:
							continue
						if str(menuItem.dish.category.key())==category['key'] and menuItem.day==actualDay:
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
					for composit in composits:
						if str(composit.category.key())==category['key'] and composit.day==actualDay:
							try:
								if (actualOrder!=None) and (str(composit.key()) in actualOrder) and int(actualOrder[str(composit.key())]) != 0:
									composit.inCurrentOrder=actualOrder[str(composit.key())]
									try:
										composit.basketprice = int(composit.inCurrentOrder) * composit.price
									except TypeError:
										composit.basketprice = 0
									dayTotal[i] = dayTotal[i] + composit.basketprice
									actualComposits.append(composit)
									itemsInRows=itemsInRows+1
								else:
									composit.inCurrentOrder=False
							except ValueError:
								composit.inCurrentOrder=False
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
			prevMonday=day+datetime.timedelta(days=-calendar[2]+1-7)
			nextMonday=day+datetime.timedelta(days=-calendar[2]+1+7)
			today=datetime.date.today()
			todayCalendat=today.isocalendar()
			actualMonday=today+datetime.timedelta(days=-todayCalendat[2]+1)
			template_values = {
				'days':days,
				'user':user,
				'menu':menu
			}
			if nextMonday <= actualMonday + datetime.timedelta(days=7):
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
		day=getFormDate(self)
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
		day=getBaseDate(self)
		now=datetime.datetime.now(timeZone)
		today=datetime.date.today()
		firstOrderableDay=today+datetime.timedelta(days=1)
		if now.hour > LAST_ORDER_HOUR:
			firstOrderableDay=today+datetime.timedelta(days=2)
		#Fetch user's previous orders. User orders is an object associating menu item keys with quantities
		userOrders={}
		userKey = self.session.get(USER_KEY,None)
		if (userKey != None):
			user = User.get(userKey)
			for userOrder in user.userOrders:
				for orderedItem in userOrder.items:
					itemQuantity = 0
					try: 
						itemKey = ""
						if orderedItem.orderedItem == None:
							itemKey = str(orderedItem.orderedComposit.key())
						else:	
							itemKey = str(orderedItem.orderedItem.key())
						if (userOrders.has_key(itemKey)):
							itemQuantity = int(userOrders[itemKey])
						if (orderedItem.itemCount != None):
							userOrders[itemKey] = itemQuantity + orderedItem.itemCount
					except ReferencePropertyResolveError:
						itemQuantity=0
		#Determine the week
		calendar=day.isocalendar()
		#Organize into days
		menu=[] #Contains menu items
		dishCategories=getCategories()
		monday=day+datetime.timedelta(days=-calendar[2]+1)
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
				actualComposits=[]
				menuItems=getDaysMenuItems(actualDay, category['key'])
				for menuItem in menuItems:
					try:
						try:
							menuItem['orderedQuantity'] = int(userOrders[menuItem['key']])
							if menuItem['price'] == None:
								menuItem['price'] = 0
							orderedPrice[i] = orderedPrice[i] +  menuItem['price'] * int(userOrders[menuItem['key']])
							itemsInRows=itemsInRows+1
						except (KeyError, ValueError):
							menuItem['orderedQuantity'] = 0
						if menuItem['orderedQuantity'] > 0:
							actualMenuItems.append(menuItem)
					except ReferencePropertyResolveError:
						continue
				composits=getDaysComposits(actualDay, category['key'])
				for composit in composits:
					try:
						try:
							composit['orderedQuantity'] = int(userOrders[composit['key']])
							if composit['price'] == None:
								composit['price'] = 0
							orderedPrice[i] = orderedPrice[i] + composit['price'] * composit['orderedQuantity']
							itemsInRows=itemsInRows+1
						except (KeyError, ValueError, TypeError):
							composit['orderedQuantity'] = 0
						if composit['orderedQuantity'] > 0:
							actualComposits.append(composit)
					except ReferencePropertyResolveError:
						continue
				actualDayObject["menuItems"]=actualMenuItems
				actualDayObject["composits"]=actualComposits
				items.append(actualDayObject)
			actualCategoryObject["days"]=items
			if (itemsInRows > 0):
				menu.append(actualCategoryObject)
		days=[]
		user = getUser(self)
		for i in range(0,5):
			actualDayObject={}
			actualDate=monday+datetime.timedelta(days=i)
			if actualDate < firstOrderableDay:
				actualDayObject["changable"] = False
			else:
				actualDayObject["changable"] = True
			actualDayObject["date"] = actualDate
			actualDayObject["orderedPrice"] = orderedPrice[i]
			actualDayObject["day"]=dayNames[i]
			addresses=user.deliveryAddresses.filter("day = ", actualDate)
			if addresses.count() > 0:
				actualDayObject["address"]=addresses[0].address
			days.append(actualDayObject)
		# A single dish with editable ingredient list
		prevMonday=day+datetime.timedelta(days=-calendar[2]+1-7)
		nextMonday=day+datetime.timedelta(days=-calendar[2]+1+7)
		today=datetime.date.today()
		todayCalendat=today.isocalendar()
		actualMonday=today+datetime.timedelta(days=-todayCalendat[2]+1)
		template_values = {
			'days':days,
			'addresses':user.addresses,
			'menu':menu
		}
		if nextMonday <= actualMonday + datetime.timedelta(days=7):
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
		now=datetime.datetime.now(timeZone)
		today=datetime.date.today()
		firstOrderableDay=today+datetime.timedelta(days=1)
		if now.hour > LAST_ORDER_HOUR:
			firstOrderableDay=today+datetime.timedelta(days=2)
		for field in self.request.arguments():
			if (field[:8]=="address_"):
				day=datetime.datetime.strptime(field[8:], "%Y-%m-%d").date()
				if day < firstOrderableDay:
					continue
				user = getUser(self)
				# Check if user has order for the day
				orders=user.orderedItems.filter("day = ", day)
				if orders.count() > 0:
					addresses = user.deliveryAddresses
					actualAddress=None
					if addresses.count() > 0:
						for address in addresses:
							if (address.day == day):
								actualAddress=address
								break
					if actualAddress==None:
						actualAddress=UserOrderAddress()
						actualAddress.user=user
						actualAddress.day=day
					address=Address.get(self.request.get(field))
					actualAddress.address=address
					actualAddress.put()
		self.redirect("/personalMenu")

class ConfirmOrder(BaseHandler):
	def post(self):
		#One step ordering - this is a trial
		if(not isUserLoggedIn(self)):
			self.redirect("/registration")
			return
		userKey = self.session.get(USER_KEY,None)
		user=None
		if (userKey != None):
			user = User.get(userKey)
		addresses = user.addresses
		if addresses.count()==0:
			template = jinja_environment.get_template('templates/no_address.html')
			self.printPage('Rendelesek', template.render(), True)
			return
		actualOrder = self.session.get(ACTUAL_ORDER,{})
		now=datetime.datetime.now(timeZone)
		orderDate=now
		today=datetime.date.today()
		firstOrderableDay=today+datetime.timedelta(days=1)
		if now.hour > LAST_ORDER_HOUR:
			firstOrderableDay=today+datetime.timedelta(days=2)
		#Save order
		if (len(actualOrder) > 0):
			userOrder = UserOrder()
			userOrder.canceled = False
			userOrder.orderDate = orderDate
			userOrder.price = 0
			userOrder.user = user
			userOrder.put()
			for orderKey in actualOrder.keys():
				try:
					if (int(actualOrder[orderKey]) != 0):
						item = db.get(orderKey)
						day=None
						day = item.day
						if day < firstOrderableDay:
							continue
						orderItem = UserOrderItem()
						alreadyOrdered = 0
						orderItemCount = int(actualOrder[orderKey])
						if orderItemCount < 0:
							# Have to go through user's orders to see if current order is a negative order
							# checks if user goes below zero if posting it
							placedOrders=user.orderedItems.filter("day = ", day)
							if type(item) == MenuItem:
								orderItem.orderedItem=item
								for placedOrder in placedOrders:
									if placedOrder.orderedItem != None and placedOrder.orderedItem.key() == item.key():
										alreadyOrdered = alreadyOrdered + placedOrder.itemCount
							else:
								orderItem.orderedComposit=item
								for placedOrder in placedOrders:
									if placedOrder.orderedComposit != None and placedOrder.orderedComposit.key() == item.key():
										alreadyOrdered = alreadyOrdered + placedOrder.itemCount
						else:
							if type(item) == MenuItem:
								orderItem.orderedItem=item
							else:
								orderItem.orderedComposit=item
						if alreadyOrdered + orderItemCount < 0:
							orderItemCount = - alreadyOrdered
						orderItem.itemCount = orderItemCount
						orderItem.day=day
						orderItem.userOrder = userOrder
						orderItem.user = userOrder.user
						try:
							orderItem.price = item.price * orderItemCount
						except TypeError:
							orderItem.price = 0
						userOrder.price = userOrder.price + orderItem.price
						if orderItemCount != 0:
							orderItem.put()
							daysAddress = user.deliveryAddresses.filter("day = ", day)
							if daysAddress.count() == 0:
								# Create new order address
								daysAddress=UserOrderAddress()
								daysAddress.day=day
								daysAddress.user=user
								daysAddress.address = addresses[addresses.count()-1]
								daysAddress.put()
						# TODO check if there are any orders left for the day
						placedOrders=user.orderedItems.filter("day = ", day)
						items = {}
						for placedOrder in placedOrders:
							key = None
							if placedOrder.orderedItem != None:
								key = placedOrder.orderedItem.key()
							else:
								key = placedOrder.orderedComposit.key()
							if items.has_key(key):
								items[key]=items[key] + placedOrder.itemCount
							else:
								items[key] = placedOrder.itemCount
						hasItem = False
						for item in items.values():
							if item > 0:
								hasItem = True
								break
						if not hasItem:
							daysAddress=user.deliveryAddresses.filter("day = ", day)[0]
							daysAddress.delete()
				except ValueError, ReferencePropertyResolveError:
					continue
			userOrder.put()
			self.session[ACTUAL_ORDER]={}
			self.redirect("/personalMenu")
		else:
			print "Nothing to confirm"

class PreviousOrders(BaseHandler):
	def get(self):
		if(not isUserLoggedIn(self)):
			self.redirect("/registration")
			return
		userKey = self.session.get(USER_KEY,None)
		if (userKey != None):
			userOrders=[]
			user = User.get(userKey)
			for order in user.userOrders:
				order.orderDate = order.orderDate + datetime.timedelta(hours=2)
				userOrders.append(order)
			template_values = {
				'userOrders':userOrders
			}
			template = jinja_environment.get_template('templates/previousOrders.html')
			self.printPage('Rendelesek', template.render(template_values), False, True)
			

class PreviousOrder(BaseHandler):
	def get(self):
		if(not isUserLoggedIn(self)):
			self.redirect("/registration")
			return
		orderKey = self.request.get("orderKey")
		userOrder = UserOrder.get(orderKey)
		if (userOrder != None):
			template_values = {
				'userOrder':userOrder
			}
			template = jinja_environment.get_template('templates/previousOrder.html')
			self.printPage('Rendeles', template.render(template_values), False, True)



















