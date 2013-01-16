from base_handler import BaseHandler, jinja_environment
from model import Maintenence
from user_management import LOGIN_NEXT_PAGE_KEY, isUserAdmin


class MaintenencePage(BaseHandler):
	URL = "/maintenance"
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
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