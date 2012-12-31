import jinja2
import os
from base_handler import BaseHandler
import webapp2


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class AboutDeliveryPage(BaseHandler):
	def get(self):
		template = jinja_environment.get_template('templates/about/aboutDelivery.html')
		self.printPage("Rendel&eacute;s", template.render(), True, True)

class AboutPage(BaseHandler):
	def get(self):
		template = jinja_environment.get_template('templates/about/about.html')
		self.printPage("R&oacute;lunk", template.render(), True, True)

class ContactsPage(BaseHandler):
	def get(self):
		template = jinja_environment.get_template('templates/contacts.html')
		self.printPage("Kapcsolat", template.render(), True, True)
		
class CaloryCalculator(BaseHandler):
	def get(self):
		template = jinja_environment.get_template('templates/caloryCalculator.html')
		self.printPage("Kaloria szamito", template.render(), True, True)
		
class GooglePage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('templates/google24f0feb13afae7e0.html')
		self.response.out.write(template.render())

class NewYearPage(BaseHandler):
	def get(self):
		template = jinja_environment.get_template('templates/newYear.html')
		self.printPage("Boldog &Uacute; &Eacute;vet!", template.render(), True, True)
