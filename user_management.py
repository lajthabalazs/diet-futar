'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.ext import db
import os
import jinja2
from model import User, Role, ROLE_ADMIN

USER_KEY="dietUserKey"

LOGIN_ERROR_KEY="login_error"
LOGIN_ERROR_UNKNOWN_USER="Ismeretlen felhas"
LOGIN_ERROR_WRONG_PASSWORD="Hiba jelsz"

REGISTRATION_ERROR_EXISTING_USER="Letezo df"
REGISTRATION_ERROR_WEAK_PASSWORD=2
REGISTRATION_ERROR_PASSWORD_DOESNT_MATCH=3
LOGIN_NEXT_PAGE_KEY="next_page"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def isUserAdmin(handler):
	return isUserLoggedIn(handler)
	userKey = handler.session.get(USER_KEY,None)
	if (userKey != None):
	#If session has a user key, than return logged in
		user = User(db.get(userKey))
		if ((user!=None) and (user.role!=None)):
			return Role(user.role).name == ROLE_ADMIN
		else:
			return False
	else:
		return False

def isUserLoggedIn(handler):
	userKey = handler.session.get(USER_KEY,None)
	if (userKey != None):
	#If session has a user key, than return logged in
		return User(db.get(userKey))!=None
	else:
		return False

def clearLoginError(handler):
	loginError=None
	if (LOGIN_ERROR_KEY in handler.session):
		loginError=handler.session[LOGIN_ERROR_KEY]
		del handler.session[LOGIN_ERROR_KEY]
	return loginError

'''
If user is not logged in, returns a login box with a login and a register button
Else returns the users personal data box with links
'''
def getUserBox(handler):
	userKey=handler.session.get(USER_KEY,None)
	template = jinja_environment.get_template('templates/loginBox.html')
	if (userKey != None):
	#If session has a user key, than return logged in
		user = db.get(userKey)
		template_values = {
			'user': user
		}
		clearLoginError(handler)
		return(template.render(template_values))
	elif(LOGIN_ERROR_KEY in handler.session):
		template_values = {
			LOGIN_ERROR_KEY: handler.session[LOGIN_ERROR_KEY]
		}
		clearLoginError(handler)
		return(template.render(template_values))
	else:
		clearLoginError(handler)
		return(template.render())



















