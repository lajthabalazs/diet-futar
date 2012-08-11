#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.api import users
import google.appengine.ext.webapp.util

class LoginRequiredHandler(webapp.RequestHandler):
	def get(self):
		continue_url, = self.request.get('continue',allow_multiple=True)
		self.redirect(users.create_login_url())

def main():
	application = webapp.WSGIApplication([('/_ah/login_required', LoginRequiredHandler),], debug=True)
	webapp.util.run_wsgi_app(application)

if __name__ == '__main__':
	main()