#!/usr/bin/env python
import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
import datetime
from model import MenuItem, DishCategory, UserOrder, UserOrderItem, User,\
	Composit, UserOrderAddress, Address
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
from user_management import USER_KEY, getUser
#from user_management import getUserBox

ACTUAL_ORDER="actualOrder"
dayNames=["H&#233;tf&#337;","Kedd","Szerda","Cs&#252;t&#246;rt&#246;k","P&#233;ntek","Szombat","Vas&#225;rnap"]


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
						orderedItemKey=""
						if orderedItem.orderedItem == None:
							orderedItemKey = orderedItem.orderedComposit.key()
						else:
							orderedItemKey = orderedItem.orderedItem.key()
						if (userOrders.has_key(orderedItemKey)):
							itemQuantity = int(userOrders[orderedItemKey])
						if (orderedItem.itemCount != None):
							userOrders[orderedItemKey] = itemQuantity + orderedItem.itemCount
					except ReferencePropertyResolveError:
						itemQuantity=0
		#Determine the week
		calendar=day.isocalendar()
		#Organize into days
		menu=[] #Contains menu items
		actualOrder=self.session.get(ACTUAL_ORDER,[])
		dishCategories=DishCategory.gql("ORDER BY index")
		monday=day+datetime.timedelta(days=-calendar[2]+1)
		sunday=day+datetime.timedelta(days=-calendar[2]+7)
		originalItems=MenuItem.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
		menuItems=sorted(originalItems, key=lambda item:item.dish.title)
		composits=Composit.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
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
				actualComposits=[]
				for menuItem in menuItems:
					try:
						if menuItem.dish.category.key()==category.key() and menuItem.day==actualDay and menuItem.containingMenuItem == None:
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
									orderedPrice[i] = orderedPrice[i] + menuItem.price * int(userOrders[menuItem.key()])
								except:
									pass
							except KeyError:
								menuItem.orderedQuantity = 0
							actualMenuItems.append(menuItem)
							itemsInRows=itemsInRows+1
					except ReferencePropertyResolveError:
						continue
				for composit in composits:
					if composit.category.key()==category.key() and composit.day==actualDay:
						if (actualOrder!=None) and (str(composit.key()) in actualOrder):
							composit.inCurrentOrder=actualOrder[str(composit.key())]
							try:
								basketPrice[i] = basketPrice[i] + composit.price * int(actualOrder[str(composit.key())])
							except:
								pass
						else:
							composit.inCurrentOrder=0
						try:
							composit.orderedQuantity = userOrders[composit.key()]
							try:
								orderedPrice[i] = orderedPrice[i] +  composit.price * int(userOrders[composit.key()])
							except:
								pass
						except KeyError:
							composit.orderedQuantity = 0
						actualComposits.append(composit)
						itemsInRows=itemsInRows+1
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
			composits=[]
			for item in mayBeNullOrderedItems:
				if item != None:
					if type(item) == MenuItem:
						orderedItems.append(item)
					else:
						composits.append(item)
			day=datetime.date.today()
			requestDay=self.request.get('day')
			if ((requestDay != None) and (requestDay != "")):
				parts=requestDay.rsplit("-")
				day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
			#Determine the week
			calendar=day.isocalendar()
			#Organize into days
			menu=[] #Contains menu items
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
					actualComposits=[]
					for menuItem in menuItems:
						try:
							menuItem.dish.category
						except ReferencePropertyResolveError:
							continue
						if menuItem.dish.category.key()==category.key() and menuItem.day==actualDay:
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
						if composit.category.key()==category.key() and composit.day==actualDay:
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
				'next':nextMonday,
				'actual':actualMonday,
				'user':user,
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
		# Get addresses and save them to the proper date
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
						itemKey = ""
						if orderedItem.orderedItem == None:
							itemKey = orderedItem.orderedComposit.key()
						else:	
							itemKey = orderedItem.orderedItem.key()
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
		dishCategories=DishCategory.gql("ORDER BY index")
		monday=day+datetime.timedelta(days=-calendar[2]+1)
		sunday=day+datetime.timedelta(days=-calendar[2]+7)
		originalItems=MenuItem.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
		composits=Composit.gql("WHERE day>=DATE(:1,:2,:3) and day<DATE(:4,:5,:6)", monday.year, monday.month, monday.day, sunday.year, sunday.month, sunday.day)
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
				actualComposits=[]
				for menuItem in menuItems:
					try:
						if menuItem.dish.category.key()==category.key() and menuItem.day==actualDay and menuItem.containingMenuItem == None:
							try:
								menuItem.orderedQuantity = int(userOrders[menuItem.key()])
								if menuItem.price == None:
									menuItem.price = 0
								orderedPrice[i] = orderedPrice[i] +  menuItem.price * int(userOrders[menuItem.key()])
								itemsInRows=itemsInRows+1
							except (KeyError, ValueError):
								menuItem.orderedQuantity = 0
							if menuItem.orderedQuantity > 0:
								actualMenuItems.append(menuItem)
					except ReferencePropertyResolveError:
						continue
				for composit in composits:
					try:
						if composit.category.key()==category.key() and composit.day==actualDay:
							try:
								composit.orderedQuantity = int(userOrders[composit.key()])
								if composit.price == None:
									composit.price = 0
								orderedPrice[i] = orderedPrice[i] +  composit.price * int(userOrders[composit.key()])
								itemsInRows=itemsInRows+1
							except (KeyError, ValueError, TypeError):
								composit.orderedQuantity = 0
							if composit.orderedQuantity > 0:
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
			'next':nextMonday,
			'actual':actualMonday,
			'addresses':user.addresses,
			'menu':menu
		}
		if (prevMonday == actualMonday) or (prevMonday > actualMonday):
			template_values['prev'] = prevMonday
		# A single dish with editable ingredient list
		template = jinja_environment.get_template('templates/reviewOrderedMenu.html')
		self.printPage(str(day), template.render(template_values), True)
	def post(self):
		# Get addresses and save them to the proper day
		for field in self.request.arguments():
			if (field[:8]=="address_"):
				day=datetime.datetime.strptime(field[8:], "%Y-%m-%d").date()
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
		actualOrder = self.session.get(ACTUAL_ORDER,{})
		orderDate=datetime.datetime.now()
		#Save order
		if (len(actualOrder) > 0):
			userOrder = UserOrder()
			userOrder.canceled = False
			userOrder.orderDate = orderDate
			userOrder.price = 0
			userKey = self.session.get(USER_KEY,None)
			user=None
			if (userKey != None):
				user = User.get(userKey)
				userOrder.user = user
			userOrder.put()
			addresses = user.addresses
			if addresses.count()==0:
				print "Cim nelkul nem lehet."
				return
			for orderKey in actualOrder.keys():
				try:
					if (int(actualOrder[orderKey]) != 0):
						orderItem = UserOrderItem()
						orderItem.userOrder = userOrder
						orderItem.user = userOrder.user
						item = db.get(orderKey)
						day=None
						if type(item) == MenuItem:
							day = item.day
							orderItem.orderedItem=item
						else:
							day = item.day
							orderItem.orderedComposit=item
						orderItem.day=day
						orderItem.itemCount = int(actualOrder[orderKey])
						daysAddress = user.deliveryAddresses.filter("day = ", day)
						if daysAddress.count() == 0:
							# Create new order address
							daysAddress=UserOrderAddress()
							daysAddress.day=day
							daysAddress.user=user
							daysAddress.address = addresses[addresses.count()-1]
							daysAddress.put()
						try:
							orderItem.price = item.price * int(actualOrder[orderKey])
						except TypeError:
							orderItem.price = 0
						userOrder.price = userOrder.price + orderItem.price
						orderItem.put()

				except ValueError, ReferencePropertyResolveError:
					continue
			userOrder.put()
			self.session[ACTUAL_ORDER]={}
			self.redirect("/personalMenu")
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



















