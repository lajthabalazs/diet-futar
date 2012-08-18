#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db
from model import Dish, Ingredient, IngredientListItem

from base_handler import BaseHandler
#from user_management import getUserBox

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(BaseHandler):
	def get(self):
		self.printPage("Kezdooldal", "Hello!", True)