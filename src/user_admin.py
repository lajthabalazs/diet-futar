#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler
from model import User, Role
from user_management import isUserAdmin, getUser, USER_KEY, LOGIN_NEXT_PAGE_KEY
from google.appengine.api.datastore_errors import BadKeyError
import hashlib

ACTUAL_ORDER="actualOrder"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class UserListPage(BaseHandler):
	URL = '/userList'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		pageText=self.request.get("page")
		pageSize=20
		actualPage=0
		if (pageText!=None and pageText!=""):
			actualPage=int(pageText)-1
		orderByText=self.request.get("order")
		if (orderByText==None or orderByText==""):
			orderByText='familyName'
		userCount=User.all().count()
		roles=Role.all().order("name")
		usersToDisplay=User.all().order(orderByText).run(offset=actualPage*pageSize, limit=pageSize)
		pages=[]
		corrector=1
		if (userCount/pageSize) * pageSize == userCount:
			corrector=0
		for i in range(0,userCount/pageSize + corrector):
			pages.append(i+1)
		template_values={
			'page':actualPage+1,
			'pages':pages,
			'userList':usersToDisplay,
			'order':orderByText,
			'roles':roles
		}
		if actualPage < userCount/ pageSize - 1 - corrector:
			template_values["nextPage"]=actualPage + 2
		if actualPage > 0:
			template_values["nextPage"]=actualPage
		template = jinja_environment.get_template('templates/userList.html')
		self.printPage("Felhasznalok", template.render(template_values), False, False)
	def post(self):
		if(not isUserAdmin(self)):
			self.redirect("/")
			return
		# Save user
		userKey=self.request.get("userKey")
		if userKey!=None and userKey!="":
			userToChange=User.get(userKey)
			user=getUser(self)
			# Can't change own account for safety reasons
			if user.key() == userToChange.key():
				self.redirect("/userList")
				return
			else:
				userToChange.activated = self.request.get("activated")=="on"
				roleKey=self.request.get("role")
				if roleKey!=None and roleKey != "":
					userToChange.role=Role.get(roleKey)
				else:
					userToChange.role=None
				userToChange.put()
		self.redirect("/userList")

class SwitchToUserPage(BaseHandler):
	URL = '/switchToUser'
	def post(self):
		if(not isUserAdmin(self)):
			self.redirect("/")
			return
		userKey = self.request.get("userKey")
		if (userKey != None and userKey != ""):
			user = None
			try:
				user = User.get(userKey)
			except BadKeyError:
				pass
			if user != None:
				self.session[USER_KEY]=str(userKey)
				self.redirect("/");

				
#An accumulated overview of every ordered item
class UserOverviewPage(BaseHandler):
	URL = '/userOverview'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		userKey = self.request.get("userKey")
		if (userKey != None and userKey != ""):
			user = None
			try:
				user = User.get(userKey)
			except BadKeyError:
				pass
			if user != None:
				template_values = {
					"user":user,
				}
				template = jinja_environment.get_template('templates/userOverview.html')
				userName = ""
				if (user.familyName != None):
					userName = userName + user.familyName
				if (user.familyName != None) and (user.givenName != None):
					userName = userName + " "
				if (user.givenName != None):
					userName = userName + user.givenName
				if userName == "":
					userName = "UNKNOWN"
				self.printPage(userName, template.render(template_values), False, False)
			else:
				template_values = {
					"title":"Nincs ilyen felhasznalo",
					"message":"Menj vissza, probald meg megegyszer."
				}
				template = jinja_environment.get_template('templates/staticMessage.html')
				self.printPage("User hiba", template.render(template_values), False, False)


class HashUserPasswordPage(BaseHandler):
	URL = '/hashUserPasswordPage'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		users = User.all()
		for user in users:
			if (user.password != "JELSZO_!@#"):
				m = hashlib.md5()
				encodedString = user.password.encode('ascii', errors='replace')
				m.update(encodedString)
				user.passwordHash = str(m.hexdigest())
				user.password = "JELSZO_!@#"
				user.put()
		template_values = {
			"title":"Jelszo hash-ek generalva.",
			"message":"Legeneraltuk a jelszo hash-ket"
		}
		template = jinja_environment.get_template('templates/staticMessage.html')
		self.printPage("User hiba", template.render(template_values), False, False)






