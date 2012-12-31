from base_handler import BaseHandler, jinja_environment, getMonday
from model import Role, ROLE_ADMIN, ROLE_DELIVERY_GUY, ROLE_COOK, ROLE_AGENT, User,\
	Maintenence, UserWeekOrder
from user_management import isUserAdmin

import datetime
from order import getOrderTotal

class AdminConsolePage(BaseHandler):
	def get(self):
		if not isUserAdmin(self):
			self.printPage("Dashboard", "", True, True)
			return
		orderedMaintenences = Maintenence.all().order('startDate')
		template_values = {
			'maintenences':orderedMaintenences
		}
		template = jinja_environment.get_template('templates/admin/siteAdmin.html')
		self.printPage("dashboard", template.render(template_values), True, True)

class ScheduleMainenencePage(BaseHandler):
	def post(self):
		displayedDate = self.request.get('displayedDate')
		features = self.request.get('features')
		maintenence = Maintenence()
		maintenence.active = True
		maintenence.startDate = datetime.datetime.now()
		maintenence.displayedDate = displayedDate
		maintenence.features = features
		maintenence.put()
		self.redirect("/siteAdmin")

class EndMainenencePage(BaseHandler):
	def post(self):
		maintenenceKey = self.request.get('maintenenceKey')
		maintenence = Maintenence.get(maintenenceKey)
		maintenence.active = False
		maintenence.endDate = datetime.datetime.now()
		maintenence.put()
		self.redirect("/siteAdmin")

class SetupPage(BaseHandler):
	def get(self):
		roles=Role.all()
		if roles.count() == 0:
			template = jinja_environment.get_template('templates/setup/setup.html')
			self.printPage("Weboldal nicializ&aacute;l&aacute;sa", template.render(), True, True)
		else:
			template = jinja_environment.get_template('templates/setup/alreadySetUp.html')
			self.printPage("Kor&aacute;bban inicializ&aacute;lva", template.render(), True, True)
	def post(self):
		roles=Role.all()
		if roles.count() == 0:
			# No roles were set up, set them up now
			adminRole = Role()
			adminRole.name=ROLE_ADMIN
			adminRole.put()
			role = Role()
			role.name=ROLE_DELIVERY_GUY
			role.put()
			role = Role()
			role.name=ROLE_COOK
			role.put()
			role = Role()
			role.name=ROLE_AGENT
			role.put()
			user = User()
			user.email = self.request.get("adminEmail")
			user.password = self.request.get("adminPassword")
			user.activated = True
			user.role = adminRole
			user.put();
			template = jinja_environment.get_template('templates/setup/setupSuccess.html')
			self.printPage("Sikeres inicializ&aacute;l&aacute;s", template.render(), True, True)
		else:
			template = jinja_environment.get_template('templates/setup/alreadySetUp.html')
			self.printPage("Kor&aacute;bban inicializ&aacute;lva", template.render(), True, True)

class EveryUsersOrderPage(BaseHandler):
	def get(self):
		if not isUserAdmin(self):
			self.printPage("Dashboard", "", True, True)
			return
		user = User()
		users = User.all()
		allUsers = []
		today=datetime.date.today()
		monday = getMonday(today)
		maxWeeks = 20
		weekTotals = []
		for i in range(0, maxWeeks):
			weekTotalITem = {
					'total' : 0,
					'monday' : monday + datetime.timedelta(days = (i - maxWeeks + 1) * 7)
				}
			weekTotals.append(weekTotalITem)
		for user in users:
			orderTotal = 0
			computedWeeks = []
			for i in range(0, maxWeeks):
				actualMonday = monday + datetime.timedelta(days = (i - maxWeeks + 1) * 7)
				weeks = user.weeks.filter("monday = ", actualMonday)
				if (weeks.count() > 0):
					weekTotal = getOrderTotal(weeks)
					weekTotals[i]['total'] = weekTotals[i]['total'] + weekTotal
					computedWeek = {
						'itemPrice': weekTotal,
						'userKey':user.key(),
						'day': actualMonday,
					}
					orderTotal = orderTotal + weekTotal
				else:
					computedWeek = {'itemPrice': 0}
				computedWeeks.append(computedWeek)
			user.computedWeeks = computedWeeks
			user.orderTotal = orderTotal
			allUsers.append(user)
		orderedUsers = sorted(allUsers, key=lambda item:item.orderTotal, reverse=True)
		template_values = {
			'users':orderedUsers,
			'weekTotals':weekTotals
		}
		template = jinja_environment.get_template('templates/admin/everyUsersOrder.html')
		self.printPage("Rendel&eacute;sek", template.render(template_values), True, True)
		