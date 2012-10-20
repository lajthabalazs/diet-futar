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
		'dishKey':str(menuItem.dish.key()),
		'price':menuItem.price,
		'sumprice':menuItem.sumprice,
		'day':menuItem.day,
		'containingMenuItem':None,
		'active':menuItem.active,
		'componentKeys':subItemKeys
	}
	return menuItemObject

def getMenuItem(key):
	client = memcache.Client()
	menuItem = client.get(key)
	if menuItem == None:
		menuItem = MenuItem.get(key)
		menuItemObject = createMenuItemData(menuItem)
		client.set(key,menuItemObject)
		return menuItemObject
	# Fetch dish for menu item and fetch subitems
	menuItem['dish']=getDish(menuItem['dishKey'])
	components = []
	for subItemKey in menuItem['componentKeys']:
		components.append(getMenuItem(subItemKey))
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
		menuItem['dish']=getDish(menuItem['dishKey'])
		components = []
		for subItemKey in menuItem['componentKeys']:
			components.append(getMenuItem(subItemKey))
		menuItem['components'] = components
		ret.append(menuItem)
	return ret

def addMenuItem(dishKey, day, containingMenuItem = None):
	# Store it in database
	dish=db.get(dishKey)
	menuItem=MenuItem()
	menuItem.day=day
	menuItem.dish=dish
	menuItem.price = dish.price
	menuItem.sumprice = dish.price
	menuItem.categoryKey=str(dish.category.key())
	menuItem.containingMenuItem = containingMenuItem
	menuItem.put()
	ret = ""
	# Store it in cache
	client = memcache.Client()
	client.set(str(menuItem.key()), createMenuItemData(menuItem))
	key = MENU_ITEMS_FOR_DAY+ str(menuItem.day) + "_" + str(menuItem.categoryKey)
	ret = ret + " KEY " + key + "<br/>"
	daysItems = client.get(key)
	#If we have something to update
	if daysItems != None:
		# Just add this menu item
		daysItems.append(createMenuItemData(menuItem))
		client.set(key,daysItems)
	else:
		# Don't do a thing, a request will trigger loading anyways
		pass

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
	else:
		# Don't do a thing, a request will trigger loading anyways
		pass

def deleteMenuItem(menuItem):
	client = memcache.Client()
	key = MENU_ITEMS_FOR_DAY+ str(menuItem.day) + "_" + str(menuItem.categoryKey)
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
	else:
		# Don't do a thing, a request will trigger loading anyways
		pass