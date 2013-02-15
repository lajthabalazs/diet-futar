from cache_menu_item import getMenuItem
from cache_composit import getComposit
from model import UserWeekOrder
def isMenuItem(key):
	# What better way than to get it from cache
	return (getMenuItem(key) != None)

def getOrderedItemsFromWeekData (weeks, day):
	orderedMenuItemIndexes={}
	orderedCompositIndexes={}
	orderedMenuItems=[]
	orderedComposits=[]
	for week in weeks:
		for menuItemString in week.orderedMenuItems:
			parts = menuItemString.split(" ")
			orderedQuantity = int(parts[0])
			menuItemKey = parts[1]
			menuItem = getMenuItem(menuItemKey)
			if menuItem != None and menuItem['day'] == day:
				if orderedMenuItemIndexes.has_key(menuItemKey):
					index = orderedMenuItemIndexes.get(menuItemKey)
					orderedMenuItems[index]['orderedQuantity'] = orderedQuantity + orderedMenuItems[index]['orderedQuantity']
				else:
					menuItem['orderedQuantity'] = orderedQuantity
					menuItem['isMenuItem'] = True
					orderedMenuItemIndexes[menuItemKey] = len(orderedMenuItems)
					orderedMenuItems.append(menuItem)
		for compositString in week.orderedComposits:
			parts = compositString.split(" ")
			orderedQuantity = int(parts[0])
			compositKey = parts[1]
			composit = getComposit(compositKey)
			if composit != None and composit['day'] == day:
				if orderedCompositIndexes.has_key(compositKey):
					index = orderedCompositIndexes.get(compositKey)
					orderedComposits[index]['orderedQuantity'] = orderedQuantity + orderedComposits[index]['orderedQuantity']
				else:
					composit['orderedQuantity'] = orderedQuantity
					composit['isMenuItem'] = False
					orderedCompositIndexes[compositKey] = len(orderedComposits)
					orderedComposits.append(composit)
	orderedItems = []
	orderedItems.extend(orderedComposits)
	orderedItems.extend(orderedMenuItems)
	return orderedItems

def getOrderAddress (week, day):
	if week == None:
		return None
	if day.weekday() == 0:
		return week.mondayAddress
	elif day.weekday() == 1:
		return week.tuesdayAddress
	elif day.weekday() == 2:
		return week.wednesdayAddress
	elif day.weekday() == 3:
		return week.thursdayAddress
	elif day.weekday() == 4:
		return week.fridayAddress
	elif day.weekday() == 5:
		return week.saturdayAddress
	elif day.weekday() == 6:
		return week.sundayAddress

def getOrderComment (week, day):
	if week == None:
		return None
	if day.weekday() == 0:
		return week.mondayComment
	elif day.weekday() == 1:
		return week.tuesdayComment
	elif day.weekday() == 2:
		return week.wednesdayComment
	elif day.weekday() == 3:
		return week.thursdayComment
	elif day.weekday() == 4:
		return week.fridayComment
	elif day.weekday() == 5:
		return week.saturdayComment
	elif day.weekday() == 6:
		return week.sundayComment

def getOrdersFromWeeks(weeks):
	orders={}
	for week in weeks:
		for orderedComposit in week.orderedComposits:
			parts = orderedComposit.split(" ")
			orderedQuantity = int(parts[0])
			orderedItemKey = parts[1]
			oldValue = 0
			try:
				oldValue = int(orders[orderedItemKey])
			except:
				pass
			orders[orderedItemKey] = orderedQuantity + oldValue
		for orderedMenuItem in week.orderedMenuItems:
			parts = orderedMenuItem.split(" ")
			orderedQuantity = int(parts[0])
			orderedItemKey = parts[1]
			oldValue = 0
			try:
				oldValue = int(orders[orderedItemKey])
			except:
				pass
			orders[orderedItemKey] = orderedQuantity + oldValue
	return orders

def getOrdersForWeek(monday):
	weeks = UserWeekOrder.all().filter("monday = ", monday)
	return getOrdersFromWeeks(weeks)

def getUserOrdersForWeek(user, monday):
	weeks = user.weeks.filter("monday = ", monday)
	return getOrdersFromWeeks(weeks)

def getOrderTotal(weeks):
	orderTotal = 0
	for week in weeks:
		for orderedComposit in week.orderedComposits:
			parts = orderedComposit.split(" ")
			orderedQuantity = int(parts[0])
			orderedItemKey = parts[1]
			composit = getComposit(orderedItemKey)
			if composit != None:
				if composit['price'] != 0:
					orderTotal = orderTotal + composit['price'] * orderedQuantity
		for orderedMenuItem in week.orderedMenuItems:
			parts = orderedMenuItem.split(" ")
			orderedQuantity = int(parts[0])
			orderedItemKey = parts[1]
			menuItem = getMenuItem(orderedItemKey)
			if menuItem != None:
				if menuItem['price'] != 0:
					orderTotal = orderTotal + menuItem['price'] * orderedQuantity
	return orderTotal

