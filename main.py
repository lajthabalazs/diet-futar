#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler

#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(BaseHandler):
	def get(self):
		template = jinja_environment.get_template('templates/main.html')
		self.printPage(None, template.render(), True, True)
