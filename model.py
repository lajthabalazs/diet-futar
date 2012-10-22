'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.ext import db

ROLE_ADMIN="admin"
ROLE_DELIVERY_GUY="fut&#225;r"
ROLE_COOK="szak&#225;cs"

class Role(db.Model):
	name = db.StringProperty()

class User(db.Model):
	email = db.StringProperty()
	password = db.StringProperty()
	familyName = db.StringProperty()
	givenName = db.StringProperty()
	phoneNumber = db.StringProperty()
	activated = db.BooleanProperty()
	activationCode = db.StringProperty()
	registrationDate=db.DateProperty()
	role=db.ReferenceProperty(Role, collection_name='users')

class Address (db.Model):
	district = db.StringProperty()
	zipCode = db.StringProperty()
	street = db.StringProperty()
	streetNumber = db.StringProperty()
	user = db.ReferenceProperty(User, collection_name='addresses')

class DishCategory(db.Model):
	name = db.StringProperty()
	isMenu = db.BooleanProperty()
	index=db.IntegerProperty()

class Dish(db.Model):
	title = db.StringProperty()
	price = db.IntegerProperty()
	subtitle=db.StringProperty()
	description = db.StringProperty(multiline=True)
	category=db.ReferenceProperty(DishCategory, collection_name='dishes')

class IngredientCategory(db.Model):
	name = db.StringProperty()

class Ingredient(db.Model):
	name = db.StringProperty()
	price = db.FloatProperty(default=0.0)
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
	

class Composit(db.Model):
	categoryKey=db.StringProperty()
	price = db.IntegerProperty()
	day=db.DateProperty()
	category=db.ReferenceProperty(DishCategory, collection_name='composits')
	active=db.BooleanProperty(default=True)

class MenuItem(db.Model):
	categoryKey=db.StringProperty()
	dish=db.ReferenceProperty(Dish, collection_name='occurrences')
	price = db.IntegerProperty()
	day=db.DateProperty()
	containingMenuItem=db.SelfReferenceProperty('Containing menu item', collection_name='components')
	active=db.BooleanProperty(default=True)

class CompositMenuItemListItem(db.Model):
	menuItem=db.ReferenceProperty(MenuItem, collection_name='composits')
	composit=db.ReferenceProperty(Composit, collection_name='components')

class UserOrder(db.Model):
	orderDate=db.DateTimeProperty()
	price=db.IntegerProperty()
	user=db.ReferenceProperty(User, collection_name='userOrders')
	canceled=db.BooleanProperty()

class UserOrderAddress(db.Model):
	day=db.DateProperty()
	user=db.ReferenceProperty(User, collection_name='deliveryAddresses')
	address=db.ReferenceProperty(Address, collection_name='deliveries')
	delivered=db.BooleanProperty(default=False)
	deliverer=db.ReferenceProperty(User, collection_name='deliveryJobs')

class UserOrderItem(db.Model):
	day=db.DateProperty()
	price=db.IntegerProperty()
	isComposit=db.BooleanProperty()
	user=db.ReferenceProperty(User, collection_name='orderedItems')
	userOrder=db.ReferenceProperty(UserOrder, collection_name='items')
	itemCount=db.IntegerProperty()
	orderedItem=db.ReferenceProperty(MenuItem, collection_name='occurrences')
	orderedComposit=db.ReferenceProperty(Composit, collection_name='occurrences')
	delivery=db.ReferenceProperty(UserOrderAddress, collection_name='items')

class Wish(db.Model):
	title = db.StringProperty()
	description=db.StringProperty(multiline=True)
	ready=db.BooleanProperty()


















