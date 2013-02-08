#!/usr/bin/env python

import jinja2
import os

from user_management import isUserAdmin, LOGIN_NEXT_PAGE_KEY
from xmlrpclib import datetime
from model import Books
from base_handler import BaseHandler, getFormDate, getMonday, dayNames, FORM_DAY

ACTUAL_ORDER="actualOrder"

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class WeeklyIncome(BaseHandler):
	URL = '/weeklyIncome'
	def get(self):
		if(not isUserAdmin(self)):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		monday = getMonday(getFormDate(self))
		prevMonday=monday + datetime.timedelta(days=-7)
		nextMonday=monday + datetime.timedelta(days=7)
		days=[]
		books = Books.all().filter("monday = ", monday);
		weeklyIncome = books.get()
		if weeklyIncome == None:
			weeklyIncome = Books()
		for i in range(0,5):
			actualDayObject={}
			actualDate=monday+datetime.timedelta(days=i)
			actualDayObject["day"] = dayNames[i]
			actualDayObject["index"] = i
			actualDayObject["date"] = actualDate
			days.append(actualDayObject)
		days[0]['total'] = weeklyIncome.mondayIncome
		days[1]['total'] = weeklyIncome.tuesdayIncome
		days[2]['total'] = weeklyIncome.wednesdayIncome
		days[3]['total'] = weeklyIncome.thursdayIncome
		days[4]['total'] = weeklyIncome.fridayIncome
		template_values={
			'days': days,
			'monday':monday,
			'prev':prevMonday,
			'next':nextMonday
		}
		template = jinja_environment.get_template('templates/admin/weeklyIncome.html')
		self.printPage("Bev&eacute;tel", template.render(template_values), False, False)
	def post(self):
		monday = getMonday(getFormDate(self))
		books = Books.all().filter("monday = ", monday);
		weeklyIncome = books.get()
		if weeklyIncome == None:
			weeklyIncome = Books()
		weeklyIncome.monday = monday
		weeklyIncome.mondayIncome = int(self.request.get("value_0"))
		weeklyIncome.tuesdayIncome = int(self.request.get("value_1"))
		weeklyIncome.wednesdayIncome = int(self.request.get("value_2"))
		weeklyIncome.thursdayIncome = int(self.request.get("value_3"))
		weeklyIncome.fridayIncome = int(self.request.get("value_4"))
		weeklyIncome.put()
		self.redirect(self.URL +"?" + FORM_DAY +"=" + str(monday))
		
		
class WeeklyOnsiteIncome(BaseHandler):
	URL = '/weeklyOnsiteIncome'
	def get(self):
		if not isUserAdmin(self):
			self.session[LOGIN_NEXT_PAGE_KEY] = self.URL
			self.redirect("/")
			return
		today=datetime.date.today()
		monday = getMonday(today)
		maxWeeks = 20
		weekTotals = []
		daysOfWeek = [
			{'name':dayNames[0], 'dailyTotals':[]},
			{'name':dayNames[1], 'dailyTotals':[]},
			{'name':dayNames[2], 'dailyTotals':[]},
			{'name':dayNames[3], 'dailyTotals':[]},
			{'name':dayNames[4], 'dailyTotals':[]},
		]
		for i in range(0, maxWeeks):
			weekTotal = 0
			actualMonday = monday + datetime.timedelta(days = (i - maxWeeks + 2) * 7)
			books = Books.all().filter("monday = ", actualMonday)
			weeklyIncome = books.get()
			if weeklyIncome == None:
				weeklyIncome = Books()
			daysOfWeek[0]['dailyTotals'].append(weeklyIncome.mondayIncome)
			weekTotal = weekTotal + weeklyIncome.mondayIncome
			daysOfWeek[1]['dailyTotals'].append(weeklyIncome.tuesdayIncome)
			weekTotal = weekTotal + weeklyIncome.tuesdayIncome
			daysOfWeek[2]['dailyTotals'].append(weeklyIncome.wednesdayIncome)
			weekTotal = weekTotal + weeklyIncome.wednesdayIncome
			daysOfWeek[3]['dailyTotals'].append(weeklyIncome.thursdayIncome)
			weekTotal = weekTotal + weeklyIncome.thursdayIncome
			daysOfWeek[4]['dailyTotals'].append(weeklyIncome.fridayIncome)
			weekTotal = weekTotal + weeklyIncome.fridayIncome
			weekTotalITem = {
				'total' : weekTotal,
				'monday' : actualMonday
			}
			weekTotals.append(weekTotalITem)
		template_values = {
			'weekTotals':weekTotals,
			'daysOfWeek' : daysOfWeek
		}
		template = jinja_environment.get_template('templates/admin/onsiteIncomeOverview.html')
		self.printPage("Rendel&eacute;sek", template.render(template_values), False, False)
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		