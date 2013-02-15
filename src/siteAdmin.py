from base_handler import BaseHandler, jinja_environment, getMonday, parseDate,\
	getSiteParam, DELIVERY_START_KEY, DELIVERY_END_KEY, ORDER_DEADLINE_KEY,\
	timeZone
from model import Role, ROLE_ADMIN, ROLE_DELIVERY_GUY, ROLE_COOK, ROLE_AGENT, User,\
	Maintenence, ZipCodes, UserWeekOrder
from user_management import isUserAdmin, LOGIN_NEXT_PAGE_KEY

import datetime
from zipCodeInit import createZipCodeList
from cache_zips import updateZipCodeEntry, updateZipCodeScript
from cacheWeek import getUsers, getUserWeekForDay, clearUsersFromCache
from orderHelper import getOrderTotal

class AdminConsolePage(BaseHandler):
	URL = "/siteAdmin"
	def get(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		
		orderedMaintenences = Maintenence.all().order('startDate')
		template_values = {
			'maintenences':orderedMaintenences,
			ORDER_DEADLINE_KEY:getSiteParam(ORDER_DEADLINE_KEY),
			DELIVERY_START_KEY:getSiteParam(DELIVERY_START_KEY),
			DELIVERY_END_KEY:getSiteParam(DELIVERY_END_KEY),
			'currentTime':datetime.datetime.now(timeZone)
		}
		template = jinja_environment.get_template('templates/admin/siteAdmin.html')
		self.printPage("dashboard", template.render(template_values), False, False)

class ScheduleMainenencePage(BaseHandler):
	URL ='/scheduleMainenence'
	def post(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		displayedDate = self.request.get('displayedDate')
		features = self.request.get('features')
		maintenence = Maintenence()
		maintenence.active = True
		maintenence.startDate = datetime.datetime.now()
		maintenence.displayedDate = displayedDate
		maintenence.features = features
		maintenence.put()
		self.redirect("/siteAdmin")

class ZipCodeEditorPage(BaseHandler):
	URL = '/editZipCodes'
	def get(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		rawCodes = ZipCodes.all().get()
		if (rawCodes == None):
			rawCodes = ZipCodes()
			zipCodeList = createZipCodeList()
			rawCodes.deliveryCosts = zipCodeList
			rawCodes.put()
		codes = []
		for code in rawCodes.deliveryCosts:
			parts=code.rsplit(" ")
			codes.append(
				{
					'code':parts[0],
					'cost':parts[1],
					'limit':parts[2]
				})
		template_values = {
			'codes':codes
		}
		template = jinja_environment.get_template('templates/admin/zipCodeEditor.html')
		self.printPage("dashboard", template.render(template_values), False, False)
	def post(self):
		self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		codes = {}
		for field in self.request.arguments():
			code = field[:4]
			if not codes.has_key(code):
				codeObj = {}
			else:
				codeObj = codes[code]
			if (field[4:8]=="_cst"):
				codeObj['cost'] = int(self.request.get(field))
			else:
				codeObj['limit'] = int(self.request.get(field))
			codes[code] = codeObj
		sortedCodes =  sorted(codes.keys())
		deliveryCosts = []
		for code in sortedCodes:
			updateZipCodeEntry(code, codes.get(code)['cost'], codes.get(code)['limit'])
			deliveryCosts.append(code + " " + str(codes.get(code)['cost']) + " " + str(codes.get(code)['limit']))
		rawCodes = ZipCodes.all().get()
		if (rawCodes == None):
			rawCodes = ZipCodes()
		rawCodes.deliveryCosts = deliveryCosts
		rawCodes.put()
		updateZipCodeScript(rawCodes)
		self.redirect("/editZipCodes")


class EndMainenencePage(BaseHandler):
	URL = '/endMaintenence'
	def post(self):
		self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		maintenenceKey = self.request.get('maintenenceKey')
		maintenence = Maintenence.get(maintenenceKey)
		maintenence.active = False
		maintenence.endDate = datetime.datetime.now()
		maintenence.put()
		self.redirect("/siteAdmin")

class SetupPage(BaseHandler):
	URL = "/setup"
	def get(self):
		roles=Role.all()
		if roles.count() == 0:
			template = jinja_environment.get_template('templates/setup/setup.html')
			self.printPage("Weboldal nicializ&aacute;l&aacute;sa", template.render(), True, True)
		else:
			template = jinja_environment.get_template('templates/setup/alreadySetUp.html')
			self.printPage("Kor&aacute;bban inicializ&aacute;lva", template.render(), True, True)
	def post(self):
		self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
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
	URL = '/everyUsersOrder'
	def get(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
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
						'monday': actualMonday,
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
		self.printPage("Rendel&eacute;sek", template.render(template_values), False, False)

class UsersFromCachePage(BaseHandler):
	URL = '/cachedUsers'
	def get(self):
		
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		users = getUsers()
		allUsers = []
		today=datetime.date.today()
		monday = getMonday(today)
		maxWeeks = 20
		weekTotals = []
		for i in range(0, maxWeeks):
			weekTotalITem = {
					'total' : 0,
					'monday' : monday + datetime.timedelta(days = (i - maxWeeks + 2) * 7)
				}
			weekTotals.append(weekTotalITem)
		for user in users:
			orderTotal = 0
			computedWeeks = []
			for i in range(0, maxWeeks):
				actualMonday = monday + datetime.timedelta(days = (i - maxWeeks + 2) * 7)
				week = getUserWeekForDay(user['key'], actualMonday)
				if week != None:
					weekTotals[i]['total'] = weekTotals[i]['total'] + week['weekTotal']
					computedWeek = {
						'itemPrice': week['weekTotal'],
						'userKey':user['key'],
						'monday': actualMonday,
					}
					orderTotal = orderTotal + week['weekTotal']
				else:
					computedWeek = {'itemPrice': 0}
				computedWeeks.append(computedWeek)
			user['computedWeeks'] = computedWeeks
			user['orderTotal'] = orderTotal
			allUsers.append(user)
		orderedUsers = sorted(allUsers, key=lambda item:item['orderTotal'], reverse=True)
		template_values = {
			'users':orderedUsers,
			'weekTotals':weekTotals
		}
		template = jinja_environment.get_template('templates/admin/users.html')
		self.printPage("Rendel&eacute;sek", template.render(template_values), False, False)
		
class ClearUserArrayFromCache(BaseHandler):
	URL = '/clearUserArrayFromCache'
	def post(self):
		self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		clearUsersFromCache()
		self.redirect(UsersFromCachePage.URL)

class ReplaceComposit(BaseHandler):
	URL = '/replaceComposit'
	def get(self):
		self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		template = jinja_environment.get_template('templates/admin/replaceComposit.html')
		self.printPage("Kompositok cser&eacute;je", template.render(), False, False)
	def post(self):
		self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		toReplace = self.request.get('toReplace')
		replaceWith = self.request.get('replaceWith')
		monday = self.request.get('monday')
		mondaysWeeks = UserWeekOrder.all().filter("monday = ", parseDate(monday))
		weeks = []
		for week in mondaysWeeks:
			newComposits = []
			modified = False
			for item in week.orderedComposits:
				if item.find(toReplace) != -1:
					modified = True
					newItem = item.replace(toReplace, replaceWith)
					newComposits.append(newItem)
				else:
					newComposits.append(item)
			if modified:
				week.orderedComposits = newComposits
				week.put()
				weeks.append(week)
		template_values = {
			'toReplace':toReplace,
			'replaceWith':replaceWith,
			'monday':monday,
			'weeks':weeks
		}
		template = jinja_environment.get_template('templates/admin/replaceComposit.html')
		self.printPage("Kompositok cser&eacute;je", template.render(template_values), False, False)

class ChangeDeliveryTime(BaseHandler):
	def post(self):
		orderDeadline = self.request.get(ORDER_DEADLINE_KEY)
		deliveryStart = self.request.get(DELIVERY_START_KEY)
		deliveryEnd = self.request.get(DELIVERY_END_KEY)
		self.redirect(AdminConsolePage.URL)











