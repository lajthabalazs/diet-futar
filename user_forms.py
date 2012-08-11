'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from base_handler import BaseHandler

class Login(BaseHandler):
	def get(self):
		print "Login"