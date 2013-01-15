from google.appengine.ext import db
import jinja2
import os
from base_handler import BaseHandler
from user_management import isUserAdmin
import time
from google.appengine.api.logservice import logservice
from google.appengine.api.logservice.logservice import fetch

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
		template_values = {
			'logLines':logs
		}
		template = jinja_environment.get_template('templates/log/logLines.html')
		self.printPage("Logs", template.render(template_values), False, False)