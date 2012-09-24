'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
import webapp2
from webapp2_extras import sessions
from user_management import getUserBox, isUserLoggedIn, isUserAdmin
import jinja2
import os
from keys import DISH_CATEGORY_URL

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

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
		ret=jinja_environment.get_template('templates/header.html').render(template_params)
		#Set menu items
		menuItems=[]
		weeklyOrderMenu={}
		weeklyOrderMenu["label"]="Heti ajanlat"
		weeklyOrderMenu["target"]="/order"
		menuItems.append(weeklyOrderMenu)
		if (isUserLoggedIn(self)):
			profile={}
			profile["label"]="Profil"
			profile["target"]="/profile"
			menuItems.append(profile)
		if (isUserLoggedIn(self)):
			ownMenu={}
			ownMenu["label"]="Menum"
			ownMenu["target"]="/personalMenu"
			menuItems.append(ownMenu)
		if (isUserAdmin(self)):
			weeklyMenu={}
			weeklyMenu["label"]="Menu osszeallitas"
			weeklyMenu["target"]="/menuEdit"
			menuItems.append(weeklyMenu)
			payingOrders={}
			payingOrders["label"]="Rendelt"
			payingOrders["target"]="/chefReviewOrders"
			menuItems.append(payingOrders)
			toMake={}
			toMake["label"]="Keszitendo"
			toMake["target"]="/chefReviewToMake"
			menuItems.append(toMake)
			ingredients={}
			ingredients["label"]="Alapanyagok"
			ingredients["target"]="/ingredient"
			menuItems.append(ingredients)
			categories={}
			categories["label"]="Ketegoriak"
			categories["target"]="/ingredientCategory"
			menuItems.append(categories)
			recepies={}
			recepies["label"]="Receptek"
			recepies["target"]="/dish"
			menuItems.append(recepies)
			dishCategories={}
			dishCategories["label"]="Fogasok"
			dishCategories["target"]=DISH_CATEGORY_URL
			menuItems.append(dishCategories)
		about={}
		about["label"]="Rolunk"
		about["target"]="/about"
		menuItems.append(about)
		template_params={
			"pageTitle":title,
			"menuItems":menuItems
		}
		ret=ret+jinja_environment.get_template('templates/menu.html').render(template_params)
		ret=ret+getUserBox(self)
		ret=ret+"<span class='clear'></span><div id='content'>"
		if(forAnonymus or (forLoggedIn and isUserLoggedIn(self)) or isUserAdmin(self)):
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
