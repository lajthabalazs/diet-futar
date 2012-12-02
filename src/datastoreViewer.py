#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db
from model import Dish, IngredientListItem, DishCategory, MenuItem,\
	UserOrderAddress, UserOrderItem, UserWeekOrder

from base_handler import BaseHandler, getMonday
from user_management import isUserCook, isUserAdmin
from keys import DISH_CATEGORY_KEY
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
from cache_dish import getDish, deleteDish, modifyDish, addDish
from cache_dish_category import getDishCategories
from cache_ingredient import getIngredients

#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def getUpdatedList(items, quantity, key):
	newItems = []
	itemFound = False
	for item in items:
		parts = item.split(" ")
		itemQuantity = int(parts[0])
		itemKey = parts[1]
		if itemKey == str(key):
			itemQuantity = itemQuantity + quantity
			newItem = str(itemQuantity) + " " + str(key)
			newItems.append(newItem)
		else:
			newItems.append(item)
	if not itemFound:
		newItem = str(quantity) + " " + str(key)
		newItems.append(newItem)
	return newItems

class ListMenuItems(BaseHandler):
	def get(self):
		if not isUserAdmin(self):
			self.redirect("/")
			return
		items = MenuItem.all()
		flatItems = []
		for item in items:
			flatItem = {}
			flatItem['key'] = str(item.key())
			flatItem['day'] = str(item.day)
			try:
				flatItem['title'] = item.dish.title
			except:
				flatItem['title'] = "error " + str(item.key())
			try:
				flatItem['categoryName'] = item.dish.category.name
			except:
				flatItem['categoryName'] = "error " + str(item.key())
			flatItems.append(flatItem)
		template_values = {
			'items':flatItems
		}
		template = jinja_environment.get_template('templates/listMenuItems.html')
		self.printPage("MenuItems", template.render(template_values), False, False)

class ListOrderAddresses(BaseHandler):
	def get(self):
		if not isUserAdmin(self):
			self.redirect("/")
			return
		items = UserOrderAddress.all().order("day")
		flatItems = []
		for item in items:
			flatItem = {}
			flatItem['key'] = str(item.key())
			flatItem['day'] = str(item.day)
			try:
				flatItem['userFamily'] = item.user.familyName
			except:
				flatItem['userFamily'] = "error"
			try:
				flatItem['userGiven'] = item.user.givenName
			except:
				flatItem['userGiven'] = "error"
			try:
				flatItem['addressZip'] = item.address.zipCode
			except:
				flatItem['addressZip'] = "error"
			try:
				flatItem['addressStreet'] = item.address.street
			except:
				flatItem['addressStreet'] = "error"
			try:
				flatItem['addressStreetNumber'] = item.address.streetNumber
			except:
				flatItem['addressStreetNumber'] = "error"
				orderedItems = item.user.orderedItems.filter("day = ", item.day)
				flatOrderItems = []
				for orderedItem in orderedItems:
					try:
						flatOrderedItem = {}
						flatOrderedItem['isComposit'] = orderedItem.isComposit
						flatOrderedItem['itemCount'] = orderedItem.itemCount
					except:
						flatOrderedItem['isComposit'] = "error"
						flatOrderedItem['itemCount'] = "error"
					flatOrderItems.append(flatOrderedItem)
				flatItem['orderedItems'] = flatOrderItems
			flatItems.append(flatItem)
		template_values = {
			'items':flatItems
		}
		template = jinja_environment.get_template('templates/listAddresses.html')
		self.printPage("MenuItems", template.render(template_values), False, False)
	def post(self):
		if not isUserAdmin(self):
			self.redirect("/")
			return
		addresses = UserOrderAddress.all()
		for address in addresses:
			monday = getMonday(address.day)
			weeks = address.user.weeks.filter("monday = ", monday)
			if weeks.count() > 0:
				week = weeks.get()
			else:
				week = UserWeekOrder()
				week.user = address.user
				week.monday = monday
			if (address.day.weekday() == 0):
				week.mondayAddress = address.address
			elif (address.day.weekday() == 1):
				week.tuesdayAddress = address.address
			elif (address.day.weekday() == 2):
				week.wednesdayAddress = address.address
			elif (address.day.weekday() == 3):
				week.thursdayAddress = address.address
			elif (address.day.weekday() == 4):
				week.fridayAddress = address.address
			elif (address.day.weekday() == 5):
				week.saturdayAddress = address.address
			elif (address.day.weekday() == 6):
				week.sundayAddress = address.address
			week.put()
		self.redirect("/listAddresses")

class ListOrders(BaseHandler):
	def get(self):
		if not isUserAdmin(self):
			self.redirect("/")
			return
		items = UserOrderItem.all()
		flatItems = []
		item = UserOrderItem()
		for item in items:
			flatItem = {}
			flatItem['key'] = str(item.key())
			flatItem['userKey'] = str(item.user.key())
			flatItem['userFamily'] = item.user.familyName
			flatItem['userGiven'] = item.user.givenName
			flatItem['day'] = str(item.day)
			flatItem['itemCount'] = item.itemCount
			monday = getMonday(item.day)
			weeks = item.user.weeks.filter("monday = ", monday)
			flatItem['hasWeek'] = (weeks.count() > 0)
			if (item.orderedComposit != None):
				flatItem['orderedComposit'] = str(item.orderedComposit.key())
			if (item.orderedItem != None):
				flatItem['orderedMenuItem'] = str(item.orderedItem.key())
			flatItems.append(flatItem)
		template_values = {
			'items':flatItems
		}
		template = jinja_environment.get_template('templates/listOrders.html')
		self.printPage("MenuItems", template.render(template_values), False, False)
	def post(self):
		if not isUserAdmin(self):
			self.redirect("/")
			return
		items = UserOrderItem.all()
		for item in items:
			monday = getMonday(item.day)
			weeks = item.user.weeks.filter("monday = ", monday)
			if weeks.count() > 0:
				week = weeks.get()
			else:
				week = UserWeekOrder()
				week.user = item.user
				week.monday = monday
			if (item.orderedComposit != None):
				week.orderedComposits = getUpdatedList(week.orderedComposits, item.itemCount, item.orderedComposit.key())
			if (item.orderedItem != None):
				week.orderedMenuItems = getUpdatedList(week.orderedMenuItems, item.itemCount, item.orderedItem.key())
			week.put()
		self.redirect("/listOrders")


























