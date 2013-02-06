#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler, timeZone
from model import User
from user_management import isUserAdmin, LOGIN_NEXT_PAGE_KEY
from xmlrpclib import datetime
from timeit import itertools

ACTUAL_ORDER="actualOrder"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class CRMMainPage(BaseHandler):
	URL = '/crmMainPage'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		template = jinja_environment.get_template('templates/crm/crmMainPage.html')
		self.printPage("Felhasznalok", template.render(), False, False)

class CRMLastOrders(BaseHandler):
	URL = '/crmLastOrders'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		today = datetime.datetime.now(timeZone)
		twoWeeksAgo = today + datetime.timedelta(days = - 14)
		unseenUsers = User.all().filter("lastOrder < ", twoWeeksAgo)
		unseenUsersOrdered = sorted(unseenUsers, key=lambda user:user.lastOrder)

		taskedUsers = User.all().filter("taskList >= ", None)
		
		template_values={
			'users': itertools.chain(taskedUsers, unseenUsersOrdered),
		}
		template = jinja_environment.get_template('templates/crm/crmTaskList.html')
		self.printPage("Felhasznalok", template.render(template_values), False, False)

class CRMInitUsers(BaseHandler):
	URL = '/crmInitUsers'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		users = User.all()
		for user in users:
			monday = None
			week = user.weeks.order("-monday").get()
			if (week != None):
				monday = week.monday
			user.lastOrder = monday
			user.lastOrderFlag = True
			user.put()
		self.redirect(CRMLastOrders.URL)

class CRMUserDetails(BaseHandler):
	URL = '/crmUserDetails'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return








