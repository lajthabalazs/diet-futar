from base_handler import BaseHandler
class Icon:
	def __init__(self, id='icon'):
		self.id = id
		self.image = ""     #uses default Google Maps icon
		self.shadow = ""
		self.iconSize = (12, 20)    # these settings match above icons
		self.shadowSize = (22, 20)
		self.iconAnchor = (6, 20)
		self.infoWindowAnchor = (5, 1)

class Map:
	def __init__(self,id="map",pointlist=None):
		self.id       = id    # div id        
		self.width    = "500px"  # map div width
		self.height   = "300px"  # map div height
		self.center   = (0,0)     # center map latitude coordinate
		self.zoom        = "1"   # zoom level
		self.navcontrols  =   True   # show google map navigation controls
		self.mapcontrols  =   True   # show toogle map type (sat/map/hybrid) controls
		if pointlist == None:
			self.points = []   # empty point list
		else:
			self.points = pointlist   # supplied point list

	def __str__(self):
		return self.id
	
	def setpoint(self, point):
		# Add a point (lat,long,html,icon)
		self.points.append(point)

class PyMap:
	# Python wrapper class for Google Maps API.
	def __str__(self):
		return "Pymap"

	def __init__(self, key=None, maplist=None, iconlist=None):
		# Default values
		self.key="ABQIAAAAQQRAsOk3uqvy3Hwwo4CclBTrVPfEE8Ms0qPwyRfPn-DOTlpaLBTvTHRCdf2V6KbzW7PZFYLT8wFD0A"
		if maplist == None:
			self.maps = [Map()]
		else:
			self.maps = maplist
		if iconlist == None:
			self.icons = [Icon()]
		else:
			self.icons = iconlist

	def addicon(self,icon):
		self.icons.append(icon)

	def _navcontroljs(self,map):
		# Returns the javascript for google maps control
		if map.navcontrols:
			return "           %s.gmap.addControl(new GSmallMapControl());\n" % (map.id)
		else:
			return ""

	def _mapcontroljs(self,map):
		# Returns the javascript for google maps control    
		if map.mapcontrols:
			return  "           %s.gmap.addControl(new GMapTypeControl());\n" % (map.id)
		else:
			return ""


	def _showdivhtml(self,map):
		# Returns html for dislaying map
		html = """\n<div id=\"%s\">\n</div>\n""" % (map.id)
		return html

	def _point_hack(self, points):
		count = 1
		for item in points:
			open = str(item).replace("(", "[")
			open = open.replace(")", "]")
		return open


	def _mapjs(self,map):
		js = "%s_points = %s;\n" % (map.id,map.points)
		js = js.replace("(", "[")
		js = js.replace(")", "]")
		js = js.replace("u'", "'")
		js = js.replace("''","")    #python forces you to enter something in a list, so we remove it here
		##        js = js.replace("'icon'", "icon")
		for icon  in self.icons:
			js = js.replace("'"+icon.id+"'",icon.id)
			js +=   """             var %s = new Map('%s',%s_points,%s,%s,%s);
			\n\n%s\n%s""" % (map.id,map.id,map.id,map.center[0],map.center[1],map.zoom, self._mapcontroljs(map), self._navcontroljs(map))
		return js

	def _iconjs(self,icon):
		js = """ 
			var %s = new GIcon(); 
			%s.image = "%s";
			%s.shadow = "%s";
			%s.iconSize = new GSize(%s, %s);
			%s.shadowSize = new GSize(%s, %s);
			%s.iconAnchor = new GPoint(%s, %s);
			%s.infoWindowAnchor = new GPoint(%s, %s);
			""" % (icon.id, icon.id, icon.image, icon.id, icon.shadow, icon.id, icon.iconSize[0],icon.iconSize[1],icon.id, icon.shadowSize[0], icon.shadowSize[1], icon.id, icon.iconAnchor[0],icon.iconAnchor[1], icon.id, icon.infoWindowAnchor[0], icon.infoWindowAnchor[1])
		return js

	def _buildicons(self):
		js = ""
		if (len(self.icons) > 0):
			for i in self.icons:
				js = js + self._iconjs(i)    
		return js

	def _buildmaps(self):
		js = ""
		for i in self.maps:
			js = js + self._mapjs(i)+'\n'
		return js

class MapTestPage(BaseHandler):
	g = PyMap()                         # creates an icon & map by default
	icon2 = Icon('icon2')               # create an additional icon
	icon2.image = "http://labs.google.com/ridefinder/images/mm_20_blue.png" # for testing only!
	icon2.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png" # do not hotlink from your web page!
	g.addicon(icon2)
	g.key = "ABQIAAAAQQRAsOk3uqvy3Hwwo4CclBTrVPfEE8Ms0qPwyRfPn-DOTlpaLBTvTHRCdf2V6KbzW7PZFYLT8wFD0A" # you will get your own key
	g.maps[0].zoom = 5
	q = [1,1]                           # create a marker with the defaults
	r = [2,2,'','icon2']                # icon2.id, specify the icon but no text
	s = [3,3,'hello, <u>world</u>']     # don't specify an icon & get the default
	g.maps[0].setpoint(q)               # add the points to the map
	g.maps[0].setpoint(r)
	g.maps[0].setpoint(s)
	
	##    print g.showhtml()
	open('test.htm','wb').write(g.showhtml())   # generate test file