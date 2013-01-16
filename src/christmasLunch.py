#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler
from user_management import getUser, isUserAdmin, isUserLoggedIn,\
	LOGIN_NEXT_PAGE_KEY
from model import WebshopItem, WebshopOrderItem, Address
import datetime

#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

CHRISTMAS_LUNCH_A = "CHRIS_A"
CHRISTMAS_LUNCH_B = "CHRIS_B"
MAKOS_BEIGLI = "MAKOS_BEIGLI"
DIOS_BEIGLI = "DIOS_BEIGLI"

class ChristmasLunchPage(BaseHandler):
	URL = '/christmasLunch'
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
		bMenuQuantity = int(self.request.get('bMenu'))
		makosQuantity = int(self.request.get('makos'))
		diosQuantity = int(self.request.get('dios'))
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
		if makosQuantity > 0:
			makosItems = WebshopItem.all().filter("code = ", MAKOS_BEIGLI)
			makosItem = None
			if makosItems.count() == 1:
				makosItem = makosItems.get()
			christmasOrder = WebshopOrderItem()
			christmasOrder.address = address
			christmasOrder.orderDate = datetime.datetime.now()
			christmasOrder.orderQuantity = makosQuantity
			christmasOrder.item = makosItem
			christmasOrder.user = user
			if message != None and message != "":
				christmasOrder.comments = [message]
				christmasOrder.commentAuthors = ['&Eacute;n']
				christmasOrder.commentDates = [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
			christmasOrder.put()
		if diosQuantity > 0:
			diosItems = WebshopItem.all().filter("code = ", DIOS_BEIGLI)
			diosItem = None
			if diosItems.count() == 1:
				diosItem = diosItems.get()
			christmasOrder = WebshopOrderItem()
			christmasOrder.address = address
			christmasOrder.orderDate = datetime.datetime.now()
			christmasOrder.orderQuantity = diosQuantity
			christmasOrder.item = diosItem
			christmasOrder.user = user
			if message != None and message != "":
				christmasOrder.comments = [message]
				christmasOrder.commentAuthors = ['&Eacute;n']
				christmasOrder.commentDates = [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
			christmasOrder.put()
		self.redirect("/userOrderList")

class InitChristmasLunchPage(BaseHandler):
	URL = '/initChristmasLunch'
	def get(self):
		if (not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
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

		makoss = WebshopItem.all().filter("code = ", MAKOS_BEIGLI)
		if (makoss.count() == 0):
			makos = WebshopItem()
			makos.code = MAKOS_BEIGLI
			makos.title = "M&aacute;kos beigli, 300g"
			makos.price = 1200
			makos.shortDescription = "Glut&eacute;nmentes m&aacute;kos beigli"
			makos.description = "Glut&eacute;nmentes m&aacute;kos beigli"
			makos.tags = ["Kar&aacute;csony", "Beigli"]
			makos.put()

		dioss = WebshopItem.all().filter("code = ", DIOS_BEIGLI)
		if (dioss.count() == 0):
			dios = WebshopItem()
			dios.code = DIOS_BEIGLI
			dios.title = "Di&oacute;s beigli, 300g"
			dios.price = 1500
			dios.shortDescription = "Glut&eacute;nmentes bejgli, val&oacute;di di&oacute;val"
			dios.description = "Glut&eacute;nmentes bejgli, val&oacute;di di&oacute;val"
			dios.tags = ["Kar&aacute;csony", "Beigli"]
			dios.put()
		
		self.printPage("Kar&aacute;csonyi eb&eacute;d", "Sikeres inicializalas.", True, True)





















