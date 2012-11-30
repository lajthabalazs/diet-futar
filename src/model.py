'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.ext import db

ROLE_ADMIN="admin"
ROLE_DELIVERY_GUY="fut&#225;r"
ROLE_COOK="szak&#225;cs"
ROLE_AGENT="agent"

class Role(db.Model):
	name = db.StringProperty()

class User(db.Model):
	referNumber = db.IntegerProperty()
	email = db.StringProperty()
	password = db.StringProperty()
	familyName = db.StringProperty()
	givenName = db.StringProperty()
	phoneNumber = db.StringProperty()
	activated = db.BooleanProperty()
	activationCode = db.StringProperty()
	registrationDate=db.DateProperty()
	referer = db.SelfReferenceProperty('The user who suggested this page', "referred")
	sourceOfInfo = db.StringProperty()
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
	canBeTopLevel = db.BooleanProperty()
	basePrice=db.IntegerProperty()
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

class UserWeekOrder(db.Model):
	user=db.ReferenceProperty(User, collection_name='weeks')
	monday=db.DateProperty() # Monday of the week
	orderedComposits=db.StringListProperty() # The list of ordered composit keys of form: quantity SPACE key
	orderedMenuItems=db.StringListProperty() # The list of ordered composit keys of form: quantity SPACE key
	mondayAddress=db.ReferenceProperty(Address, collection_name='mondays')
	tuesdayAddress=db.ReferenceProperty(Address, collection_name='tuesdays')
	wednesdayAddress=db.ReferenceProperty(Address, collection_name='wednesdays')
	thursdayAddress=db.ReferenceProperty(Address, collection_name='thursdays')
	fridayAddress=db.ReferenceProperty(Address, collection_name='fridays')
	saturdayAddress=db.ReferenceProperty(Address, collection_name='saturdays')
	sundayAddress=db.ReferenceProperty(Address, collection_name='sundays')
	
class Wish(db.Model):
	title = db.StringProperty()
	description=db.StringProperty(multiline=True)
	ready=db.BooleanProperty()


















