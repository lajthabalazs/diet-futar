'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
import webapp2
from webapp2_extras import sessions
from user_management import getUserBox, isUserLoggedIn, isUserAdmin, isUserCook, isUserDelivery
import jinja2
import os
from keys import DISH_CATEGORY_URL
import datetime

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# Returns the first date user can order or the date indicated by the request
def getBaseDate(handler):
	day=datetime.date.today()	
	requestDay=handler.request.get('day')
	if ((requestDay != None) and (requestDay != "")):
		parts=requestDay.rsplit("-")
		day=datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
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
			weeklyMenu={}
			weeklyMenu["label"]="Menu osszeallitas"
			weeklyMenu["target"]="/menuEdit"
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
		elif isUserCook(self):
			weeklyMenu={}
			weeklyMenu["label"]="Menu osszeallitas"
			weeklyMenu["target"]="/menuEdit"
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
		about={}
		about["label"]="R&#243;lunk"
		about["target"]="/about"
		menuItems.append(about)
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
		self.response.out.write(ret);
	@webapp2.cached_property
	def session(self):
		# Returns a session using the default cookie key.
		return self.session_store.get_session()
