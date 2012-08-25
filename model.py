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
	subTitle = db.StringProperty()
	description = db.StringProperty(multiline=True)
	category=db.ReferenceProperty(DishCategory, collection_name='dishes')

class IngredientCategory(db.Model):
	name = db.StringProperty()

class Ingredient(db.Model):
	name = db.StringProperty()
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
	day=db.DateProperty()
	#type=db.StringProperty()
	#menuItemIndex=db.IntegerProperty()

class Wish(db.Model):
	title = db.StringProperty()
	description=db.StringProperty(multiline=True)
	ready=db.BooleanProperty()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	