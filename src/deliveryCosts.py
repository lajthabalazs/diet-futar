import jinja2
import os
from base_handler import BaseHandler, logInfo
from cache_zips import getLimitArrayScript, getCostArrayScript


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class AboutDeliveryPage(BaseHandler):
	URL = '/aboutDelivery'
	def get(self):
		template_values = {
			'addressLimits' : getLimitArrayScript(),
			'addressCosts' : getCostArrayScript()
			}
		logInfo(self, self.URL, "DELIVERY_PAGE_LOADED")
		template = jinja_environment.get_template('templates/about/aboutDelivery.html')
		self.printPage("Rendel&eacute;s", template.render(template_values), True, True)