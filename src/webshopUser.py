#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler
from user_management import isUserLoggedIn, getUser
from model import WebshopOrderItem, WebshopItem
import datetime

#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class UserWebshopOrderListPage(BaseHandler):
	def get(self):
		if not isUserLoggedIn(self):
			self.redirect("/")
			return
		user = getUser(self)
		if (user!=None):
			orders = user.webshopOrders
			orderedOrders = sorted(orders, key=lambda order: order.orderDate, reverse=True)
			orders = []
			for order in orderedOrders:
				order.addressString = order.address.zipCode + " " + order.address.street + " " + order.address.streetNumber
				order.price = order.item.price * order.orderQuantity
				orders.append(order)
			template_values = {
				'orders':orders
			}
			template = jinja_environment.get_template('templates/webshop/userOrderList.html')
			self.printPage("Rendel&eacute;sek", template.render(template_values), True, True)
		else:
			print "Error, no logged in user"

class UserWebshopOrderDetailsPage(BaseHandler):
	def get(self):
		if not isUserLoggedIn(self):
			self.redirect("/")
			return
		orderKey = self.request.get('orderKey')
		if orderKey != None:
			order = WebshopOrderItem.get(orderKey)
			order.addressString = order.address.zipCode + " " + order.address.street + " " + order.address.streetNumber
			order.price = order.item.price * order.orderQuantity
			if order != None:
				formattedComments = []
				for i in range(0,len(order.comments)):
					formattedComments.append(
						{
							"comment":order.comments[i],
							"author":order.commentAuthors[i],
							"date":order.commentDates[i]
						}
					)
				order.formattedComments = formattedComments
				template_values = {
					'order':order
				}
				template = jinja_environment.get_template('templates/webshop/userOrderDetails.html')
				self.printPage("Rendel&eacute;s r&eacute;szletei", template.render(template_values), True, True)
				return
		self.printPage("Rendel&eacute;s r&eacute;szletei", "Missing parameter for user order", True, True)

class WebshopItemDetailsPage(BaseHandler):
	def get(self):
		if not isUserLoggedIn(self):
			self.redirect("/")
			return
		itemKey = self.request.get('itemKey')
		item = WebshopItem.get(itemKey)
		template_values = {
			'item':item
		}
		template = jinja_environment.get_template('templates/webshop/webshopItemDetails.html')
		self.printPage("Rendel&eacute;s r&eacute;szletei", template.render(template_values), True, True)

class UserWebshopPostMessagePage(BaseHandler):
	def post(self):
		if not isUserLoggedIn(self):
			self.redirect("/")
			return
		orderKey = self.request.get('orderKey')
		order = WebshopOrderItem.get(orderKey)
		comments = order.comments
		comments.append(self.request.get('message'))
		order.comments = comments
		authors = order.commentAuthors
		authors.append('&Eacute;n')
		order.commentAuthors = authors
		dates = order.commentDates
		dates.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		order.commentDates = dates
		order.put()
		self.redirect("/webshopUserOrder?orderKey=" + orderKey)























