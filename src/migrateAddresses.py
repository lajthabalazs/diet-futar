from base_handler import BaseHandler, jinja_environment
from model import Address
from user_management import isUserAdmin
from cache_zips import getZipCodeEntry

def isProperZipCode(code):
	return (getZipCodeEntry(code) != None)

class MigrateZipCodesToNumberFormat(BaseHandler):
	def get(self):
		if not isUserAdmin(self):
			self.printPage("Dashboard", "", True, True)
			return
		addresses = Address.all()
		address = Address()
		for address in addresses:
			address.active = True
			try:
				code = int(address.zipCode)
				if isProperZipCode(code):
					address.zipNumCode = code
				else:
					address.zipNumCode = 1111
			except:
				address.zipNumCode = 1111
			address.put()
		template_values = {
			'addresses':addresses
		}
		template = jinja_environment.get_template('templates/admin/siteAdmin.html')
		self.printPage("dashboard", template.render(template_values), False, False)
