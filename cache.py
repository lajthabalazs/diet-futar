'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.api import memcache
from model import Dish, DishCategory, MenuItem, Composit

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

def getDaysMenuItems(day, categoryKey):
	client = memcache.Client()
	key = MENU_ITEMS_FOR_DAY+ str(day) + "_" + str(categoryKey)
	daysItems = client.get(key)
	if daysItems == None:
		menuItems = MenuItem.all().filter("day = ", day).filter("categoryKey = ", categoryKey).filter("containingMenuItem = ", None)
		menuItemList=[]
		for menuItem in menuItems:
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
			menuItemList.append(menuItemObject)
		client.add(key,menuItemList)
		return menuItemList
	return daysItems

def getDaysComposits(day, categoryKey):
	client = memcache.Client()
	key = COMPOSIT_FOR_DAY+ str(day) + "_" + str(categoryKey)
	daysItems = client.get(key)
	if daysItems == None:
		composits = Composit.all().filter("day = ", day).filter("categoryKey = ", categoryKey)
		compositList=[]
		for composit in composits:
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
			compositList.append(compositObject)
		client.add(key,compositList)
		return compositList
	return daysItems


def getCategories():
	client = memcache.Client()
	#client.delete(CATEGORIES_KEY)
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
		client.add(CATEGORIES_KEY, categoryList)
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
	
