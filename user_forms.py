'''
Created on Aug 11, 2012

@author: lajthabalazs
'''

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
from model import User
from user_management import LOGIN_ERROR_KEY, LOGIN_ERROR_UNKNOWN_USER,\
	REGISTRATION_ERROR_KEY, REGISTRATION_ERROR_EXISTING_USER,\
	REGISTRATION_ERROR_PASSWORD_DOESNT_MATCH, USER_KEY

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))



class LoginPage(BaseHandler):
	def get(self):
		userKey = self.session.get(USER_KEY,None)
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
				LOGIN_ERROR_KEY:self.session.get(LOGIN_ERROR_KEY,0)
			}
			if (LOGIN_ERROR_KEY in self.session):
				del self.session[LOGIN_ERROR_KEY]
			template = jinja_environment.get_template('templates/login.html')
			self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render(template_values))
	def post(self):
		#Check login
		userName = self.request.get('userName')
		password = self.request.get('password')
		users= User.gql('WHERE userName = :1', userName)
		if (users.count(1)==0):
			self.session[LOGIN_ERROR_KEY]=LOGIN_ERROR_UNKNOWN_USER
			self.redirect('/login')
		elif (users[0].password != password):
			self.request[LOGIN_ERROR_KEY] = LOGIN_ERROR_UNKNOWN_USER
			self.redirect('/login')
		else:
			#Log the user in
			self.session[USER_KEY]=str(users[0].key())
			self.redirect("/login")

class LogoutPage(BaseHandler):
	def get(self):
		if (USER_KEY in self.session):
			del self.session[USER_KEY]
		self.redirect("/login")	
class RegisterPage(BaseHandler):
	def get(self):
		template = jinja_environment.get_template('templates/register.html')
		self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render())
	def post(self):
		userName = self.request.get('userName')
		password = self.request.get('password')
		passwordCheck = self.request.get('passwordCheck')
		users = User.gql('WHERE userName = :1', userName)
		if (users.count(1)>0):
			self.session[REGISTRATION_ERROR_KEY]=REGISTRATION_ERROR_EXISTING_USER
			self.redirect('/register')
		elif (passwordCheck != password):
			self.request[REGISTRATION_ERROR_KEY] = REGISTRATION_ERROR_PASSWORD_DOESNT_MATCH
			self.redirect('/register')
		else:
			#Everything went ok, create the user and log him in
			user = User()
			user.userName = userName
			user.password = password
			user.put()
			self.session[USER_KEY]=str(user.key())
			self.redirect("/login")










