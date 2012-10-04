'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.ext import db
import os
import jinja2
from model import User, ROLE_ADMIN

USER_KEY="dietUserKey"
USER="user"

LOGIN_ERROR_KEY="login_error"
LOGIN_ERROR_UNKNOWN_USER="Ismeretlen felhasznalo"
LOGIN_ERROR_WRONG_PASSWORD="Hiba jelsz"
LOGIN_ERROR_NOT_ACTIVATED="Nem aktivalt felhasznalo"
REGISTRATION_ERROR_KEY="registration_error"
REGISTRATION_ERROR_EXISTING_USER="Letezo felhasznalo"
REGISTRATION_ERROR_WEAK_PASSWORD="Gyenge jelszo"
REGISTRATION_ERROR_PASSWORD_DOESNT_MATCH="Ket jelszo nem egyezik"
REGISTRATION_ERROR_USER_NAME_NOT_FILLED="Felhasznalo neve kotelezo"
LOGIN_NEXT_PAGE_KEY="next_page"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def isUserAdmin(handler):
	userKey = handler.session.get(USER_KEY,None)
	if (userKey != None):
	#If session has a user key, than return logged in
		user = User.get(userKey)
		if ((user!=None) and (user.roleName!=None)):
			return user.roleName == ROLE_ADMIN
		else:
			return False
	else:
		return False

def isUserLoggedIn(handler):
	userKey = handler.session.get(USER_KEY,None)
	if (userKey != None):
	#If session has a user key, than return logged in
		return User.get(userKey)!=None
	else:
		return False

def clearLoginError(handler):
	loginError=None
	if (LOGIN_ERROR_KEY in handler.session):
		loginError=handler.session[LOGIN_ERROR_KEY]
		del handler.session[LOGIN_ERROR_KEY]
	return loginError

def clearRegistrationError(handler):
	loginError=None
	if (REGISTRATION_ERROR_KEY in handler.session):
		loginError=handler.session[REGISTRATION_ERROR_KEY]
		del handler.session[REGISTRATION_ERROR_KEY]
	if (USER in handler.session):
		del handler.session[USER]
	return loginError

def getUser(handler):
	userKey=handler.session.get(USER_KEY,None)
	if (userKey != None):
	#If session has a user key, than return logged in
		user = db.get(userKey)
		return user
	else:
		return None
	
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



















