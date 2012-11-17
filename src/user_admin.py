#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler
from model import User, Role, ROLE_ADMIN
from user_management import isUserAdmin, getUser
#from user_management import getUserBox

ACTUAL_ORDER="actualOrder"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

#An accumulated overview of every ordered item
class UserListPage(BaseHandler):
	def get(self):
		#user=getUser(self)
		#user.role=Role.all().filter("name = ", ROLE_ADMIN)[0]
		#user.put()
		if(not isUserAdmin(self)):
			self.redirect("/")
			return
		pageText=self.request.get("page")
		pageSize=10
		actualPage=0
		if (pageText!=None and pageText!=""):
			actualPage=int(pageText)-1
		orderByText=self.request.get("order")
		if (orderByText==None or orderByText==""):
			orderByText='email'
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
#An accumulated overview of every ordered item
class UserOverviewPage(BaseHandler):
	def get(self):
		if(not isUserAdmin(self)):
			self.redirect("/")
			return
		userKey = self.request.get("userKey")
		if (userKey != None and userKey != ""):
			user = User.get(userKey)
			if user != None:
				template_values = {
					"user":user,
				}
				template = jinja_environment.get_template('templates/userOverview.html')
				self.printPage(user.familyName + " " + user.givenName, template.render(template_values), False, False)
			else:
				self.printPage("User hiba", "Nincs ilyen felhasznalo.", False, False)