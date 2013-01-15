from google.appengine.ext import db
import jinja2
import os
from base_handler import BaseHandler
from user_management import isUserAdmin
import time
from google.appengine.api.logservice import logservice
from google.appengine.api.logservice.logservice import fetch
import codecs

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class ViewLogs(BaseHandler):
	def get(self):
		if not isUserAdmin(self):
			self.redirect("/")
			return
		now = int(time.mktime(time.gmtime()))
		# Fetch 24 hours of logs
		start = now - 3600 * 24
		logs = fetch(start_time=start, end_time=now, minimum_log_level=logservice.LOG_LEVEL_INFO, include_incomplete=False, include_app_logs=True)
		messages = []
		for log in logs:
			for appLog in log.app_logs:
				message = unicode(appLog.message.strip(codecs.BOM_UTF8), 'utf-8')
				if message.startswith("2013"):
					messages.append(message)
		template_values = {
			'messages':messages
		}
		template = jinja_environment.get_template('templates/log/logLines.html')
		self.printPage("Logs", template.render(template_values), False, False)