#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler
from user_management import getUser, isUserAdmin, isUserLoggedIn
from model import WebshopItem, WebshopOrderItem, Address
import datetime

#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

CHRISTMAS_LUNCH_A = "CHRIS_A"
CHRISTMAS_LUNCH_B = "CHRIS_B"

class ChristmasLunchPage(BaseHandler):
	def get(self):
		template_values = {
		}
		user = getUser(self)
		if user != None:
			template_values['user'] = user
		template = jinja_environment.get_template('templates/webshop/christmasLunch.html')
		self.printPage("Kar&aacute;csonyi eb&eacute;d", template.render(template_values), True, True)
	def post(self):
		if not isUserLoggedIn(self):
			self.redirect("/")
			return
		user = getUser(self)
		aMenuQuantity = int(self.request.get('aMenu'))
		bMenuQuantity = int(self.request.get('aMenu'))
		addressKey = self.request.get('address')
		address = Address.get(addressKey)
		message = self.request.get('message') 
		if aMenuQuantity > 0:
			aMenuItems = WebshopItem.all().filter("code = ", CHRISTMAS_LUNCH_A)
			aMenuItem = None
			if aMenuItems.count() == 1:
				aMenuItem = aMenuItems.get()
			christmasOrder = WebshopOrderItem()
			christmasOrder.address = address
			christmasOrder.orderDate = datetime.datetime.now()
			christmasOrder.orderQuantity = aMenuQuantity
			christmasOrder.item = aMenuItem
			christmasOrder.user = user
			if message != None and message != "":
				christmasOrder.comments = [message]
				christmasOrder.commentAuthors = ['&Eacute;n']
				christmasOrder.commentDates = [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
			christmasOrder.put()
		if bMenuQuantity > 0:
			bMenuItems = WebshopItem.all().filter("code = ", CHRISTMAS_LUNCH_B)
			bMenuItem = None
			if bMenuItems.count() == 1:
				bMenuItem = bMenuItems.get()
			christmasOrder = WebshopOrderItem()
			christmasOrder.address = address
			christmasOrder.orderDate = datetime.datetime.now()
			christmasOrder.orderQuantity = bMenuQuantity
			christmasOrder.item = bMenuItem
			christmasOrder.user = user
			if message != None and message != "":
				christmasOrder.comments = [message]
				christmasOrder.commentAuthors = ['&Eacute;n']
				christmasOrder.commentDates = [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
			christmasOrder.put()
		self.redirect("/userOrderList")

class InitChristmasLunchPage(BaseHandler):
	def get(self):
		if (not isUserAdmin(self)):
			self.redirect("/")
			return
		aMenus = WebshopItem.all().filter("code = ", CHRISTMAS_LUNCH_A)
		if (aMenus.count() == 0):
			aMenu = WebshopItem()
			aMenu.code = CHRISTMAS_LUNCH_A
			aMenu.title = "Kar&aacute;csonyi eb&eacute;d - A"
			aMenu.price = 2300
			aMenu.shortDescription = "Szegedi hal&aacute;szl&eacute; harcsafil&eacute;vel, t&ouml;lt&ouml;tt k&aacute;poszta, bejgli"
			aMenu.description = "Szegedi hal&aacute;szl&eacute; harcsafil&eacute;vel, t&ouml;lt&ouml;tt k&aacute;poszta, bejgli"
			aMenu.tags = ["Kar&aacute;csony"]
			aMenu.put()
		bMenus = WebshopItem.all().filter("code = ", CHRISTMAS_LUNCH_B)
		if (bMenus.count() == 0):
			bMenu = WebshopItem()
			bMenu.code = CHRISTMAS_LUNCH_B
			bMenu.title = "Kar&aacute;csonyi eb&eacute;d - B"
			bMenu.price = 2600
			bMenu.shortDescription = "Szegedi hal&aacute;szl&eacute; harcsafil&eacute;vel, harcsapaprik&aacute;s t&uacute;r&oacute;scsusz&aacute;val, bejgli"
			bMenu.description = "Szegedi hal&aacute;szl&eacute; harcsafil&eacute;vel, harcsapaprik&aacute;s t&uacute;r&oacute;scsusz&aacute;val, bejgli"
			bMenu.tags = ["Kar&aacute;csony"]
			bMenu.put()
		self.printPage("Kar&aacute;csonyi eb&eacute;d", "Sikeres inicializalas.", True, True)





















