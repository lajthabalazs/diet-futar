import jinja2
import os
from base_handler import BaseHandler, logInfo, getDeadline, getSiteParam,\
	DELIVERY_START_KEY, DELIVERY_END_KEY, ORDER_DEADLINE_KEY
from cache_zips import getLimitArrayScript, getCostArrayScript


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class AboutDeliveryPage(BaseHandler):
	URL = '/aboutDelivery'
	def get(self):
		deadline = getSiteParam(ORDER_DEADLINE_KEY)
		deliveryStart = getSiteParam(DELIVERY_START_KEY)
		deliveryEnd = getSiteParam(DELIVERY_END_KEY)
		template_values = {
			'addressLimits' : getLimitArrayScript(),
			'addressCosts' : getCostArrayScript(),
			'deadline' : deadline,
			'deliveryStart' : deliveryStart,
			'deliveryEnd' : deliveryEnd
			}
		logInfo(self, self.URL, "DELIVERY_PAGE_LOADED")
		template = jinja_environment.get_template('templates/about/aboutDelivery.html')
		self.printPage("Rendel&eacute;s", template.render(template_values), True, True)