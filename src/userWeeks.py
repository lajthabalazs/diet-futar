#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
from user_management import isUserAdmin
from model import User
from google.appengine.api.datastore_errors import BadKeyError

#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class WeeksListPage(BaseHandler):
	def get(self):
		if not isUserAdmin(self):
			self.redirect("/")
			return
		userKey = self.request.get("userKey")
		if (userKey != None and userKey != ""):
			user = None
			try:
				user = User.get(userKey)
			except BadKeyError:
				pass
			if user != None:
				weeks = user.weeks
				orderedWeeks = sorted(weeks, key=lambda item:item.monday)
				template_values = {
					'user':user,
					'weeks':orderedWeeks
				}
				template = jinja_environment.get_template('templates/admin/userWeeksList.html')
				userName = ""
				if user.familyName!= None:
					userName = userName + user.familyName
				if user.familyName!= None and user.givenName!=None:
					userName = userName + " "
				if user.givenName!=None:
					userName = userName + user.givenName
				if len(userName) == 0:
					userName = "ISMERETLEN"
				self.printPage(userName + " rendel&eacute;sei", template.render(template_values), False, False)










