#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler
from model import User
from user_management import isUserAdmin, LOGIN_NEXT_PAGE_KEY
from google.appengine.api import mail

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class NewsletterPage(BaseHandler):
	URL = '/newsletter'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		users=User.all().order("familyName")
		template_values={
			'userList':users
		}
		template = jinja_environment.get_template('templates/newsletter/newsletterEditor.html')
		self.printPage("H&iacute;rlev&eacute;l", template.render(template_values), False, False)
	def post(self):
		if(not isUserAdmin(self)):
			self.redirect("/")
			return
		recipientKeys = []
		htmlMessage = self.request.get("htmlMessage")
		textMessage = self.request.get("textMessage")
		messageTitle = self.request.get("messageTitle")
		for field in self.request.arguments():
			if (field[:5]=="USER_"):
				if (self.request.get(field) == "send"):
					recipientKeys.append(field[5:])
		dbUsers=User.all().order("familyName")
		users = []
		for user in dbUsers:
			try:
				if str(user.key()) in recipientKeys:
					# Send mail
					message_template = {
						'user' : user,
						'htmlMessage' : htmlMessage,
						'textMessage' : textMessage,
						'messageTitle': messageTitle
					}
					messageTxtTemplate = jinja_environment.get_template('templates/newsletter/newsletterText.txt')
					messageHtmlTemplate = jinja_environment.get_template('templates/newsletter/newsletterText.html')
					message = mail.EmailMessage(sender="Diet Futar <dietfutar@dietfutar.hu>")
					message.subject=messageTitle
					message.to = user.email
					message.body = messageTxtTemplate.render(message_template)
					message.html = messageHtmlTemplate.render(message_template)
					message.send()
					user.mailSent = True
			except:
				pass
			users.append(user)
		template_values={
			'userList':users,
			'htmlMessage':htmlMessage,
			'textMessage':textMessage,
			'messageTitle': messageTitle
		}
		template = jinja_environment.get_template('templates/newsletter/newsletterResult.html')
		self.printPage("H&iacute;rlev&eacute;l", template.render(template_values), False, False)
		
class UnsubscribePage(BaseHandler):
	URL = '/unsubscribe'
	def get(self):
		user = User.get(self.request.get("userKey"))
		user.unsubscribedFromNewsletter = True
		user.put()
		template = jinja_environment.get_template('templates/newsletter/unsubscribe.html')
		self.printPage("H&iacute;rlev&eacute;l", template.render(), False, False)