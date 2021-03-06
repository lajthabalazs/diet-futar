'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import DishCategory, MenuItem, Composit,\
	CompositMenuItemListItem
from cache_menu_item import getMenuItem
from cache_dish_category import getDishCategory

COMPOSIT_FOR_DAY="COMP_DAY"

def createCompositData(compositDb):
	menuItemKeys=[]
	for component in compositDb.components:
		menuItem = component.menuItem
		menuItemKeys.append(
			{
				'menuItemKey':str(menuItem.key()),
				'componentKey':str(component.key())
			}
		)
	compositObject={
		'key':str(compositDb.key()),
		'categoryKey':compositDb.categoryKey,
		'price':compositDb.price,
		'day':compositDb.day,
		'active':compositDb.active,
		'menuItemKeys':menuItemKeys,
		'alterable':True
	}
	return compositObject

def fetchMenuItemsForComposit(compositObject):
	# Fetch menu item data for keys
	menuItems=[]
	i = 0
	for keyPair in compositObject['menuItemKeys']:
		menuItemObject = getMenuItem(keyPair['menuItemKey'])
		menuItemObject['uid'] = compositObject['key'] + str(i)
		menuItemObject['componentKey'] = keyPair['componentKey']
		i = i + 1
		menuItems.append(menuItemObject)
	return menuItems
	
def getComposit(key):
	client = memcache.Client()
	composit = client.get(key)
	if composit == None:
		try:
			compositDb = Composit.get(key)
			if compositDb == None:
				return None
		except:
			return None
		composit = createCompositData(compositDb)
		client.set(key,composit)
	# Fetch menu item data for keys
	composit['category'] = getDishCategory(composit['categoryKey'])
	composit['components'] = fetchMenuItemsForComposit(composit)
	return composit

def getDaysComposits(day, categoryKey):
	client = memcache.Client()
	key = COMPOSIT_FOR_DAY+ str(day) + "_" + str(categoryKey)
	daysItems = client.get(key)
	if daysItems == None:
		composits = Composit.all().filter("day = ", day).filter("categoryKey = ", categoryKey)
		daysItems=[]
		for composit in composits:
			compositObject = createCompositData(composit)
			client.set(compositObject['key'], compositObject)
			daysItems.append(compositObject)
		client.set(key,daysItems)
	retItems = []
	# Fetch menu item data for keys
	for composit in daysItems:
		composit['components'] = fetchMenuItemsForComposit(composit)
		retItems.append(composit)
	return retItems

def addComposit(categoryKey, day):
	# Add it to database
	composit = Composit()
	composit.day=day
	composit.category=DishCategory.get(categoryKey)
	composit.price = composit.category.basePrice
	composit.categoryKey=str(categoryKey)
	composit.put()
	# Adds it to cache
	client = memcache.Client()
	key = COMPOSIT_FOR_DAY+ str(composit.day) + "_" + str(composit.categoryKey)
	daysComposits = client.get(key)
	#If we have something to update
	if daysComposits != None:
		# Just add this menu item
		compositObject = createCompositData(composit)
		daysComposits.append(compositObject)
		client.set(compositObject['key'], compositObject)
		client.set(key,daysComposits)

def modifyComposit(compositDb):
	client = memcache.Client()
	daysCompositsKey = COMPOSIT_FOR_DAY+ str(compositDb.day) + "_" + str(compositDb.categoryKey)
	daysComposits = client.get(daysCompositsKey)
	compositKey=str(compositDb.key())
	#If we have something to update
	composit = createCompositData(compositDb)
	client.set(compositKey, composit)
	if daysComposits != None:
		newComposits = []
		for dayItem in daysComposits:
			if (dayItem['key'] == compositKey):
				# Add menu item to new array
				newComposits.append(composit)
			else:
				newComposits.append(dayItem)
		# Finally just add it to the cache 
		client.set(daysCompositsKey, newComposits)

def addMenuItemToComposit(compositKey, menuItemKey):
	composit = Composit.get(compositKey)
	menuItem = MenuItem.get(menuItemKey)
	compositItem = CompositMenuItemListItem()
	compositItem.menuItem = menuItem
	compositItem.composit = composit
	compositItem.put()
	modifyComposit(composit)

def deleteComposit(composit):
	client = memcache.Client()
	key = COMPOSIT_FOR_DAY+ str(composit.day) + "_" + str(composit.categoryKey)
	daysComposits = client.get(key)
	compositKey=str(composit.key())
	#If we have something to update
	if daysComposits != None:
		newComposits = []
		for dayItem in daysComposits:
			if (dayItem['key'] == compositKey):
				# Find item by key
				client.delete(compositKey)
			else:
				# Add menu item to new array
				newComposits.append(dayItem)
		# Finally just add it to the cache 
		client.set(key,newComposits)