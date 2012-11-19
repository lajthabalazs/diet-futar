'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
import webapp2
from webapp2_extras import sessions
from user_management import getUserBox, isUserLoggedIn, isUserAdmin, isUserCook, isUserDelivery,\
	isUserAgent
import jinja2
import os
from keys import DISH_CATEGORY_URL
import datetime
from timezone import USTimeZone

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
LAST_ORDER_HOUR=12
timeZone=USTimeZone(1, "CEST", "CEST", "CEST")

def getFirstOrderableDate(handler):
	today=datetime.date.today()
	now=datetime.datetime.now(timeZone)
	firstOrderableDay = today
	if now.hour > LAST_ORDER_HOUR:
		firstOrderableDay=today+datetime.timedelta(days=1)
	return firstOrderableDay;
# Returns the first date user can order
def getOrderBaseDate(handler):
	day=datetime.date.today()	
	requestDay=handler.request.get('day')
	if ((requestDay != None) and (requestDay != "")):
		parts=requestDay.rsplit("-")
		day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
	else:
		calendar=day.isocalendar()
		#Organize into days
		if calendar[2]==4 and datetime.datetime.now().hour > 16:
			day=day+datetime.timedelta(days=4)
		elif calendar[2]==5:
			day=day+datetime.timedelta(days=3)
		elif calendar[2]==6:
			day=day+datetime.timedelta(days=2)
		elif calendar[2]==7:
			day=day+datetime.timedelta(days=1)
	return day

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
			day=day+datetime.timedelta(days=4)
		elif calendar[2]==5:
			day=day+datetime.timedelta(days=3)
		elif calendar[2]==6:
			day=day+datetime.timedelta(days=2)
		elif calendar[2]==7:
			day=day+datetime.timedelta(days=1)
	return day

# Returns the day indicated by the posted form if any otherwise the current day
def getFormDate(handler):
	day=datetime.date.today()
	requestDay=handler.request.get('formDay')
	if ((requestDay != None) and (requestDay != "")):
		parts=requestDay.rsplit("-")
		day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
	return day

class BaseHandler(webapp2.RequestHandler):
	def dispatch(self):
		# Get a session store for this request.
		self.session_store = sessions.get_store(request=self.request)
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
		ret=jinja_environment.get_template('templates/header_part_zero.html').render(template_params)
		topMenu=[]
		if isUserAdmin(self):
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
			toMake={}
			toMake["label"]="K&#233;sz&#237;tend&#337;"
			toMake["target"]="/chefReviewToMake"
			topMenu.append(toMake)
			toDeliver={}
			toDeliver["label"]="Szallitando"
			toDeliver["target"]="/deliveryReviewOrders"
			topMenu.append(toDeliver)			
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
			userList={}
			userList["label"]="Felhasznalok"
			userList["target"]="/userList"
			topMenu.append(userList)
			agent={}
			agent["label"]="Ajanlott"
			agent["target"]="/referred"
			topMenu.append(agent)
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
			toMake={}
			toMake["label"]="K&#233;sz&#237;tend&#337;"
			toMake["target"]="/chefReviewToMake"
			topMenu.append(toMake)
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
			ret=ret + jinja_environment.get_template('templates/admin_menu.html').render(template_params)
		ret=ret + jinja_environment.get_template('templates/header_part_one.html').render()
		#Set menu items
		menuItems=[]
		weeklyOrderMenu={}
		weeklyOrderMenu["label"]="Heti aj&#225;nlat"
		weeklyOrderMenu["target"]="/order"
		menuItems.append(weeklyOrderMenu)
		if (isUserLoggedIn(self)):
			ownMenu={}
			ownMenu["label"]="Men&#252;m"
			ownMenu["target"]="/personalMenu"
			menuItems.append(ownMenu)
		aboutDelivery={}
		aboutDelivery["label"]="Rendel&eacute;s"
		aboutDelivery["target"]="/aboutDelivery"
		menuItems.append(aboutDelivery)
		template_params={
			"menuItems":menuItems
		}
		ret=ret+jinja_environment.get_template('templates/menu.html').render(template_params)
		ret=ret+getUserBox(self)
		ret=ret+jinja_environment.get_template('templates/header_part_two.html').render()
		if forAnonymus or isUserLoggedIn(self):
			ret=ret+content
		else:
			ret=ret + "A tartalom nem jelenitheto meg"
		ret=ret+"</div>"
		ret=ret+jinja_environment.get_template('templates/footer.html').render()
		self.response.out.write(ret)
	@webapp2.cached_property
	def session(self):
		# Returns a session using the default cookie key.
		return self.session_store.get_session()