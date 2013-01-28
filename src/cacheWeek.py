'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import UserWeekOrder, User
from orderHelper import getOrderTotal

USERS_KEY = "userList"

def createWeekDb (weekDb):
	weekTotal = getOrderTotal([weekDb])
	week={
		'key':str(weekDb.key()),
		'user':str(weekDb.user.key()),
		'monday':weekDb.monday,
		'orderedComposits':weekDb.orderedComposits,
		'orderedMenuItems':weekDb.orderedMenuItems,
		'weekTotal':weekTotal
	}
	# TODO cache week total
	return week

def getUserWeekForDay(key, monday):
	user = getUser(key)
	total = 0
	for week in user['weeks']:
		if (week['monday'] == monday):
			total = total + week['weekTotal']
	week = {
		'weekTotal':total
	}
	return week
	

def createUser(userDb):
	weeks = []
	for weekDb in userDb.weeks:
		weeks.append(createWeekDb(weekDb))
	user = {
		'key':str(userDb.key()),
		'familyName':userDb.familyName,
		'givenName':userDb.givenName,
		'activated':userDb.activated,
		'registrationDate':userDb.registrationDate,
		'role':userDb.role,
		'weeks':weeks
	}
	return user

def getUserWeek(key):
	client = memcache.Client()
	week = client.get(str(key))
	# If not in memcache, does nothing
	if week != None:
		return week
	else:
		weekDb = UserWeekOrder.get(key)
		if (weekDb == None):
			return None
		week = createWeekDb(weekDb)
		client.add(str(key), week)
		return week

def updateUser(userDb):
	client = memcache.Client()
	users = client.get(USERS_KEY)
	key = str(userDb.key())
	if users != None:
		return
	newUsers = []
	for user in users:
		if user['key'] == key:
			newUsers.append(createUser(userDb))
		else:
			newUsers.append(user)
	client.add(USERS_KEY, newUsers)

def deleteUserWeek(userDb, key):
	client = memcache.Client()
	client.delete(key)
	updateUser(userDb)

def modifyUserWeek(weekDb):
	key=str(weekDb.key())
	client = memcache.Client()
	week = createWeekDb(weekDb)
	client.add(str(key), week)
	updateUser(weekDb.user)

def getUser(key):
	client = memcache.Client()
	user = client.get(key)
	if user == None:
		userDb = User.get(key)
		if userDb != None:
			user = createUser(userDb)
			client.add(key, user)
	return user


def getUsers():
	client = memcache.Client()
	users = client.get(USERS_KEY)
	if users == None:
		users = []
		usersDb = User.all()
		for userDb in usersDb:
			users.append(createUser(userDb))
		client.add(USERS_KEY, users)
	return users