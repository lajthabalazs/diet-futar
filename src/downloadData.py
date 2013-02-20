from base_handler import BaseHandler, jinja_environment
from user_management import isUserAdmin, LOGIN_NEXT_PAGE_KEY
from model import Dish, Composit, MenuItem, User, UserWeekOrder

class DataDownloadMainPage(BaseHandler):
	URL = "/dataDownloadPage"
	def get(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		template = jinja_environment.get_template('templates/admin/dataDownloadPage.html')
		self.response.out.write(template.render())
	
class DishListCsv(BaseHandler):
	URL = "/dishList.csv"
	def get(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		dishes = Dish.all()
		template_values = {
			'dishes' : dishes
		}
		template = jinja_environment.get_template('templates/csv/dishList.download')
		self.response.out.write(template.render(template_values))

class CompositListCsv(BaseHandler):
	URL = "/compositList.csv"
	def get(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		composits = Composit.all()
		template_values = {
			'composits' : composits
		}
		template = jinja_environment.get_template('templates/csv/compositList.download')
		self.response.out.write(template.render(template_values))

class MenuItemListCsv(BaseHandler):
	URL = "/menuItemList.csv"
	def get(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		menuItems = MenuItem.all()
		template_values = {
			'menuItems' : menuItems
		}
		template = jinja_environment.get_template('templates/csv/menuItemList.download')
		self.response.out.write(template.render(template_values))

class UserListCsv(BaseHandler):
	URL = "/userList.csv"
	def get(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		users = User.all()
		template_values = {
			'users' : users
		}
		template = jinja_environment.get_template('templates/csv/userList.download')
		self.response.out.write(template.render(template_values))

class WeeksCsv(BaseHandler):
	URL = "/userOrders.csv"
	def get(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		weeks = UserWeekOrder.all()
		template_values = {
			'weeks' : weeks
		}
		template = jinja_environment.get_template('templates/csv/userOrders.download')
		self.response.out.write(template.render(template_values))




























