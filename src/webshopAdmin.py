#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler
from user_management import isUserAdmin, LOGIN_NEXT_PAGE_KEY
from model import User, WebshopItem, WebshopOrderItem

#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class ItemListPage(BaseHandler):
	URL = '/itemList'
	def get(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		items = WebshopItem.all().order('title')
		template_values = {
			'items':items
		}

		template = jinja_environment.get_template('templates/webshop/itemList.html')
		self.printPage("Term&eacute;kek", template.render(template_values), True, True)

class UsersOrdersPage(BaseHandler):
	URL = '/usersOrders'
	def get(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		userKey = self.request.get('userKey')
		orders = None
		user = None
		if userKey != None and userKey != '':
			user = User.get(userKey)
			if user != None:
				orders = user.webshopOrders
		if orders == None:
			orders = WebshopOrderItem.all().order("-orderDate")
		orderedOrders = sorted(orders, key=lambda order: order.orderDate, reverse=True)
		orders = []
		for order in orderedOrders:
			order.addressString = order.address.zipNumCode + " " + order.address.street + " " + order.address.streetNumber
			order.price = order.item.price * order.orderQuantity
			orders.append(order)
		template_values = {
			'orders':orders
		}
		if user != None:
			template_values['user'] = user
		template = jinja_environment.get_template('templates/webshop/usersOrders.html')
		self.printPage("Rendel&eacute;sek", template.render(template_values), True, True)























