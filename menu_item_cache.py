'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import Dish, DishCategory, MenuItem, Composit,\
	CompositMenuItemListItem
from google.appengine.ext import db

MENU_ITEMS_FOR_DAY="MI_DAY"
CATEGORIES_KEY="CATS"
COMPOSIT_FOR_DAY="COMP_DAY"

def getDish(key):
	client = memcache.Client()
	dish = client.get(key)
	if dish == None:
		dish = Dish.get(key)
		if dish != None:
			dishDict={
				'key':key,
				'title':dish.title,
				'categoryKey':dish.category.key(),
				'price':dish.price
			}
			client.set(key, dishDict)
			return dishDict
	else:
		return dish

# Modify dish
def modifyDish(dish):
	client = memcache.Client()
	key = str(dish.key())
	# Create object
	dishDict={
		'key':key,
		'title':dish.title,
		'categoryKey':dish.category.key(),
		'price':dish.price
	}
	client.set(key, dishDict)

# Adds a dish to the cache
def addDish(dish):
	client = memcache.Client()
	dishDict={
		'key':dish.key(),
		'title':dish.title,
		'categoryKey':dish.category.key(),
		'price':dish.price
	}
	client.set(str(dish.key()), dishDict)

def createMenuItemData(menuItem):
	subItemList=[]
	for subItem in menuItem.components:
		subItemObject={
			'key':str(subItem.key()),
			'categoryKey':subItem.categoryKey,
			'dish':getDish(str(subItem.dish.key())),
			'price':subItem.price,
			'sumprice':subItem.sumprice,
			'day':subItem.day,
			'containingMenuItem':menuItem,
			'active':subItem.active
		}
		subItemList.append(subItemObject)
	menuItemObject={
		'key':str(menuItem.key()),
		'categoryKey':menuItem.categoryKey,
		'dish':getDish(str(menuItem.dish.key())),
		'price':menuItem.price,
		'sumprice':menuItem.sumprice,
		'day':menuItem.day,
		'containingMenuItem':None,
		'active':menuItem.active,
		'components':subItemList
	}
	return menuItemObject

# Delete dish from cache
def deleteDish(key):
	client = memcache.Client()
	dish = client.get(key)
	if dish == None:
		return
	else:
		client.delete(key)

def getDaysMenuItems(day, categoryKey):
	client = memcache.Client()
	key = MENU_ITEMS_FOR_DAY+ str(day) + "_" + str(categoryKey)
	daysItems = client.get(key)
	if daysItems == None:
		menuItems = MenuItem.all().filter("day = ", day).filter("categoryKey = ", categoryKey).filter("containingMenuItem = ", None)
		menuItemList=[]
		for menuItem in menuItems:
			menuItemObject = createMenuItemData(menuItem)
			menuItemList.append(menuItemObject)
		client.set(key,menuItemList)
		return menuItemList
	return daysItems

def addMenuItem(dishKey, day):
	# Store it in database
	dish=db.get(dishKey)
	menuItem=MenuItem()
	menuItem.day=day
	menuItem.dish=dish
	menuItem.price = dish.price
	menuItem.sumprice = dish.price
	menuItem.categoryKey=str(dish.category.key())
	menuItem.put()
	ret = ""
	# Store it in cache
	client = memcache.Client()
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
				newItems.append(createMenuItemData(menuItem))
			else:
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
				# Skip adding the item, and voila it's deleted
				pass
			else:
				# Add menu item to new array
				newItems.append(dayItem)
		# Finally just add it to the cache
		client.set(key,newItems)
	else:
		# Don't do a thing, a request will trigger loading anyways
		pass

def createCompositData(composit):
	menuItemList=[]
	for menuItem in composit.components:
		subItemList=[]
		for subItem in menuItem.menuItem.components:
			subItemObject={
				'key':str(subItem.key()),
				'categoryKey':subItem.categoryKey,
				'dish':getDish(str(subItem.dish.key())),
				'price':subItem.price,
				'sumprice':subItem.sumprice,
				'day':subItem.day,
				'containingMenuItem':menuItem,
				'active':subItem.active
			}
			subItemList.append(subItemObject)
		menuItemObject={
			'key':str(menuItem.menuItem.key()),
			'categoryKey':menuItem.menuItem.categoryKey,
			'dish':getDish(str(menuItem.menuItem.dish.key())),
			'price':menuItem.menuItem.price,
			'sumprice':menuItem.menuItem.sumprice,
			'day':menuItem.menuItem.day,
			'containingMenuItem':None,
			'active':menuItem.menuItem.active,
			'components':subItemList
		}
		menuItemList.append(menuItemObject)
	compositObject={
		'key':str(composit.key()),
		'categoryKey':composit.categoryKey,
		'price':composit.price,
		'sumprice':composit.sumprice,
		'day':composit.day,
		'category':composit.category,
		'active':composit.active,
		'components':menuItemList
	}
	return compositObject

def addComposit(categoryKey, day):
	# Add it to database
	composit = Composit()
	composit.day=day
	composit.category=DishCategory.get(categoryKey)
	composit.categoryKey=str(categoryKey)
	composit.put()
	# Adds it to cache
	client = memcache.Client()
	key = COMPOSIT_FOR_DAY+ str(composit.day) + "_" + str(composit.categoryKey)
	daysComposits = client.get(key)
	#If we have something to update
	if daysComposits != None:
		# Just add this menu item
		daysComposits.append(createCompositData(composit))
		client.set(key,daysComposits)
	else:
		# Don't do a thing, a request will trigger loading anyways
		pass

def addMenuItemToComposit(compositKey, menuItemKey):
	composit = Composit.get(compositKey)
	if composit.occurrences.count()==0:
		menuItem = MenuItem.get(menuItemKey)
		compositItem = CompositMenuItemListItem()
		compositItem.menuItem = menuItem
		compositItem.composit = composit
		compositItem.put()
	modifyComposit(composit)

def modifyComposit(composit):
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
				newComposits.append(createCompositData(composit))
			else:
				# Add menu item to new array
				newComposits.append(dayItem)
		# Finally just add it to the cache 
		client.set(key,newComposits)
	else:
		# Don't do a thing, a request will trigger loading anyways
		pass

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
				pass
			else:
				# Add menu item to new array
				newComposits.append(dayItem)
		# Finally just add it to the cache 
		client.set(key,newComposits)
	else:
		# Don't do a thing, a request will trigger loading anyways
		pass


def getDaysComposits(day, categoryKey):
	client = memcache.Client()
	key = COMPOSIT_FOR_DAY+ str(day) + "_" + str(categoryKey)
	daysItems = client.get(key)
	if daysItems == None:
		composits = Composit.all().filter("day = ", day).filter("categoryKey = ", categoryKey)
		compositList=[]
		for composit in composits:
			compositList.append(createCompositData(composit))
		client.set(key,compositList)
		return compositList
	return daysItems

def getCategories():
	client = memcache.Client()
	categories=client.get(CATEGORIES_KEY)
	if categories == None:
		categories = DishCategory.all().order("index")
		categoryList=[]
		for category in categories:
			categoryObject={
				'key':str(category.key()),
				'name':category.name,
				'isMenu':category.isMenu,
				'index':category.index
			}
			categoryList.append(categoryObject)
		client.set(CATEGORIES_KEY, categoryList)
		return categoryList
	return categories

def getCategoryWithDishes(key):
	client = memcache.Client()
	category = client.get(key)
	if category == None:
		category = DishCategory.get(key)
		if category != None:
			dishes=[]
			for dish in category.dishes:
				dishObject={
					'key':key,
					'title':dish.title,
					'categoryKey':dish.category.key(),
					'price':dish.price
				}
				dishes.append(dishObject)
			categoryObject={
				'key':category.key,
				'name':category.name,
				'isMenu':category.isMenu,
				'index':category.index,
				'dishes':dishes
			}
			client.set(key, categoryObject)
			return categoryObject
	else:
		return category
	
