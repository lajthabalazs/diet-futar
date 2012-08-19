#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler, PAGE_TITLE
import datetime
from model import Dish
#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class DayMenuPage(BaseHandler):
	def get(self):
		day=datetime.date.today()
		if ((self.request.get('day') != None) and (self.request.get('day') != "")):
			day=datetime.date.fromtimestamp(self.request.get('day'))
		#menuItems=MenuItem.gql("WHERE day=")
		# A single dish with editable ingredient list
		dishes=Dish.gql("ORDER BY title")
		template_values = {
			'day': day,
			'availableDishes':dishes
		}
		template = jinja_environment.get_template('templates/dayMenu.html')
		self.printPage(PAGE_TITLE + " - " + str(day), template.render(template_values), True, True)