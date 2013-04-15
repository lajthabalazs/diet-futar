from base_handler import BaseHandler, jinja_environment
import webapp2

class AboutPage(BaseHandler):
	URL = '/about'
	def get(self):
		template = jinja_environment.get_template('templates/about/about.html')
		self.printPage("R&oacute;lunk", template.render(), True, True)

class FAQPage(BaseHandler):
	URL = '/faq'
	def get(self):
		template = jinja_environment.get_template('templates/about/faq.html')
		self.printPage("GY.I.K", template.render(), True, True)

class ServicesPage(BaseHandler):
	URL = '/services'
	def get(self):
		template = jinja_environment.get_template('templates/about/services.html')
		self.printPage("Szolg&aacute;ltat&aacute;sok", template.render(), True, True)

class GlutenPage(BaseHandler):
	URL = '/gluten'
	def get(self):
		template = jinja_environment.get_template('templates/about/gluten.html')
		self.printPage("GY.I.K", template.render(), True, True)

class ContactsPage(BaseHandler):
	URL = '/contacts'
	def get(self):
		template = jinja_environment.get_template('templates/contacts.html')
		self.printPage("Kapcsolat", template.render(), True, True)
		
class CaloryCalculator(BaseHandler):
	URL = '/caloryCalculator'
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

class PrivacyPage(BaseHandler):
	URL = '/privacy'
	def get(self):
		template = jinja_environment.get_template('templates/userForms/privacy.html')
		self.printPage("Adatv&eacute;delmi nyilatkozat", template.render(), True, True)
