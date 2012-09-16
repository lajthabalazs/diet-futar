'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.ext import db

ROLE_ADMIN="admin"
class Role (db.Model):
	name = db.StringProperty()

class User(db.Model):
	userName = db.StringProperty()
	password = db.StringProperty()
	role = db.ReferenceProperty(Role, collection_name='users')

class DishCategory(db.Model):
	name = db.StringProperty()
	index=db.IntegerProperty()

class Dish(db.Model):
	title = db.StringProperty()
	price = db.IntegerProperty()
	subTitle = db.StringProperty()
	description = db.StringProperty(multiline=True)
	category=db.ReferenceProperty(DishCategory, collection_name='dishes')

class IngredientCategory(db.Model):
	name = db.StringProperty()

class Ingredient(db.Model):
	name = db.StringProperty()
	price = db.IntegerProperty()
	category = db.ReferenceProperty(IngredientCategory, collection_name='ingredients')
	energy = db.FloatProperty(default=0.0)
	carbs = db.FloatProperty(default=0.0)
	protein = db.FloatProperty(default=0.0)
	fat = db.FloatProperty(default=0.0)
	fiber = db.FloatProperty(default=0.0)
	glucozeFree = db.BooleanProperty(default=False)

class IngredientListItem(db.Model):
	ingredient = db.ReferenceProperty(Ingredient, collection_name='dishes')
	dish = db.ReferenceProperty(Dish, collection_name='ingredients')
	quantity = db.FloatProperty()
	
class MenuItem(db.Model):
	dish=db.ReferenceProperty(Dish, collection_name='occurrences')
	price = db.IntegerProperty()
	sumprice = db.IntegerProperty()
	day=db.DateProperty()
	containingMenuItem=db.SelfReferenceProperty('Containing menu item', collection_name='components')

class UserOrder(db.Model):
	orderDate=db.DateTimeProperty()
	price=db.IntegerProperty()
	user=db.ReferenceProperty(User, collection_name='userOrders')
	canceled=db.BooleanProperty()

class UserOrderItem(db.Model):
	price=db.IntegerProperty()
	userOrder=db.ReferenceProperty(UserOrder, collection_name='items')
	itemCount=db.IntegerProperty()
	orderedItem=db.ReferenceProperty(MenuItem, collection_name='occurrences')

class Wish(db.Model):
	title = db.StringProperty()
	description=db.StringProperty(multiline=True)
	ready=db.BooleanProperty()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	