'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
import webapp2
from webapp2_extras import sessions
from user_management import getUserBox, isUserLoggedIn, isUserAdmin, isUserCook, isUserDelivery,\
	isUserAgent, getUser
import jinja2
import os
from keys import DISH_CATEGORY_URL
import datetime
from timezone import USTimeZone
from model import Maintenence, SiteParams
from string import replace, split
import logging
from orderHelper import isMenuItem
from cache_menu_item import getMenuItem
from cache_composit import getComposit
import time

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
LAST_ORDER_HOUR=11
timeZone=USTimeZone(1, "CEST", "CEST", "CEST")
dayNames=["H&#233;tf&#337;","Kedd","Szerda","Cs&#252;t&#246;rt&#246;k","P&#233;ntek","Szombat","Vas&#225;rnap"]
FORM_DAY = "formDay"
ORDER_DEADLINE_KEY = "orderDeadline"
DELIVERY_START_KEY = "deliveryStart"
DELIVERY_END_KEY = "deliveryEnd"

def getSiteParam(paramName):
	paramDb = SiteParams.all().filter("name = ", paramName).get()
	if paramDb == None:
		return None
	else:
		return paramDb.value

def setSiteParam(name, value):
	paramDb = SiteParams.all().filter("name = ", name).get()
	if paramDb != None:
		paramDb.value = value
	else:
		paramDb = SiteParams()
		paramDb.name = name
		paramDb.value = value
	paramDb.put()
	
def logInfo(handler, url, message):
	template_values_for_logging = {
		"user":getUser(handler),
		"url":url,
		"message":message,
		'now':datetime.datetime.now(timeZone)
	}
	
	loggingTemplate = jinja_environment.get_template('templates/log/basic_message.txt')
	logging.info(loggingTemplate.render(template_values_for_logging))

def getDeadline():
	orderDeadline = getSiteParam(ORDER_DEADLINE_KEY)
	if orderDeadline != None:
		try:
			return time.strptime(orderDeadline, "%H:%M")
		except:
			pass
	return time.strptime("10:00", "%H:%M")
	
def getFirstOrderableDate(handler):
	today = datetime.date.today()
	now = datetime.datetime.now(timeZone)
	firstOrderableDay = today
	deadline = getDeadline()
	if now.hour > deadline.tm_hour or ((now.hour == deadline.tm_hour) and (now.minute > deadline.tm_min)):
		firstOrderableDay=today+datetime.timedelta(days=1)
	if firstOrderableDay.weekday()==5:
		firstOrderableDay=firstOrderableDay+datetime.timedelta(days=2)
	elif firstOrderableDay.weekday()==6:
		firstOrderableDay=firstOrderableDay+datetime.timedelta(days=1)
	return firstOrderableDay;

def getMonday(day):
	return day + datetime.timedelta(days = - day.weekday())
	
# Returns the first date user can order
def getOrderBaseDate(handler):
	day = datetime.date.today()	
	requestDay=handler.request.get('day')
	if ((requestDay != None) and (requestDay != "")):
		parts = requestDay.rsplit("-")
		day = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
	else:
		day = getFirstOrderableDate(handler)
	return day

# Returns the first date the user has an ordered item
def getBasketBaseDate(actualOrder, handler):
	requestDay=handler.request.get('day')
	if ((requestDay != None) and (requestDay != "")):
		parts=requestDay.rsplit("-")
		day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
		return day
	firstDay = None
	if actualOrder != None and len(actualOrder) > 0:
		orderedMenuItemKeys=[]
		for key in actualOrder.keys():
			orderedMenuItemKeys.append(key)
		for key in orderedMenuItemKeys:
			actualDay = None
			if isMenuItem(key):
				menuItem = getMenuItem(key)
				if (menuItem != None):
					actualDay = menuItem['day']
			else:
				composit = getComposit(key)
				if (composit != None):
					actualDay = composit['day']
			if (firstDay == None):
				firstDay = actualDay
			elif firstDay > actualDay:
				firstDay = actualDay
	if firstDay == None:
		return getFirstOrderableDate(handler)
	else:
		return firstDay

# Returns the first date user can order or the date indicated by the request
def getBaseDate(handler):
	day=datetime.date.today()	
	requestDay=handler.request.get('day')
	if ((requestDay != None) and (requestDay != "")):
		parts=requestDay.rsplit("-")
		day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
	else:
		calendar=day.isocalendar()
		#Organize into days
		if calendar[2]==4 and datetime.datetime.now().hour > 16:
			pass
			#day=day+datetime.timedelta(days=3)
		elif calendar[2]==5:
			day=day+datetime.timedelta(days=2)
		elif calendar[2]==6:
			day=day+datetime.timedelta(days=1)
	return day

def parseDate(requestDay):
	if ((requestDay != None) and (requestDay != "")):
		parts=requestDay.rsplit("-")
		day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
		return day
	else:
		return None
	
# Returns the day indicated by the posted form if any otherwise the current day
def getFormDate(handler):
	requestDay=handler.request.get(FORM_DAY)
	day=parseDate(requestDay)
	if day != None:
		return day
	else:
		return datetime.date.today()

class BaseHandler(webapp2.RequestHandler):
	def dispatch(self):
		self.session_store = sessions.get_store(request=self.request)
		if Maintenence.all().filter("active = ", True).count() > 0:
			if not isUserAdmin(self):
				baseUrl = replace(self.request.url, self.request.query_string, "")
				baseUrl = replace(baseUrl, "?", "")
				parts = split(baseUrl,"/")
				lastPart = parts[len(parts) -1]
				if (lastPart != "siteAdmin") and \
						(lastPart != "login") and \
						(lastPart != "logout") and \
						(lastPart != "maintenence"):
					self.redirect("/maintenence")
					return
		# Get a session store for this request.
		try:
			# Dispatch the request.
			webapp2.RequestHandler.dispatch(self)
		finally:
			# Save all sessions.
			self.session_store.save_sessions(self.response)
	def printPage(self, title, content, forAnonymus=False, forLoggedIn=False):
		if (title != None and title != ""):
			title = "Diet futar - " + title
		else:
			title="Diet futar"
		template_params={
			"pageTitle":title
		}
		ret=jinja_environment.get_template('templates/headers/header_part_zero.html').render(template_params)
		topMenu=[]
		user = getUser(self)
		if (user != None):
			user.lastPageAccess = datetime.datetime.now(timeZone)
			user.put()
		if isUserAdmin(self):
			dailyMenu={}
			dailyMenu["label"]="Napi menu"
			dailyMenu["target"]="/menuEdit"
			topMenu.append(dailyMenu)
			weeklyMenu={}
			weeklyMenu["label"]="Heti menu"
			weeklyMenu["target"]="/menuWeekEdit"
			topMenu.append(weeklyMenu)
			payingOrders={}
			payingOrders["label"]="Rendelt"
			payingOrders["target"]="/chefReviewOrders"
			topMenu.append(payingOrders)
			toDeliver={}
			toDeliver["label"]="Sz&aacute;llitand&oacute;"
			toDeliver["target"]="/deliveryReviewOrders"
			topMenu.append(toDeliver)
			webShop={}
			webShop["label"]="Term&eacute;kek"
			webShop["target"]="/itemList"
			topMenu.append(webShop)
			webShopOrder={}
			webShopOrder["label"]="WebShop"
			webShopOrder["target"]="/usersOrders"
			topMenu.append(webShopOrder)
			ingredients={}
			ingredients["label"]="Alapanyagok"
			ingredients["target"]="/ingredient"
			topMenu.append(ingredients)
			categories={}
			categories["label"]="Ketegori&aacute;k"
			categories["target"]="/ingredientCategory"
			topMenu.append(categories)
			recepies={}
			recepies["label"]="Receptek"
			recepies["target"]="/dish"
			topMenu.append(recepies)
			dishCategories={}
			dishCategories["label"]="Fog&aacute;sok"
			dishCategories["target"]=DISH_CATEGORY_URL
			topMenu.append(dishCategories)
			userList={}
			userList["label"]="Felhaszn&aacute;l&oacute;k"
			userList["target"]="/userList"
			topMenu.append(userList)
			agent={}
			agent["label"]="Aj&aacute;nlott"
			agent["target"]="/referred"
			topMenu.append(agent)
			siteAdmin={}
			siteAdmin["label"]="Adminisztraci&oacute;"
			siteAdmin["target"]="/siteAdmin"
			topMenu.append(siteAdmin)
			viewLogs={}
			viewLogs["label"]="Logok"
			viewLogs["target"]="/viewLogs"
			topMenu.append(viewLogs)
			crm={}
			crm["label"]="CRM"
			crm["target"]="/crmMainPage"
			topMenu.append(crm)
			onsiteIncome={}
			onsiteIncome["label"]="Facebook l&aacute;togat&oacute;k"
			onsiteIncome["target"]="/weeklyFacebookVisits"
			topMenu.append(onsiteIncome)
			dataDownload={}
			dataDownload["label"]="Adatok let&ouml;lt&eacute;se"
			dataDownload["target"]="/dataDownloadPage"
			topMenu.append(dataDownload)
			newsLetter={}
			newsLetter["label"]="H&iacute;rlev&eacute;l"
			newsLetter["target"]="/newsletter"
			topMenu.append(newsLetter)
		elif isUserCook(self):
			dailyMenu={}
			dailyMenu["label"]="Menu osszeallitas"
			dailyMenu["target"]="/menuEdit"
			topMenu.append(dailyMenu)
			weeklyMenu={}
			weeklyMenu["label"]="Menu attekintes"
			weeklyMenu["target"]="/menuWeekEdit"
			topMenu.append(weeklyMenu)
			payingOrders={}
			payingOrders["label"]="Rendelt"
			payingOrders["target"]="/chefReviewOrders"
			topMenu.append(payingOrders)
			ingredients={}
			ingredients["label"]="Alapanyagok"
			ingredients["target"]="/ingredient"
			topMenu.append(ingredients)
			categories={}
			categories["label"]="Ketegoriak"
			categories["target"]="/ingredientCategory"
			topMenu.append(categories)
			recepies={}
			recepies["label"]="Receptek"
			recepies["target"]="/dish"
			topMenu.append(recepies)
			dishCategories={}
			dishCategories["label"]="Fogasok"
			dishCategories["target"]=DISH_CATEGORY_URL
			topMenu.append(dishCategories)
		elif isUserDelivery(self):
			toDeliver={}
			toDeliver["label"]="Szallitando"
			toDeliver["target"]="/deliveryReviewOrders"
			topMenu.append(toDeliver)
		elif isUserAgent(self):
			agent={}
			agent["label"]="Ajanlott"
			agent["target"]="/referred"
			topMenu.append(agent)
		if len(topMenu) > 0:
			template_params={
				"menuItems":topMenu
			}
			ret=ret + jinja_environment.get_template('templates/admin/adminMenu.html').render(template_params)
		ret=ret + jinja_environment.get_template('templates/headers/header_part_one.html').render()
		#Set menu items
		menuItems=[]
		weeklyOrderMenu={}
		weeklyOrderMenu["label"]="Heti aj&#225;nlat"
		weeklyOrderMenu["target"]="/order"
		menuItems.append(weeklyOrderMenu)
		aboutUsMenu={}
		aboutUsMenu["label"]="R&oacute;lunk"
		aboutUsMenu["target"]="/about"
		menuItems.append(aboutUsMenu)
		servicesMenu={}
		servicesMenu["label"]="Szolg&aacute;ltat&aacute;sok"
		servicesMenu["target"]="/services"
		menuItems.append(servicesMenu)
		glutenMenu={}
		glutenMenu["label"]="Glut&eacute;n&eacute;rz&eacute;kenys&eacute;g"
		glutenMenu["target"]="/gluten"
		menuItems.append(glutenMenu)
		aboutDelivery={}
		aboutDelivery["label"]="Rendel&eacute;si felt&eacute;telek"
		aboutDelivery["target"]="/aboutDelivery"
		menuItems.append(aboutDelivery)
		faqMenu={}
		faqMenu["label"]="GY.I.K."
		faqMenu["target"]="/faq"
		#menuItems.append(faqMenu)
		template_params={
			"menuItems":menuItems
		}
		ret=ret+jinja_environment.get_template('templates/menu.html').render(template_params)
		ret=ret+getUserBox(self)
		ret=ret+jinja_environment.get_template('templates/headers/header_part_two.html').render()
		if forAnonymus or isUserLoggedIn(self):
			ret=ret+content
		else:
			ret=ret + "A tartalom nem jelenitheto meg"
		ret=ret+"</div>"
		ret=ret+jinja_environment.get_template('templates/headers/footer.html').render()
		self.response.out.write(ret)
	@webapp2.cached_property
	def session(self):
		# Returns a session using the default cookie key.
		return self.session_store.get_session()













