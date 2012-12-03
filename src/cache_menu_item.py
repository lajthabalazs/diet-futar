'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import MenuItem
from google.appengine.ext import db
from cache_dish import getDish

MENU_ITEMS_FOR_DAY="MI_DAY"

def createMenuItemData(menuItem):
	subItemKeys=[]
	for subItem in menuItem.components:
		subItemKeys.append(str(subItem.key()))
	menuItemObject={
		'key':str(menuItem.key()),
		'categoryKey':menuItem.categoryKey,
		'price':menuItem.price,
		'day':menuItem.day,
		'containingMenuItem':None,
		'active':menuItem.active,
		'componentKeys':subItemKeys,
		'alterable':True
	}
	try:
		menuItemObject['dishKey'] = str(menuItem.dish.key()),
	except:
		pass
	return menuItemObject

def getMenuItem(key):
	client = memcache.Client()
	menuItem = client.get(key)
	if menuItem == None:
		menuItemDb = MenuItem.get(key)
		menuItem = createMenuItemData(menuItemDb)
		client.set(key,menuItem)
	# Fetch dish for menu item and fetch subitems
	try:
		dish = getDish(menuItem['dishKey'])
		menuItem['dish'] = dish
		sumprice = 0
		try:
			sumprice = dish['price']
		except KeyError:
			pass
		if sumprice == None:
			sumprice = 0
		energy = 0
		try:
			energy = dish['energy']
		except KeyError:
			pass
		if energy == None:
			energy=0
		fat = 0
		try:
			fat = dish['fat']
		except KeyError:
			pass
		if fat == None:
			fat=0
		carbs = 0
		try:
			carbs = dish['carbs']
		except KeyError:
			pass
		if carbs == None:
			carbs=0
		fiber = 0
		try:
			fiber = dish['fiber']
		except KeyError:
			pass
		if fiber == None:
			fiber=0
		protein = 0
		try:
			protein = dish['protein']
		except KeyError:
			pass
		if protein == None:
			protein=0
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
	except:
		menuItem['sumprice'] = -1
		menuItem['energy'] = -1
		menuItem['fat'] = -1
		menuItem['carbs'] = -1
		menuItem['fiber'] = -1 
		menuItem['protein'] = -1
		menuItem['components'] = []
		pass
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
		try:
			sumprice = getDish(menuItem['dishKey'])['price']
		except KeyError:
			pass
		if sumprice == None:
			sumprice = 0
		menuItem['dish']=getDish(menuItem['dishKey'])
		components = []
		for subItemKey in menuItem['componentKeys']:
			component = getMenuItem(subItemKey)
			components.append(component)
			componentPrice = 0
			try:
				componentPrice = getDish(component['dishKey'])['price']
			except KeyError:
				pass
			if componentPrice != None:
				sumprice = sumprice + componentPrice
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