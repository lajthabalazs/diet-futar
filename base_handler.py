'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
import webapp2
from webapp2_extras import sessions
from user_management import getUserBox, isUserLoggedIn, isUserAdmin, USER_KEY
import jinja2
import os
from keys import DISH_CATEGORY_URL
from model import User
from google.appengine.ext import db

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
		ret=jinja_environment.get_template('templates/header_part_zero.html').render(template_params)
		if isUserAdmin(self):
			adminMenuItems=[]
			weeklyMenu={}
			weeklyMenu["label"]="Menu osszeallitas"
			weeklyMenu["target"]="/menuEdit"
			adminMenuItems.append(weeklyMenu)
			payingOrders={}
			payingOrders["label"]="Rendelt"
			payingOrders["target"]="/chefReviewOrders"
			adminMenuItems.append(payingOrders)
			toMake={}
			toMake["label"]="K&#233;sz&#237;tend&#337;"
			toMake["target"]="/chefReviewToMake"
			adminMenuItems.append(toMake)
			toDeliver={}
			toDeliver["label"]="Szallitando"
			toDeliver["target"]="/deliveryReviewOrders"
			adminMenuItems.append(toDeliver)			
			ingredients={}
			ingredients["label"]="Alapanyagok"
			ingredients["target"]="/ingredient"
			adminMenuItems.append(ingredients)
			categories={}
			categories["label"]="Ketegoriak"
			categories["target"]="/ingredientCategory"
			adminMenuItems.append(categories)
			recepies={}
			recepies["label"]="Receptek"
			recepies["target"]="/dish"
			adminMenuItems.append(recepies)
			dishCategories={}
			dishCategories["label"]="Fogasok"
			dishCategories["target"]=DISH_CATEGORY_URL
			adminMenuItems.append(dishCategories)
			userList={}
			userList["label"]="Felhasznalok"
			userList["target"]="/userList"
			adminMenuItems.append(userList)
			template_params={
				"menuItems":adminMenuItems
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
