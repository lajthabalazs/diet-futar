#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
from user_management import USER_KEY, isUserAdmin
from model import User, WebshopItem, WebshopOrderItem

#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class ItemListPage(BaseHandler):
	def get(self):
		if not isUserAdmin(self):
			self.redirect("/")
			return
		items = WebshopItem.all().order('title')
		template_values = {
			'items':items
		}

		template = jinja_environment.get_template('templates/webshop/itemList.html')
		self.printPage("Term&eacute;kek", template.render(template_values), True, True)

class UsersOrdersPage(BaseHandler):
	def get(self):
		if not isUserAdmin(self):
			self.redirect("/")
			return
		orders = WebshopOrderItem.all().order('orderDate')
		template_values = {
			'orders':orders
		}

		template = jinja_environment.get_template('templates/webshop/usersOrders.html')
		self.printPage("Rendel&eacute;sek", template.render(template_values), True, True)























