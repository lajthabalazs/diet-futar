'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import MenuItem
from google.appengine.ext import db
from cache_dish import getDish

MENU_ITEMS_FOR_DAY="MI_DAY"

def getDishKeyString(menuItem):
	ret = None
	try:
		ret = str(menuItem.dish.key())
	except:
		pass
	return ret

def createMenuItemData(menuItem):
	subItemKeys=[]
	for subItem in menuItem.components:
		subItemKeys.append(str(subItem.key()))
	menuItemObject={
		'key':str(menuItem.key()),
		'categoryKey':menuItem.categoryKey,
		'dishKey':getDishKeyString(menuItem),
		'price':menuItem.price,
		'day':menuItem.day,
		'containingMenuItem':None,
		'active':menuItem.active,
		'componentKeys':subItemKeys,
		'alterable':True
	}
	return menuItemObject

def dummyDish():
	dish = {
		'title' : 'UNKNOWN',
		'price' : 0,
		'energy' : 0,
		'fat' : 0,
		'carbs' : 0,
		'fiber' : 0,
		'protein' : 0, 
	}
	return dish


def getMenuItem(key):
	client = memcache.Client()
	menuItem = client.get(key)
	if menuItem == None:
		menuItemDb = MenuItem.get(key)
		if menuItemDb == None:
			return None
		menuItem = createMenuItemData(menuItemDb)
		client.set(key,menuItem)
	# Fetch dish for menu item and fetch subitems
	dish = getDish(menuItem['dishKey'])
	if dish == None:
		menuItem['dish'] = dummyDish()
		sumprice = 0
		energy = 0
		fat = 0
		carbs = 0
		fiber = 0
		protein = 0
	else:
		menuItem['dish'] = dish
		sumprice = dish['price']
		energy = dish['energy']
		fat = dish['fat']
		carbs = dish['carbs']
		fiber = dish['fiber']
		protein = dish['protein']
	# Calculate sum price
	components = []
	for subItemKey in menuItem['componentKeys']:
		component = getMenuItem(subItemKey)
		components.append(component)
		componentPrice = component['dish']['price']
		componentEnergy = component['dish']['energy']
		componentFat = component['dish']['fat']
		componentCarbs = component['dish']['carbs']
		componentFiber = component['dish']['fiber']
		componentProtein = component['dish']['protein']
		if componentPrice != None:
			sumprice = sumprice + componentPrice
		if componentEnergy != None:
			energy = energy + componentEnergy
		if componentFat != None:
			fat = fat + componentFat
		if componentCarbs != None:
			carbs = carbs + componentCarbs
		if componentFiber != None:
			fiber = fiber + componentFiber
		if componentProtein != None:
			protein = protein + componentProtein
	menuItem['sumprice'] = sumprice
	menuItem['energy'] = energy
	menuItem['fat'] = fat
	menuItem['carbs'] = carbs
	menuItem['fiber'] = fiber
	menuItem['protein'] = protein
	menuItem['components'] = components
	return menuItem
	
def getDaysMenuItems(day, categoryKey):
	client = memcache.Client()
	key = MENU_ITEMS_FOR_DAY+ str(day) + "_" + str(categoryKey)
	daysItems = client.get(key)
	if daysItems == None:
		menuItems = MenuItem.all().filter("day = ", day).filter("categoryKey = ", categoryKey).filter("containingMenuItem = ", None)
		daysItems=[]
		for menuItem in menuItems:
			menuItemObject = createMenuItemData(menuItem)
			daysItems.append(menuItemObject)
		client.set(key,daysItems)
	# Fetch dishes for menu items
	ret = []
	for menuItem in daysItems:
		menuItemObject=getMenuItem(menuItem['key']);
		ret.append(menuItemObject)
	return ret

def getDaysAvailableMenuItems(day):
	client = memcache.Client()
	key = MENU_ITEMS_FOR_DAY+ str(day)
	daysItems = client.get(key)
	if daysItems == None:
		menuItems = MenuItem.all().filter("day = ", day).filter("containingMenuItem = ", None)
		daysItems=[]
		for menuItem in menuItems:
			menuItemObject = createMenuItemData(menuItem)
			daysItems.append(menuItemObject)
		client.set(key,daysItems)
	# Fetch dishes for menu items
	ret = []
	for menuItem in daysItems:
		sumprice = 0
		dish = getDish(menuItem['dishKey'])
		menuItem['dish'] = dish
		if dish != None:
			sumprice = dish['price']
		components = []
		for subItemKey in menuItem['componentKeys']:
			component = getMenuItem(subItemKey)
			components.append(component)
			componentDish = getDish(component['dishKey'])
			if componentDish != None:
				sumprice = sumprice + componentDish['price']
		menuItem['sumprice'] = sumprice
		menuItem['components'] = components
		ret.append(menuItem)
	return ret

def addMenuItem(dishKey, day, containingMenuItem = None):
	# Store it in database
	dish=db.get(dishKey)
	menuItem=MenuItem()
	menuItem.day=day
	menuItem.dish=dish
	menuItem.price = dish.category.basePrice
	menuItem.categoryKey=str(dish.category.key())
	menuItem.containingMenuItem = containingMenuItem
	menuItem.put()
	# Store it in cache
	client = memcache.Client()
	client.set(str(menuItem.key()), createMenuItemData(menuItem))
	key = MENU_ITEMS_FOR_DAY+ str(menuItem.day) + "_" + str(menuItem.categoryKey)
	daysItems = client.get(key)
	#If we have something to update
	if daysItems != None and containingMenuItem == None:
		# Just add this menu item
		daysItems.append(createMenuItemData(menuItem))
		client.set(key,daysItems)
	availableKey = MENU_ITEMS_FOR_DAY+ str(menuItem.day)
	daysAvailableItems = client.get(availableKey)
	#If we have something to update
	if daysAvailableItems != None and containingMenuItem == None:
		# Just add this menu item
		daysAvailableItems.append(createMenuItemData(menuItem))
		client.set(availableKey,daysAvailableItems)

def modifyMenuItem(menuItem):
	client = memcache.Client()
	key = MENU_ITEMS_FOR_DAY+ str(menuItem.day) + "_" + str(menuItem.categoryKey)
	daysItems = client.get(key)
	menuItemKey=str(menuItem.key())
	#If we have something to update
	if daysItems != None:
		newItems = []
		for dayItem in daysItems:
			if (dayItem['key'] == menuItemKey):
				# Find item by key
				dayItem = createMenuItemData(menuItem)
				client.set(menuItemKey, dayItem)
			# Add menu item to new array
			newItems.append(dayItem)
		# Finally just add it to the cache 
		client.set(key,newItems)
	availableKey = MENU_ITEMS_FOR_DAY+ str(menuItem.day)
	daysAvailableItems = client.get(availableKey)
	#If we have something to update
	if daysAvailableItems != None:
		newItems = []
		for dayItem in daysAvailableItems:
			if (dayItem['key'] == menuItemKey):
				# Find item by key
				dayItem = createMenuItemData(menuItem)
			# Add menu item to new array
			newItems.append(dayItem)
		# Finally just add it to the cache 
		client.set(availableKey,newItems)
	# Modify item
	menuItemObject = createMenuItemData(menuItem)
	client.set(menuItemKey, menuItemObject)

def deleteMenuItem(menuItem):
	client = memcache.Client()
	key = MENU_ITEMS_FOR_DAY + str(menuItem.day) + "_" + str(menuItem.categoryKey)
	daysItems = client.get(key)
	menuItemKey=str(menuItem.key())
	#If we have something to update
	if daysItems != None:
		newItems = []
		for dayItem in daysItems:
			if (dayItem['key'] == menuItemKey):
				# Skip adding the item, and delete item from store
				client.delete(menuItemKey)
			else:
				# Add menu item to new array
				newItems.append(dayItem)
		# Finally just add it to the cache
		client.set(key,newItems)