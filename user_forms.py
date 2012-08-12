'''
Created on Aug 11, 2012

@author: lajthabalazs
'''

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
from model import User

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))



class Login(BaseHandler):
	def get(self):
		userKey = self.session.get('userKey',None)
		if (userKey != None):
		#If session has a user key, than return logged in
			user = db.get(userKey)
			template_values = {
				'user': user
			}
			template = jinja_environment.get_template('templates/loggedIn.html')
			self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render(template_values))
		else:
			#Show login form
			template_values = {
				'error_code':self.session.get('error_code',0)
			}
			if ('error_code' in self.session):
				del self.session['error_code']
			template = jinja_environment.get_template('templates/login.html')
			self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render(template_values))
	def post(self):
		#Check login
		userName = self.request.get('userName')
		password = self.request.get('password')
		user = User.gql('WHERE userName = :1', userName)
		if (user.count(1)==0):
			self.session["error_code"]=1
			self.redirect('/login')
		elif (user.password != password):
			self.request['error_code'] = 2
			self.redirect('/login')














