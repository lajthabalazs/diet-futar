#!/usr/bin/env python

import jinja2
import os

from base_handler import BaseHandler, timeZone
from model import User
from user_management import isUserAdmin, LOGIN_NEXT_PAGE_KEY, getUser
from xmlrpclib import datetime
from timeit import itertools

ACTUAL_ORDER="actualOrder"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def getLastOrderDate(x):
	return x.lastOrder or x.registrationDate
 
class CRMMainPage(BaseHandler):
	URL = '/crmMainPage'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		template = jinja_environment.get_template('templates/crm/crmMainPage.html')
		self.printPage("Felhasznalok", template.render(), False, False)

class CRMUsersWithTasks(BaseHandler):
	URL = '/crmUsersWithTasks'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		today = datetime.datetime.now(timeZone)
		twoWeeksAgo = today + datetime.timedelta(days = - 14)
		unseenUsers = User.all().filter("lastOrder < ", twoWeeksAgo)
		unseenUsersOrdered = sorted(unseenUsers, key=getLastOrderDate)
		taskedUsers = User.all().filter("taskList >= ", None)
		
		template_values={
			'users': itertools.chain(taskedUsers, unseenUsersOrdered),
		}
		template = jinja_environment.get_template('templates/crm/crmTaskList.html')
		self.printPage("Felhaszn&aacute;l&oacute;k", template.render(template_values), False, False)

class CRMInitUsers(BaseHandler):
	URL = '/crmInitUsers'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		users = User.all()
		for user in users:
			monday = None
			week = user.weeks.order("-monday").get()
			if (week != None):
				monday = week.monday
			user.lastOrder = monday
			user.lastOrderFlag = True
			if (user.registrationDate !=None):
				try:
					user.registrationDate = datetime.datetime.combine(user.registrationDate, datetime.time())
					print user.familyName + " " + user.givenName + " OK<br/>"
				except:
					print user.familyName + " " + user.givenName + " FAILED<br/>"
					pass
			user.put()
		#self.redirect(CRMUsersWithTasks.URL)

class CRMUserDetails(BaseHandler):
	URL = '/crmUserDetails'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		userKey = self.request.get("userKey")
		user = User.get(userKey)
		processedHistory = []
		for entry in user.contactHistory:
			parts = entry.split(" ", 3)
			processedEntry = {}
			processedEntry['date'] = parts[1]
			processedEntry['admin'] = User.get(parts[2])
			processedEntry['message'] = parts[3]
			processedHistory.append(processedEntry)
		user.processedHistory = sorted(processedHistory, key=lambda entry:entry['date'], reverse = True)

		processedTasks = []
		for entry in user.taskList:
			parts = entry.split(" ", 4)
			processedEntry = {}
			processedEntry['id'] = parts[0]
			processedEntry['date'] = parts[1]
			processedEntry['doneDate'] = parts[2]
			processedEntry['admin'] = User.get(parts[3])
			processedEntry['message'] = parts[4]
			processedTasks.append(processedEntry)
		user.processedTasks = sorted(processedTasks, key=lambda entry:entry['date'], reverse = True)

		processedDoneTasks = []
		for entry in user.doneTasks:
			parts = entry.split(" ", 4)
			processedEntry = {}
			processedEntry['id'] = parts[0]
			processedEntry['date'] = parts[1]
			processedEntry['doneDate'] = parts[2]
			processedEntry['admin'] = User.get(parts[3])
			processedEntry['message'] = parts[4]
			processedDoneTasks.append(processedEntry)
		user.processedDoneTasks = sorted(processedDoneTasks, key=lambda entry:entry['date'], reverse = True)
		template_values={
			'user': user,
		}
		template = jinja_environment.get_template('templates/crm/userOverview.html')
		self.printPage("Felhasznal&oacute; reszletei", template.render(template_values), False, False)

class AddHistoryEntry(BaseHandler):
	URL = '/addHistoryEntry'
	def post(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		admin = getUser(self)
		userKey = self.request.get("userKey")
		message = self.request.get("historyText")
		user = User.get(userKey)
		actualTime = datetime.datetime.now(timeZone)
		history = user.contactHistory
		history.append(str(len(history)) + " " + actualTime.strftime("%Y-%m-%d_%H:%M") + " " + str(admin.key()) + " " + message)
		user.contactHistory = history
		user.lastContact = actualTime
		user.put()
		self.redirect(CRMUserDetails.URL + "?userKey=" + str(user.key()))

class AddTaskToUser(BaseHandler):
	URL = '/addTaskToUser'
	def post(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		admin = getUser(self)
		userKey = self.request.get("userKey")
		user = User.get(userKey)
		message = self.request.get("task")
		if len(message) == 0:
			message = "Nincs feladat ?!"
		actualTime = datetime.datetime.now(timeZone)
		taskList = user.taskList
		taskList.append(str(len(taskList)) + " " + actualTime.strftime("%Y-%m-%d_%H:%M") + " NOT_DONE " + str(admin.key()) + " " + message)
		user.taskList = taskList
		user.put()
		self.redirect(CRMUserDetails.URL + "?userKey=" + str(user.key()))

class TaskAccomplished(BaseHandler):
	URL = '/taskAccomplished'
	def post(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		admin = getUser(self)
		userKey = self.request.get("userKey")
		user = User.get(userKey)
		taskId = self.request.get("taskId")
		actualTime = datetime.datetime.now(timeZone)
		taskList = user.taskList
		newTaskList = []
		doneTask = None
		for task in taskList:
			if task.encode('ascii','ignore').startswith(str(taskId) + " "):
				doneTask = task
			else:
				newTaskList.append(task)
		if doneTask != None:
			actualTime = datetime.datetime.now(timeZone)
			parts = doneTask.split(" ", 4)
			updatedTaskString = parts[0] + " " + parts[1] + " " + actualTime.strftime("%Y-%m-%d_%H:%M") + " " + str(admin.key()) + " " + parts[4] 
			doneTasks = user.doneTasks
			doneTasks.append(updatedTaskString)
			user.taskList = newTaskList
			user.doneTasks = doneTasks
			user.put()
		self.redirect(CRMUserDetails.URL + "?userKey=" + str(user.key()))




