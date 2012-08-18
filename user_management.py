'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.ext import db
import os
import jinja2

USER_KEY="dietUserKey"

LOGIN_ERROR_KEY="login_error"
LOGIN_ERROR_UNKNOWN_USER=1
LOGIN_ERROR_WRONG_PASSWORD=2

REGISTRATION_ERROR_KEY="login_error"
REGISTRATION_ERROR_EXISTING_USER=1
REGISTRATION_ERROR_WEAK_PASSWORD=2
REGISTRATION_ERROR_PASSWORD_DOESNT_MATCH=3

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def checkUserAdmin(handler):
	return True

def checkUserLoggedIn(handler):
	return True

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
		return(template.render(template_values))
	else:
		return(template.render())



















