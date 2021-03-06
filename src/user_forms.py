'''
Created on Aug 11, 2012

@author: lajthabalazs
'''

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler, timeZone
from model import User, Address
from user_management import LOGIN_ERROR_KEY, REGISTRATION_ERROR_EXISTING_USER,\
	REGISTRATION_ERROR_PASSWORD_DOESNT_MATCH, USER_KEY, LOGIN_NEXT_PAGE_KEY,\
	REGISTRATION_ERROR_KEY, clearRegistrationError, clearLoginError, USER,\
	REGISTRATION_ERROR_USER_NAME_NOT_FILLED, isUserLoggedIn, EMAIL_KEY
from random import Random
from xmlrpclib import datetime
from google.appengine.api import mail
import hashlib
from cacheWeek import updateUser

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def clearNextPage(handler):
	nextPage="/"
	if (LOGIN_NEXT_PAGE_KEY in handler.session):
		nextPage=handler.session[LOGIN_NEXT_PAGE_KEY]
		del handler.session[LOGIN_NEXT_PAGE_KEY]
	return nextPage

class LoginPage(BaseHandler):
	URL = '/login'
	def post(self):
		#Check login
		email = self.request.get('email')
		password = self.request.get('password')
		m = hashlib.md5()
		encodedString = password.encode('ascii', errors='replace')
		m.update(encodedString)
		passwordHash = str(m.hexdigest())
		users= User.gql('WHERE email = :1', email)
		if (users.count(1)==0):
			self.session[EMAIL_KEY]=email
			self.session[LOGIN_ERROR_KEY]="USER"
			self.redirect(clearNextPage(self))
		elif (users[0].passwordHash != passwordHash): #
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
	URL = '/logout'
	def get(self):
		if (USER_KEY in self.session):
			del self.session[USER_KEY]
		self.redirect(clearNextPage(self))

class ForgotPassword(BaseHandler):
	URL = '/forgotPassword'
	def get(self):
		email = self.session.get(EMAIL_KEY)
		users = User.gql('WHERE email = :1', email)
		template_params={
		}
		if (users.count(1) == 1):
			template_params[EMAIL_KEY] = email
		template = jinja_environment.get_template('templates/userForms/changePass.html')
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
			m = hashlib.md5()
			encodedString = word.encode('ascii', errors='replace')
			m.update(encodedString)
			user.passwordHash = str(m.hexdigest()) 
			user.put()
			template_values = {
				"password":word
			}
			messageTemplate = jinja_environment.get_template('templates/userForms/changePassMail.html')
			message = mail.EmailMessage(sender="Diet Futar <dietfutar@dietfutar.hu>")
			message.subject="Diet-futar, uj jelszo"
			message.to = email
			message.html = messageTemplate.render(template_values)
			message.send()
			template_params[EMAIL_KEY] = email
		template = jinja_environment.get_template('templates/userForms/changePassSuccess.html')
		self.printPage("Uj jelszo", template.render(template_params), True, True)
		
class RegisterPage(BaseHandler):
	URL = '/registration'
	def get(self):
		refererKey = self.request.get('refererKey')
		template_params={
			REGISTRATION_ERROR_KEY:self.session.get(REGISTRATION_ERROR_KEY,None),
			USER:self.session.get(USER, None)
		}
		if refererKey != None and refererKey != "":
			template_params['referer'] = User.get(refererKey)
		clearRegistrationError(self)
		template = jinja_environment.get_template('templates/userForms/register.html')
		self.printPage("Regisztracio", template.render(template_params), True, True)
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
		sourceOfInfo=self.request.get('sourceOfInfo')
		user = {}
		user["email"]= email
		user["familyName"]=familyName
		user["givenName"]=givenName
		user["phoneNumber"]=phoneNumber
		user["sourceOfInfo"]=sourceOfInfo
		users = User.gql('WHERE email = :1', email)
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
			user.password = "JELSZO_!@#"
			m = hashlib.md5()
			encodedString = password.encode('ascii', errors='replace')
			m.update(encodedString)
			user.passwordHash = str(m.hexdigest())
			user.phoneNumber=phoneNumber
			user.activated = False
			user.registrationDate=datetime.datetime.now(timeZone)
			user.referer = referer
			user.sourceOfInfo = sourceOfInfo
			word = ''
			random = Random()
			for i in range(1,32):
				word += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
			user.activationCode = word			
			user.put()
			updateUser(user)
			template_values = {
				'email':email,
				'activationCode':word,
				'user':user
			}
			messageTemplate = jinja_environment.get_template('templates/userForms/activation/activation_code.html')
			message = mail.EmailMessage(sender="Diet Futar <dietfutar@dietfutar.hu>")
			message.subject="Diet-futar, sikeres regisztracio"
			message.to = email
			message.body = messageTemplate.render(template_values)
			message.send()
			self.redirect("/activationPending")

class ActivationPendingPage (BaseHandler):
	URL = '/activationPending'
	def get(self):
			template = jinja_environment.get_template('templates/userForms/activation/activation_pending.html')
			self.printPage("Aktivacio", template.render(), True)
	
class ActivatePage (BaseHandler):
	URL = '/activate'
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
		template = jinja_environment.get_template('templates/userForms/activation/activation.html')
		self.printPage("Aktivacio", template.render(template_values), True)

class ChangePasswordPage (BaseHandler):
	URL = '/changePassword'
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
			m = hashlib.md5()
			encodedString = self.request.get("oldPassword").encode('ascii', errors='replace')
			m.update(encodedString)
			passwordHash = str(m.hexdigest())

			if user.passwordHash == passwordHash:
				passwd1 = self.request.get("newPassword")
				passwd2 = self.request.get("passwordCheck")
				if passwd1 == passwd2:
					m2 = hashlib.md5()
					encodedString = passwd1.encode('ascii', errors='replace')
					m2.update(encodedString)
					user.passwordHash = str(m2.hexdigest()) 
					user.put()
				else:
					self.session[LOGIN_ERROR_KEY] = REGISTRATION_ERROR_PASSWORD_DOESNT_MATCH
			else:
				self.session[LOGIN_ERROR_KEY] = "Hibas jelsz&oacute;"
		self.redirect("/profile")


class UserProfilePage (BaseHandler):
	URL = '/profile'
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
				LOGIN_ERROR_KEY:self.session.get(LOGIN_ERROR_KEY,0)
			}
			template = jinja_environment.get_template('templates/userForms/profile.html')
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
				}
				template = jinja_environment.get_template('templates/userForms/profile.html')
				self.printPage("Profil", template.render(template_values), False, True)
			else:
				self.redirect("/registration")
		else:
			self.redirect("/registration")

class AddressPage (BaseHandler):
	URL = '/address'
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
			if address != None:
				if (address.user.email != user.email):
					self.redirect("/profile")
					return
		if address == None:
			address = Address()
		address.user = user
		address.billingName = self.request.get("billingName")
		address.zipNumCode = int(self.request.get("zipNumCode"))
		address.street = self.request.get("street")
		address.streetNumber = self.request.get("streetNumber")
		address.put()
		self.redirect("/profile")

class DeleteAddressPage (BaseHandler):
	URL = '/deleteAddress'
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
			if address != None:
				if (address.user.email != user.email):
					self.redirect("/profile")
					return
				address.active = False
				address.put()
		self.redirect("/profile")

class Referals (BaseHandler):
	URL = '/referred'
	def get(self):
		if(not isUserLoggedIn(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
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
		






