#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
from user_management import USER_KEY
from model import User

#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class ChristmasLunchPage(BaseHandler):
	def get(self):
		userKey = self.session.get(USER_KEY,None)
		template_values = {
		}
		if (userKey != None):
			user = User.get(userKey)
			if user != None:
				template_values['user'] = user

		template = jinja_environment.get_template('templates/christmasLunch.html')
		self.printPage("Kar&aacute;csonyi eb&eacute;d", template.render(template_values), True, True)
























