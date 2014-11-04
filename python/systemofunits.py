#!/usr/bin/env python
""":mod:`systemofunits` -- System of Units
=====================================

.. module:: systemofunits
   :platform: Unix
      :synopsis: define system of units and its prefixes and suffixes.
	  The module can be imported in any way, being the relevant item
	  the 'unit' instance of the unitcontainer class. The suggested
	  way to import is: from PyAnUtils.systemofunits import unit
	  
	  Example:
	    from PyAnUtils.systemofunits import unit 
		L=10*unit.m
		...

	  .. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""
# Preventing the exportation of everything except "unit" and "getavailableunits" 
# when using "from PyAnUtils.systemofunits import *"
__all__ = [ "unit" ,"getavailableunits"]

# TODO / FIXME
# Avoid the use of this module separately, in particular the only class can be exported
# is the 'unitcontainer' class, all the others not must be instantiated out of this module
# in order not to break the correlation between units

# Some basic definitions and descriptions
BASEUNITS    = { "L": "Lenght", "T": "Time", "M": "Mass", "I":"Electric current",
		"THETA":"Temperature", "N":"Amount of substance", "J":"Luminous intensity" }
DERIVEDUNITS = { "A": "angle", "SA": "Solid Angle", "Nu": "Frequency", "F": "Force, Weight",
		"P": "Pressure, stress", "E": "Energy, work, heat", "W": "Power, radiant fluw",
		"Q": "Electric charge",
		"V": "Voltage (Electrical potential difference)","C": "Electric capacitance",
		"R": "Electric resistance, impedance, reactance", "EC": "Electric conductance",
		"MB": "Magnetic flux", "B": "Magnetic field strength", "H": "Inductance",
		"Bq": "Radioactivity (decays per unit time)", "Gy": "Absorbed dose (of inonizing radiation)",
		"Sv": "Equivalent dose (of ionizing radiation)"
		}
UNITS = dict(BASEUNITS)
UNITS.update(DERIVEDUNITS)

# Unit symbols and suffixes and prefixes
UNITSYMBOL = { 'L': ('m','metre'), 'T': ('sec','second'), 'M': ('g', 'gram'), 'I': ("A","Ampere"),
		"THETA": ("K","kelvin"), "N":("mol","mol"), "J": ("cd", "candela"),
		"A": ("rad","radian"), "SA": ("sr", "stereoradian"), "Nu": ("Hz", "hertz"),
		"F": ("N", "newton"), "P": ("Pa", "pascal"), "E": ("J","joule"), "W": ("W","watt"),
		"Q": ("C","coulomb"), "V": ("V","volt"), "C": ("F","farad"), "R": ("Ohm","ohm"),
		"EC": ("S","siemens"),"MB": ("Wb", "weber"), "B": ("T","tesla"), "H": ("H","henry"),
		"Bq": ("Bq","becquerel"), "Gy": ("Gy","gray"), "Sv": ("Sv","sievert")
		}

# prefixes and suffixes definition with respect to the unit symbol stored in UNITSYMBOL
_prefixes = {"da": 1e1, "h": 1e2, "k":1e3, "M": 1e6, "G":1e9, "T":1e12, "P":1e15, "E":1e18, "Z":1e21, "Y":1e24}
_suffixes = { "d":1e-1, "c":1e-2, "m":1e-3, "u":1e-6, "n":1e-9, "p":1e-12, "f":1e-15, "a":1e-18, "z":1e-21, "y":1e-24}

# A global variable to ... Fixing to 1.0 the base units we want to used
BASEUNITVALUES = {}
#BASEUNITVALUES = dict(map(lambda x: (UNITSYMBOL[x][0],1.0) ,BASEUNITS.keys()))
DERIVEDINTERMS = { "A": "L/L", 'SA': "L**2/L**2", "Nu": "1/T", "F": "M*L/T**2", "P": "M/L/T**2",
		"E": "M*L**2/T**2", "W": "M*L**2/T**3", "Q": "I*T", "V": "M*L**2/T**3/I",
		"C": "T**4*I**2/M/L**2", "R": "M*L**2/T**3/I**2", "EC": "T**3*I**2/M/L**2",
		"MB": "M*L**2/T**2/I", "B": "M/T**2/I", "H": "M*L**2/T**2/I**2",
		"Bq": "1/T", "Gy": "L**2/T**2", "Sv": "L**2/T**2"
		}

# Informative function
def getavailableunits():
	""".. function:: getavailableunits() -> string

	Return the available units in the module
	"""
	maxsylen= max(max(map(lambda x: len(x),UNITSYMBOL.keys())),len("Unit"))
	maxdlen = max(max(map(lambda x: len(x),UNITS.values())),len("Description"))
	maxulen = max(max(map(lambda x: len(x),UNITS.keys())),len("Key"))
	ku = '%'+str(maxulen)+"s  %"+str(maxdlen)+"s  %"+str(maxsylen)+"s  %s\n" 
	u = ku % ("Key","Description","Unit","")
	u += ku % ("-"*maxulen,"-"*maxdlen,"-"*maxsylen,"")
	for i,j in UNITS.iteritems():
		unit = UNITSYMBOL[i]
		u+= ku % (i,j,unit[0],unit[1])
	return u

def getunitintermsofbase(unittype):
	""".. function:: getunitintermsofbase(unittype) -> 
	"""
	from math import log10

	if len(BASEUNITVALUES) != 7:
		mess = "\033[1;31m getunitintermsofbase ERROR\033[1;m Needed all the BASE units"
		mess +=" initialized before trying to init derived units!"
		raise RuntimeError(mess)
	derivedexpr = DERIVEDINTERMS[unittype]
	# Preparing the expression to parse
	chunks = []
	for ch in derivedexpr:
		if ch.isdigit():
			if len(chunks) > 0 and chunks[-1].isdigit():   
				chunks[-1]+= ch
			else:
				chunks.append(ch)
		elif ch == '*' and chunks[-1] == '*':
			chunks[-1] += ch
		else:
			chunks.append(ch)
	# Extract the units prefered by the user
	cheval= []
	for ustr in chunks:
		if ustr not in BASEUNITS.keys():
			cheval.append(ustr)
			continue
		defaultval = UNITSYMBOL[ustr][0]
		userval    = BASEUNITVALUES[ustr]
		preorsuf = userval.replace(defaultval,'',1)
		# Note that the per default central unit in "M" is kg
		# so, do nothing when found kg
		if len(preorsuf) == 0 or userval == 'kg':
			# No modification from the default
			cheval.append('1.0')
		elif userval != "kg":
			# There is modifications
			_total = dict(_prefixes); _total.update(_suffixes)
			cheval.append( str(_total[preorsuf]) )
	
	# The expression is ready to be evaluated
	chexpr = ''
	for i in cheval:
		chexpr += i
	correctionfactor = 1.0/eval(chexpr)
	# It there are not correction (correctionfactor=1)
	nearestunit = UNITSYMBOL[unittype][0]
	# Get the near value to the correction factor
	if abs(correctionfactor-1.0) > 1e-6:
		_total = dict(_prefixes); _total.update(_suffixes)
		preorsufnear = min(_total,key=lambda x: abs(log10(correctionfactor)-log10(_total[x])))
		nearestunit = preorsufnear+nearestunit
	
	return nearestunit

# Basic class to deal with units
class unitobject(object):
	""".. class:: unitobject(object) 
	
	Base class defining a unit. The class defines to which base or derived class 
	belongs (Length, Mass, Energy, ...) and the unit defined to be the central one,
	i.e. the one with value=1
	"""
	def __init__(self,unittype,centralunit=None):
		""".. method:: unitobject(unitttype[,centralunit=None]) -> unitobject instance
		"""
		global BASEUNITVALUES

		if unittype not in UNITS.keys():
			mess = "\033[1;31m ERROR\033[1;m Invalid system of units!"
			mess +=" The valid units are: \n%s" % getavailbleunits() 
			raise RuntimeError(mess)
		self.unittype = unittype

		# FIXME : Mass is an exception, kg=1
		if unittype == "M" and centralunit:
			mess = "\033[1;33m WARNING\033[1;m Moving the central value"
			mess +=" for the 'Mass' unit type is not implemented yet. Exiting"
			raise RuntimeError(mess)

		# Check if is a base or derived in order to obtain the base units
		# to build this derived unit
		self.isbasetype = True
		if self.unittype in DERIVEDUNITS:
			self.isbasetype = False
		# Name of the default central unit
		self.centralunit = UNITSYMBOL[self.unittype][0]
		self.symbolname = UNITSYMBOL[self.unittype][1]
		# Using as 1.0 the defined base unit for the user, otherwise the default
		# one (S.I. contained in UNIT SYMBOL-- except for M which is kg)
		self.baseunit = self.centralunit
		self.basename = self.symbolname
		self.correctionfactor = 1.0
		if self.unittype == 'M':
			self.baseunit = 'kg'
			self.basename = 'kilogram'
			self.correctionfactor /= 1e3
		
		if centralunit and self.isbasetype:
			# Check if this symbol exists
			if centralunit not in [self.centralunit] + map(lambda x: x+UNITSYMBOL[self.unittype][0],
				_prefixes.keys()+_suffixes.keys()):
				mess = "\033[1;31m ERROR\033[1;m Invalid symbol name '%s'" % centralunit
				mess +=" for the unit type '%s'" % self.unittype
				raise RuntimeError(mess)
			_pr = centralunit.replace(self.baseunit,'',1)
			_totalprsu = dict(_prefixes); _totalprsu.update(_suffixes)
			self.baseunit = centralunit
			self.basename = centralunit
		elif not self.isbasetype:
			# Only base units can have a displaced central value
			self.baseunit = getunitintermsofbase(self.unittype)
			self.basename = self.baseunit
			_pr = self.baseunit.replace(self.centralunit,'',1)
			_totalprsu = dict(_prefixes); _totalprsu.update(_suffixes)
			try:
				# Checking if there displacement from the central unit
				self.correctionfactor = 1.0/_totalprsu[_pr]
			except KeyError:
				pass
		
		if self.isbasetype:
			# Updating the base system of units
			BASEUNITVALUES[self.unittype] = self.baseunit

		# Fixing the value of the central unit
		self.__setattr__(self.centralunit,self.correctionfactor)
		# Prefixes and suffixes
		self.__buildprefixes__()
		self.__buildsuffixes__()

	def __str__(self):
		""" .. method:: __str__() --> str
		
		Description of the unit 
		"""
		return "Unit type: %s\nUnit symbol: %s (%s)" % (self.unittype,self.centralunit,self.symbolname)

	def __buildprefixes__(self):
		""".. method:: __buildprefixes__() 

		Build and assign values to the prefixes 
		with respect the central value
		"""
		self.__buildps__(_prefixes)
		
	def __buildsuffixes__(self):
		""".. method:: __buildsuffixes__() 

		Build and assign values to the suffixes
		with respect the central value
		"""
		self.__buildps__(_suffixes)
	
	def __buildps__(self,_d):
		""".. method:: __buildps__(_d) 

		Set the attributes with the prefixes/suffixes, which are
		described in the dictionary '_d'
		"""
		# Recovering the centralunit
		for i,f in _d.iteritems():
			self.__setattr__(i+self.centralunit,f*self.correctionfactor)

# Unit container dummy class
class unitcontainer(object):
	# TODO: Introduce the mechanism to allow the inclusion of different central values
	# for the base units, and do the code above inside the class
	pass

## Create a full system of units, adding the name of the unit, prefixes and suffixes
## as attributes of the 'unit' instance. Some examples:
## unit.m : metre (1)
## unit.mm: milimeter (1e-3*unit.m)
#print "::System of Units initialized"
unit = unitcontainer()

for i in BASEUNITS.keys():
	s = UNITSYMBOL[i][0]
	a = unitobject(i)
	for attr in [s]+map(lambda x: x+s,_prefixes.keys()+_suffixes.keys()):
		unit.__setattr__(attr,a.__getattribute__(attr))

for i in DERIVEDUNITS.keys():
	s = UNITSYMBOL[i][0]
	a = unitobject(i)
	for attr in [s]+map(lambda x: x+s,_prefixes.keys()+_suffixes.keys()):
		unit.__setattr__(attr,a.__getattribute__(attr))
