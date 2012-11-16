import jinja2
import os
from base_handler import BaseHandler


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class AboutPage(BaseHandler):
	def get(self):
		template = jinja_environment.get_template('templates/about.html')
		self.printPage("Rendel&eacute;s", template.render(), True, True)
		
class CaloryCalculator(BaseHandler):
	def get(self):
		template = jinja_environment.get_template('templates/caloryCalculator.html')
		self.printPage("Kaloria szamito", template.render(), True, True)