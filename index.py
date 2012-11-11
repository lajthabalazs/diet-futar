import jinja2
import os
from base_handler import BaseHandler


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class AboutPage(BaseHandler):
	def get(self):
		template = jinja_environment.get_template('templates/about.html')
		self.printPage("Alapanyagok", template.render(), False, False)