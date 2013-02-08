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
from model import Maintenence
from string import replace, split
from cache_zips import getZipCodeEntry
import logging
from orderHelper import isMenuItem
from cache_menu_item import getMenuItem
from cache_composit import getComposit

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
LAST_ORDER_HOUR=11
timeZone=USTimeZone(1, "CEST", "CEST", "CEST")
dayNames=["H&#233;tf&#337;","Kedd","Szerda","Cs&#252;t&#246;rt&#246;k","P&#233;ntek","Szombat","Vas&#225;rnap"]
FORM_DAY = "formDay"

def getZipBasedDeliveryCost(code, price):
	costs = getZipCodeEntry(code)
	if costs != None:
		if (price < costs['limit']):
			return costs['cost']
		else:
			return 0
	else:
		if (price < 5000):
			return 1000
		else:
			return 0
	
def getZipBasedDeliveryLimit(code):
	costs = getZipCodeEntry(code)
	if costs != None:
		return costs['limit']
	else:
		return 5000
	
def logInfo(handler, url, message):
	template_values_for_logging = {
		"user":getUser(handler),
		"url":url,
		"message":message,
		'now':datetime.datetime.now(timeZone)
	}
	
	loggingTemplate = jinja_environment.get_template('templates/log/basic_message.txt')
	logging.info(loggingTemplate.render(template_values_for_logging))

def getFirstOrderableDate(handler):
	today=datetime.date.today()
	now=datetime.datetime.now(timeZone)
	firstOrderableDay = today
	if now.hour > LAST_ORDER_HOUR:
		firstOrderableDay=today+datetime.timedelta(days=1)
	return firstOrderableDay;

def getMonday(day):
	return day + datetime.timedelta(days = - day.weekday())
	
# Returns the first date user can order
def getOrderBaseDate(handler):
	day=datetime.date.today()	
	requestDay=handler.request.get('day')
	if ((requestDay != None) and (requestDay != "")):
		parts=requestDay.rsplit("-")
		day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
	else:
		#Organize into days
		if day.weekday()==4:
			pass
		#	day=day+datetime.timedelta(days=3)
		elif day.weekday()==5:
			day=day+datetime.timedelta(days=2)
		elif day.weekday()==6:
			day=day+datetime.timedelta(days=1)
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
			if isMenuItem(key):
				menuItem = getMenuItem(key)
				actualDay = menuItem['day']
			else:
				composit = getComposit(key)
				actualDay = composit['day']
			if (firstDay == None):
				firstDay = actualDay
			elif firstDay > actualDay:
				firstDay = actualDay
	if firstDay == None:
		return getOrderBaseDate(handler)
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

# Returns the day indicated by the posted form if any otherwise the current day
def getFormDate(handler):
	day=datetime.date.today()
	requestDay=handler.request.get(FORM_DAY)
	if ((requestDay != None) and (requestDay != "")):
		parts=requestDay.rsplit("-")
		day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
	return day

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
			onsiteIncome["label"]="Helysz&iacute;ni bev&eacute;tel"
			onsiteIncome["target"]="/weeklyIncome"
			topMenu.append(onsiteIncome)
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
		aboutDelivery={}
		aboutDelivery["label"]="Rendel&eacute;si felt&eacute;telek"
		aboutDelivery["target"]="/aboutDelivery"
		menuItems.append(aboutDelivery)
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