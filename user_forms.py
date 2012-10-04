'''
Created on Aug 11, 2012

@author: lajthabalazs
'''

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
from model import User, Address
from user_management import LOGIN_ERROR_KEY, LOGIN_ERROR_UNKNOWN_USER,\
	REGISTRATION_ERROR_EXISTING_USER,\
	REGISTRATION_ERROR_PASSWORD_DOESNT_MATCH, USER_KEY, LOGIN_NEXT_PAGE_KEY,\
	LOGIN_ERROR_WRONG_PASSWORD, REGISTRATION_ERROR_KEY, clearRegistrationError,\
	isUserAdmin, clearLoginError, LOGIN_ERROR_NOT_ACTIVATED
from random import Random
from xmlrpclib import datetime

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def clearNextPage(handler):
	nextPage="/"
	if (LOGIN_NEXT_PAGE_KEY in handler.session):
		nextPage=handler.session[LOGIN_NEXT_PAGE_KEY]
		del handler.session[LOGIN_NEXT_PAGE_KEY]
	return nextPage

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
			template = jinja_environment.get_template('templates/login.html')
			self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render(template_values))
	def post(self):
		#Check login
		email = self.request.get('email')
		password = self.request.get('password')
		users= User.gql('WHERE email = :1', email)
		if (users.count(1)==0):
			self.session[LOGIN_ERROR_KEY]=LOGIN_ERROR_UNKNOWN_USER
			self.redirect(clearNextPage(self))
		elif (users[0].password != password):
			self.session[LOGIN_ERROR_KEY] = LOGIN_ERROR_WRONG_PASSWORD
			self.redirect(clearNextPage(self))
		elif users[0].activated != True:
			self.session[LOGIN_ERROR_KEY] = LOGIN_ERROR_NOT_ACTIVATED
			self.redirect(clearNextPage(self))
		else:
			#Log the user in
			self.session[USER_KEY]=str(users[0].key())
			self.redirect(clearNextPage(self))

class LogoutPage(BaseHandler):
	def get(self):
		if (USER_KEY in self.session):
			del self.session[USER_KEY]
		self.redirect(clearNextPage(self))
		
class RegisterPage(BaseHandler):
	def get(self):
		template_params={
			REGISTRATION_ERROR_KEY:self.session.get(REGISTRATION_ERROR_KEY,None)
		}
		clearRegistrationError(self)
		template = jinja_environment.get_template('templates/register.html')
		self.printPage("Regisztracio", template.render(template_params), True, True)
		#self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render())
	def post(self):
		email = self.request.get('email')
		password = self.request.get('password')
		passwordCheck = self.request.get('passwordCheck')
		users = User.gql('WHERE email = :1', email)
		if (users.count(1)>0):
			self.session[REGISTRATION_ERROR_KEY]=REGISTRATION_ERROR_EXISTING_USER
			self.redirect('/registration')
		elif (passwordCheck != password):
			self.session[REGISTRATION_ERROR_KEY] = REGISTRATION_ERROR_PASSWORD_DOESNT_MATCH
			self.redirect('/registration')
		else:
			#Everything went ok, create the user and log him in
			user = User()
			user.email = email
			user.password = password
			user.activated = False
			user.registrationDate=datetime.date.today()
			word = ''
			random = Random()
			for i in range(1,32):
				word += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
			user.activationCode = word
			user.put()
			#TODO Send activation mail
			template_values = {
				'email':email,
				'activationCode':word
			}
			template = jinja_environment.get_template('templates/activation_code.html')
			self.printPage("Aktivacio", template.render(template_values), True)
			
			#self.session[USER_KEY]=str(user.key())
			#self.redirect(clearNextPage(self))

class ActivatePage (BaseHandler):
	def get(self):
		# Finds user with given email and activation code and activates it
		email = self.request.get('email')
		activationCode = self.request.get('activationCode')
		users = User.gql('WHERE email = :1', email)
		activationResult = -1
		if (users.count(1) > 0):
			user = users[0]
			if (user.activationCode == activationCode):
				user.activated = True
				user.put()
				self.session[USER_KEY]=str(users[0].key())
				activationResult = 0
			else:
				activationResult = 2
		else:
			activationResult = 1
		template_values = {
			'activationResult' : activationResult
		}
		template = jinja_environment.get_template('templates/activation.html')
		self.printPage("Aktivacio", template.render(template_values), True)

class ChangePasswordPage (BaseHandler):
	def post(self):
		clearLoginError(self)
		if(not isUserAdmin(self)):
			self.redirect("/registration")
		userKey=self.session.get(USER_KEY,None)
		user = None
		if (userKey != None):
			user = db.get(userKey)
		if user == None:
			self.redirect("/registration")
		else:
			if user.password == self.request.get("oldPassword"):
				passwd1 = self.request.get("newPassword")
				passwd2 = self.request.get("passwordCheck")
				if passwd1 == passwd2:
					user.password = passwd1
					user.put()
				else:
					self.session[LOGIN_ERROR_KEY] = REGISTRATION_ERROR_PASSWORD_DOESNT_MATCH
			else:
				self.session[LOGIN_ERROR_KEY] = LOGIN_ERROR_WRONG_PASSWORD
		self.redirect("/profile")


class UserProfilePage (BaseHandler):
	def get(self):
		if(not isUserAdmin(self)):
			self.redirect("/registration")
		userKey=self.session.get(USER_KEY,None)
		if (userKey != None):
			user = db.get(userKey)
			user.password = "__________"
			user.role = None
			template_values = {
				'user': user,
				LOGIN_ERROR_KEY:self.session.get(LOGIN_ERROR_KEY,0)
			}
			template = jinja_environment.get_template('templates/profile_new.html')
			self.printPage("Profil", template.render(template_values), False, True)
	def post(self):
		if(not isUserAdmin(self)):
			self.redirect("/registration")
		userKey=self.session.get(USER_KEY,None)
		if (userKey != None):
			user = db.get(userKey)
			if user != None:
				user.familyName = self.request.get('familyName')
				user.givenName = self.request.get('givenName')
				user.put()
				user.password = "__________"
				user.role = None
				template_values = {
					'user': user
				}
				template = jinja_environment.get_template('templates/profile_new.html')
				self.printPage("Profil", template.render(template_values), False, True)
			else:
				self.redirect("/registration")
		else:
			self.redirect("/registration")

class AddressPage (BaseHandler):
	def post(self):
		user = None
		if(not isUserAdmin(self)):
			self.redirect("/registration")
		userKey=self.session.get(USER_KEY,None)
		if (userKey != None):
			user = db.get(userKey)
		else:
			self.redirect("/profile")
		addressKey = self.request.get("addressKey")
		address = None
		if addressKey != None and addressKey != "":
			address = Address.get(addressKey)
		if address == None:
			address = Address()
		address.user = user
		address.billingName = self.request.get("billingName")
		address.district = self.request.get("district")
		address.phoneNumber = self.request.get("phoneNumber")
		address.zipCode = self.request.get("zipCode")
		address.street = self.request.get("street")
		address.streetNumber = self.request.get("streetNumber")
		address.put()
		self.redirect("/profile")







