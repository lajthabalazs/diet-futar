'''
Created on Aug 11, 2012

@author: lajthabalazs
'''

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
from model import User, Address, Role
from user_management import LOGIN_ERROR_KEY, REGISTRATION_ERROR_EXISTING_USER,\
	REGISTRATION_ERROR_PASSWORD_DOESNT_MATCH, USER_KEY, LOGIN_NEXT_PAGE_KEY,\
	REGISTRATION_ERROR_KEY, clearRegistrationError, clearLoginError, USER,\
	REGISTRATION_ERROR_USER_NAME_NOT_FILLED, isUserLoggedIn, EMAIL_KEY
from random import Random
from xmlrpclib import datetime
from google.appengine.api import mail

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

districts=["I","II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII","XXIII", "XXIV"]

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
			self.session[EMAIL_KEY]=email
			self.session[LOGIN_ERROR_KEY]="USER"
			self.redirect(clearNextPage(self))
		elif (users[0].password != password):
			self.session[EMAIL_KEY]=email
			self.session[LOGIN_ERROR_KEY] = "PASS"
			self.redirect(clearNextPage(self))
		elif users[0].activated != True:
			self.session[EMAIL_KEY]=email
			self.session[LOGIN_ERROR_KEY] = "ACTIVATE"
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

class ForgotPassword(BaseHandler):
	def get(self):
		email = self.session.get(EMAIL_KEY)
		users = User.gql('WHERE email = :1', email)
		template_params={
		}
		if (users.count(1) == 1):
			template_params[EMAIL_KEY] = email
		template = jinja_environment.get_template('templates/changePass.html')
		self.printPage("Uj jelszo", template.render(template_params), True, True)
	def post(self):
		email = self.session.get(EMAIL_KEY)
		users = User.gql('WHERE email = :1', email)
		template_params={
		}
		if (users.count(1) == 1):
			word = ''
			random = Random()
			for i in range(1,8):
				word += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
			user = users.get()
			user.password = word
			# TODO send mail
			template_values = {
				"password":word
			}
			messageTemplate = jinja_environment.get_template('templates/changePassMail.html')
			message = mail.EmailMessage(sender="Diet Futar <dietfutar@dietfutar.hu>")
			message.subject="Diet-futar, uj jelszo"
			message.to = email
			message.body = messageTemplate.render(template_values)
			message.send()
			user.put()
			template_params[EMAIL_KEY] = email
		template = jinja_environment.get_template('templates/changePassSuccess.html')
		self.printPage("Uj jelszo", template.render(template_params), True, True)
		
class RegisterPage(BaseHandler):
	def get(self):
		refererKey = self.request.get('refererKey')
		template_params={
			REGISTRATION_ERROR_KEY:self.session.get(REGISTRATION_ERROR_KEY,None),
			USER:self.session.get(USER, None)
		}
		if refererKey != None and refererKey != "":
			template_params['referer'] = User.get(refererKey)
		clearRegistrationError(self)
		template = jinja_environment.get_template('templates/register.html')
		self.printPage("Regisztracio", template.render(template_params), True, True)
		#self.response.out.write(jinja_environment.get_template('templates/header.html').render() + template.render())
	def post(self):
		referer = None
		refererKey = self.request.get('refererKey')
		if refererKey != None and refererKey != "":
			referer = User.get(refererKey)
		email = self.request.get('email')
		phoneNumber = self.request.get('phoneNumber')
		password = self.request.get('password')
		passwordCheck = self.request.get('passwordCheck')
		familyName= self.request.get('familyName')
		givenName= self.request.get('givenName')
		user = {}
		user["email"]= email
		user["familyName"]=familyName
		user["givenName"]=givenName
		user["phoneNumber"]=phoneNumber
		users = User.gql('WHERE email = :1', email)
		# Check if roles are set up properly
#		roles=Role.all()
#		if roles.count() == 0:
#			role = Role()
#			role.name=ROLE_ADMIN
#			role.put()
#			role = Role()
#			role.name=ROLE_DELIVERY_GUY
#			role.put()
#			role = Role()
#			role.name=ROLE_COOK
#			role.put()
		refererUrlPart = ""
		if referer != None:
			refererUrlPart = "?refererKey=" + str(referer.key())
		self.session[USER]=user
		if (users.count(1)>0):
			self.session[REGISTRATION_ERROR_KEY]=REGISTRATION_ERROR_EXISTING_USER
			self.redirect('/registration' + refererUrlPart)
		elif (passwordCheck != password):
			self.session[REGISTRATION_ERROR_KEY] = REGISTRATION_ERROR_PASSWORD_DOESNT_MATCH
			self.redirect('/registration' + refererUrlPart)
		elif familyName==None or familyName=="" or givenName==None or givenName=="":
			self.session[REGISTRATION_ERROR_KEY] = REGISTRATION_ERROR_USER_NAME_NOT_FILLED
			self.redirect('/registration' + refererUrlPart)
		else:
			#Everything went ok, create the user and log him in
			user = User()
			user.email = email
			user.familyName=familyName
			user.givenName=givenName
			user.password = password
			user.phoneNumber=phoneNumber
			user.activated = False
			user.registrationDate=datetime.date.today()
			user.referer = referer
			word = ''
			random = Random()
			for i in range(1,32):
				word += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
			user.activationCode = word
			user.put()
			template_values = {
				'email':email,
				'activationCode':word,
				'user':user
			}
			messageTemplate = jinja_environment.get_template('templates/activation_code.html')
			message = mail.EmailMessage(sender="Diet Futar <dietfutar@dietfutar.hu>")
			message.subject="Diet-futar, sikeres regisztracio"
			message.to = email
			message.body = messageTemplate.render(template_values)
			message.send()
			self.redirect("/activationPending")

class ActivationPendingPage (BaseHandler):
	def get(self):
			template = jinja_environment.get_template('templates/activation_pending.html')
			self.printPage("Aktivacio", template.render(), True)
	
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
		if(not isUserLoggedIn(self)):
			self.redirect("/registration")
			return
		clearLoginError(self)
		userKey=self.session.get(USER_KEY,None)
		user = None
		if (userKey != None):
			user = db.get(userKey)
		if user == None:
			self.redirect("/registration")
			return
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
				self.session[LOGIN_ERROR_KEY] = "Hibas jelsz&oacute;"
		self.redirect("/profile")


class UserProfilePage (BaseHandler):
	def get(self):
		if(not isUserLoggedIn(self)):
			self.redirect("/registration")
			return
		userKey=self.session.get(USER_KEY,None)
		if (userKey != None):
			user = db.get(userKey)
			user.password = "__________"
			user.role = None
			template_values = {
				'user': user,
				'districts':districts,
				LOGIN_ERROR_KEY:self.session.get(LOGIN_ERROR_KEY,0)
			}
			template = jinja_environment.get_template('templates/profile_new.html')
			self.printPage("Profil", template.render(template_values), False, True)
	def post(self):
		if(not isUserLoggedIn(self)):
			self.redirect("/registration")
			return
		userKey=self.session.get(USER_KEY,None)
		if (userKey != None):
			user = db.get(userKey)
			if user != None:
				user.familyName = self.request.get('familyName')
				user.givenName = self.request.get('givenName')
				user.phoneNumber = self.request.get('phoneNumber')
				user.put()
				user.password = "__________"
				user.role = None
				template_values = {
					'user': user,
					'districts':districts
				}
				template = jinja_environment.get_template('templates/profile_new.html')
				self.printPage("Profil", template.render(template_values), False, True)
			else:
				self.redirect("/registration")
		else:
			self.redirect("/registration")

class AddressPage (BaseHandler):
	def post(self):
		if(not isUserLoggedIn(self)):
			self.redirect("/registration")
			return
		user = None
		userKey=self.session.get(USER_KEY,None)
		if (userKey != None):
			user = db.get(userKey)
		else:
			self.redirect("/profile")
			return
		addressKey = self.request.get("addressKey")
		address = None
		if addressKey != None and addressKey != "":
			address = Address.get(addressKey)
		if address == None:
			address = Address()
		address.user = user
		address.billingName = self.request.get("billingName")
		address.district = self.request.get("district")
		address.zipCode = self.request.get("zipCode")
		address.street = self.request.get("street")
		address.streetNumber = self.request.get("streetNumber")
		address.put()
		self.redirect("/profile")

class Referals (BaseHandler):
	def get(self):
		if(not isUserLoggedIn(self)):
			self.redirect("/registration")
			return
		user = None
		userKey=self.session.get(USER_KEY,None)
		if (userKey != None):
			user = db.get(userKey)
		referred = sorted(user.referred, key=lambda user:user.registrationDate)
		template_values = {
			'referred' : referred
		}
		template = jinja_environment.get_template('templates/referred.html')
		self.printPage("Profil", template.render(template_values), False, True)
		






