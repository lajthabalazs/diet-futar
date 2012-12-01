from base_handler import BaseHandler, jinja_environment
from model import Maintenence


class MaintenencePage(BaseHandler):
	def get(self):
		template_values = {
			'date':'UNKNOWN',
			'features':''
		}
		maintenences = Maintenence.all().filter("active = ", True)
		if maintenences.count() > 0:
			m = maintenences.get()
			template_values['date'] = m.displayedDate
			template_values['features'] = m.features
		template = jinja_environment.get_template('templates/admin/siteDown.html')
		self.response.out.write(template.render(template_values))