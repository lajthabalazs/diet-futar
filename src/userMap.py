#!/usr/bin/env python
import jinja2
import os

from base_handler import BaseHandler
from user_management import isUserDelivery, LOGIN_NEXT_PAGE_KEY
import time
#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class UserMapPage(BaseHandler):
	URL = '/userMap'
	def get(self):
		if not isUserDelivery(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		now = int(time.mktime(time.gmtime()))
		template_values = {
		}
		template = jinja_environment.get_template('templates/admin/userMap.html')
		self.printPage("Logs", template.render(template_values), False, False)