#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
from model import Wish
from user_management import isUserAdmin, LOGIN_NEXT_PAGE_KEY

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class WishPage(BaseHandler):
	URL = '/wish'
	def post(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
		if ((self.request.get('wishKey') != None) and (self.request.get('wishKey') != "")):
		#Modification of basic data
			wish = db.get(self.request.get('wishKey'))
			wish.title = self.request.get('title')
			wish.description = self.request.get('description')
			wish.put()
			self.redirect('/wish?wishKey=%s' % self.request.get('wishKey'))
		else:
			wish = Wish()
			wish.title = self.request.get('title')
			wish.description = self.request.get('description')
			wish.put()
			self.redirect('/wish?wishKey=%s' % wish.key())
	def get(self):
		if(not isUserAdmin(self)):
			self.redirect("/")
		if ((self.request.get('wishKey') != None) and (self.request.get('wishKey') != "")):
		# A single wish with editable ingredient list
			wish = db.get(self.request.get('wishKey'))
			template_values = {
				'wish': wish,
			}
			template = jinja_environment.get_template('templates/wish.html')
			self.printPage(wish.title, template.render(template_values), False, False)
		else:
		# All the wishes
			wishes = Wish.gql("ORDER BY title")
			template_values = {
			  'wishes': wishes,
			}
			template = jinja_environment.get_template('templates/wish_list.html')
			self.printPage("Fejlesztesi kivansagok", template.render(template_values), False, False)

class DeleteWishPage(BaseHandler):
	URL = '/deleteWish'
	def post(self):
		if(not isUserAdmin(self)):
			self.redirect("/")
		wish = db.get(self.request.get('wishKey'))
		wish.delete()
		self.redirect('/wish')
