#!/usr/bin/env python

import jinja2
import os

from google.appengine.ext import db

from base_handler import BaseHandler
from model import User
#from user_management import getUserBox

ACTUAL_ORDER="actualOrder"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

#An accumulated overview of every ordered item
class UserListPage(BaseHandler):
	def get(self):
		pageText=self.request.get("page")
		pageSize=10
		actualPage=0
		if (pageText!=None and pageText!=""):
			actualPage=int(pageText)-1
		orderByText=self.request.get("order")
		if (orderByText==None or orderByText==""):
			orderByText='email'
		userCount=User.all().count()
		
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
			'order':orderByText
		}
		if actualPage < userCount/ pageSize - 1 - corrector:
			template_values["nextPage"]=actualPage + 2
		if actualPage > 0:
			template_values["nextPage"]=actualPage
		template = jinja_environment.get_template('templates/userList.html')
		self.printPage("Felhasznalok", template.render(template_values), True)

		
#An accumulated overview of every ordered item
class UserOverviewPage(BaseHandler):
	def get(self):
		pass