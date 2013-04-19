'''
Created on Aug 11, 2012

@author: lajthabalazs
'''
from google.appengine.ext import db
import datetime

ROLE_ADMIN="admin"
ROLE_DELIVERY_GUY="fut&#225;r"
ROLE_COOK="szak&#225;cs"
ROLE_AGENT="agent"

class Role(db.Model):
	name = db.StringProperty()

class SiteParams(db.Model):
	name = db.StringProperty(multiline=True, default='')
	value = db.StringProperty(multiline=True,default='')

class Maintenence(db.Model):
	startDate = db.DateTimeProperty()
	endDate = db.DateTimeProperty()
	displayedDate = db.StringProperty(multiline=True)
	features = db.StringProperty(multiline=True)
	active = db.BooleanProperty()

class ZipCodes(db.Model):
	deliveryCosts = db.StringListProperty()

class User(db.Model):
	referNumber = db.IntegerProperty()
	email = db.StringProperty()
	password = db.StringProperty()
	passwordHash = db.StringProperty()
	familyName = db.StringProperty()
	givenName = db.StringProperty()
	phoneNumber = db.StringProperty()
	activated = db.BooleanProperty()
	activationCode = db.StringProperty()
	registrationDate=db.DateTimeProperty()
	referer = db.SelfReferenceProperty('The user who suggested this page', "referred")
	sourceOfInfo = db.StringProperty()
	role=db.ReferenceProperty(Role, collection_name='users')
	#CRM fields
	customerStatus=db.StringProperty()
	customerStatusHistory = db.StringListProperty()
	lastOrder = db.DateProperty()
	lastPageAccess = db.DateTimeProperty()
	lastOrderFlag = db.BooleanProperty(default=True)
	lastContact = db.DateTimeProperty()
	taskList = db.StringListProperty()
	doneTasks = db.StringListProperty()
	contactHistory = db.StringListProperty()
	unsubscribedFromNewsletter = db.BooleanProperty(default=False)
	inNewsLetterTargetGroup = db.BooleanProperty(default=True)
	
class Address (db.Model):
	user = db.ReferenceProperty(User, collection_name='addresses')
	zipCode = db.StringProperty()
	zipNumCode = db.IntegerProperty()
	street = db.StringProperty(multiline=True)
	streetNumber = db.StringProperty(multiline=True)
	active = db.BooleanProperty(default=True)
	lat = db.StringProperty(default=None)
	lon = db.StringProperty(default=None)

class DishCategory(db.Model):
	name = db.StringProperty()
	abbreviation = db.StringProperty()
	isExtra = db.BooleanProperty()
	isMenu = db.BooleanProperty()
	canBeTopLevel = db.BooleanProperty()
	basePrice=db.IntegerProperty()
	index=db.IntegerProperty()

class Dish(db.Model):
	title = db.StringProperty()
	creationDate = db.DateProperty()
	price = db.IntegerProperty()
	subtitle=db.StringProperty(multiline=True)
	description = db.StringProperty(multiline=True)
	category=db.ReferenceProperty(DishCategory, collection_name='dishes')
	eggFree = db.BooleanProperty(default=False)
	milkFree = db.BooleanProperty(default=False)
	codeModifier = db.StringProperty(default=None)

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
	orderHistory=db.StringListProperty() # The list of ordered items keys of form: date_time SPACE quantity SPACE key	
	mondayAddress=db.ReferenceProperty(Address, collection_name='mondays')
	tuesdayAddress=db.ReferenceProperty(Address, collection_name='tuesdays')
	wednesdayAddress=db.ReferenceProperty(Address, collection_name='wednesdays')
	thursdayAddress=db.ReferenceProperty(Address, collection_name='thursdays')
	fridayAddress=db.ReferenceProperty(Address, collection_name='fridays')
	saturdayAddress=db.ReferenceProperty(Address, collection_name='saturdays')
	sundayAddress=db.ReferenceProperty(Address, collection_name='sundays')
	mondayComment=db.StringProperty(default="",multiline=True)
	tuesdayComment=db.StringProperty(default="",multiline=True)
	wednesdayComment=db.StringProperty(default="",multiline=True)
	thursdayComment=db.StringProperty(default="",multiline=True)
	fridayComment=db.StringProperty(default="",multiline=True)
	saturdayComment=db.StringProperty(default="",multiline=True)
	sundayComment=db.StringProperty(default="",multiline=True)
	mondayPaid=db.IntegerProperty(default=0)
	tuesdayPaid=db.IntegerProperty(default=0)
	wednesdayPaid=db.IntegerProperty(default=0)
	thursdayPaid=db.IntegerProperty(default=0)
	fridayPaid=db.IntegerProperty(default=0)
	saturdayPaid=db.IntegerProperty(default=0)
	sundayPaid=db.IntegerProperty(default=0)

class WebshopItem(db.Model):
	title=db.StringProperty()
	code=db.StringProperty(default=None)
	active = db.BooleanProperty(default=True)
	nextAvailable = db.DateProperty(default=datetime.datetime.strptime('2012-10-01','%Y-%m-%d').date())
	availableUntil = db.DateProperty(default=datetime.datetime.strptime('9999-12-30','%Y-%m-%d').date())
	price=db.IntegerProperty(default=0)
	availableQuantity=db.IntegerProperty(default=10000)
	tags=db.StringListProperty()
	shortDescription=db.StringProperty(multiline=True)
	description=db.StringProperty(multiline=True)

class WebshopOrderItem(db.Model):
	user=db.ReferenceProperty(User, collection_name='webshopOrders')
	item=db.ReferenceProperty(WebshopItem, collection_name='orders')
	orderQuantity=db.IntegerProperty(default=0)
	orderDate=db.DateTimeProperty()
	orderState=db.IntegerProperty(default=0) # States are the following: 0 ordered 1 accepted 2 rejected 3 prepared 4 delivered 5 failed 6 deleted_by_user
	address=db.ReferenceProperty(Address, collection_name='webshopOrders')
	comments=db.StringListProperty()
	commentDates=db.StringListProperty()
	commentAuthors=db.StringListProperty()
	
class Wish(db.Model):
	title = db.StringProperty()
	description=db.StringProperty(multiline=True)
	ready=db.BooleanProperty()

class UserOrderEvent(db.Model):
	orderDate=db.DateTimeProperty()
	price=db.IntegerProperty()
	user=db.ReferenceProperty(User, collection_name='userOrderEvents')
	orderedItems = db.StringListProperty()

class Books(db.Model):
	monday=db.DateProperty()
	mondayIncome=db.IntegerProperty(default=0)
	tuesdayIncome=db.IntegerProperty(default=0)
	wednesdayIncome=db.IntegerProperty(default=0)
	thursdayIncome=db.IntegerProperty(default=0)
	fridayIncome=db.IntegerProperty(default=0)
	saturdayIncome=db.IntegerProperty(default=0)
	sundayIncome=db.IntegerProperty(default=0)

# OLD STUFF Needed only for migration

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

















