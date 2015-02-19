#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import etreeabstraction as ET
import os
import os.path
import re
import sys
import time
import json



# Constants
# Trustabily levels
TRUSTABILITY_AUTO_REDUCED = 6 # Values can be added only if the value is currently empty
TRUSTABILITY_AUTO = 5         # Values can be changed and/or added
TRUSTABILITY_NEED_CHECK = 3   # No values should be changed but some can be added
TRUSTABILITY_OK = 0	      # No values should be changed nor added

# Log update verbose level
LOG_DEFAULT_LEVEL_UPDATE = 0

# Import dependencies
from mculib.log import *
from mculib.categories import *
from mculib.parser import *

class DatabaseSelector(MCULibClass):
	match_list = {}
	db = None
	mcu_list = None

	def __init__(self, db):
		self.db = db
		self.reset()

	def reset(self):
		self.mcu_list = self.db.get_mcu_list()
		# Build the match list
		self.match_list = {}

	def parse_selector(self, selector):
		# The rules
		rules = []
		regexpr_format = r"(!?)([^=:]+):?([^=]*)=?(.*)"
		category_list = [x.to_param() for x in get_category_list()]
		for sub_selector in selector.split(";"):
			values = re.findall(regexpr_format, sub_selector)
			if len(values) != 1:
				raise error("This sub-selector is not well formed `%s'." % (str(sub_selector)), self)
			v = values[0]
			# If v[2] is not a number, raise an error
			if v[2] and not is_number(v[2]):
				raise error("This parameter multi-value selector is not well formed %s." % (str(v)), self)
			if not v[3] and v[1] not in category_list:
				v = ('', v[2], v[1], v[0] == "!")
			if v[1] and v[1] not in category_list:
				raise error("This parameter is unknown (%s)." % (v[1]), self)
			# By default a missing param is a CategoryDeviceName
			if not v[1]:
				v = ('CategoryDeviceName', v[2], v[3], v[0] == "!")
			# By default a missing multi_value is ''
			if not v[2]:
				v = (v[1], '', v[3], v[0] == "!")
			rules.append(v)
		# Return the rules
		return rules

	def select(self, selector):
		"""
		Select and update the device list
		"""
		# Select the devices
		match_list = self.select_(selector)
		# Keep these devices
		self.match_list = match_list
		# Update the mcu list
		self.mcu_list = self.match_from_mcu_list(match_list)
		# return this object
		return self

	def get(self, selector = None):
		"""
		Get the selected mcu list
		"""
		if selector != None:
			self.match_list = self.select_(selector)
			return self.match_from_mcu_list(self.match_list)
		return self.mcu_list

	def get_match_list(self):
		return self.match_list

	def match_from_mcu_list(self, match_list):
		return [match_list[mcu_name]['mcu'] for mcu_name in match_list]

	def select_(self, selector):
		"""
		Select the devices / parameters from the database
		"""
		mcu_list = self.mcu_list
		match_list = {}
		# Build the match list
		for mcu in mcu_list:
			match_list[self.db.get_name(mcu)] = {
				'mcu': mcu,
				'match': []
			}

		# Generate the rules
		rules = self.parse_selector(selector)

		# Go through the list
		for rule in rules:
			selector_param = rule[0]
			selector_multi_value = rule[1]
			selector_value = rule[2]
			negate = rule[3]

			# Explore the devices list
			try:
				is_list = self.db.is_param_list(selector_param)
				is_multi = self.db.is_param_multi(selector_param)
				# Go through the MCU list
				for mcu in mcu_list:
					is_match = False
					# Get the value of the selected parameter
					param = self.db.get_parameter(mcu, selector_param)
					if param != None:
						mcu_value = self.db.get_param_value(param)
						if not is_list:
							mcu_value = [mcu_value]
						# List all the values of this parameter
						for index, value in enumerate(mcu_value):
							if is_multi and is_number(selector_multi_value):
								value = value[to_number(selector_multi_value)]
							if bool(re.match("^" + selector_value + "$", str(value))) != negate:
								match_list[self.db.get_name(mcu)]['match'].append({
									'param': param,
									'list_index': to_number(index),
									'field_index': to_number(selector_multi_value),
									'value': value
								})
								is_match = True
								break
					# Match if negate is on
					elif negate:
						is_match = True

					# If no match for this mcu, delete it from the list
					if not is_match:
						del match_list[self.db.get_name(mcu)]
				# Re-build the mcu list
				mcu_list = self.match_from_mcu_list(match_list)
			except Exception as e:
				raise
			#	raise error("Invalid regular expression `%s' - %s" % (str(selector_value), str(e)), self)

		# Return the match list
		return match_list

class DatabaseLog(MCULibClass):
	"""
	This class is responsible to log all database changes
	"""
	LOG_PATH = "database.log"
	NEW_MCU_PARAM = "new_mcu"
	NEW_ALIAS_PARAM = "new_alias"
	DELETE_MCU = "delete_mcu"
	DELETE_ALIAS = "delete_alias"
	record = True

	def __init__(self, record = True):
		self.clear_context()
		self.record = record

	def clear_context(self):
		self.context = []
		self.reset()

	def reset(self):
		"""
		Reset the context selection
		"""
		self.context_selection = self.context

	def read(self):
		"""
		Load the existing database log. If the current one is not empty, raise an error.
		"""
		if len(self.context) != 0:
			raise error("Current database log is not empty, %i element(s)" % (len(self.context)), self)
		# Load the existing content
		try:
			raw_data = read_file(DatabaseLog.LOG_PATH)
			self.context = json.loads(raw_data)
		except:
			self.context = []
		self.reset()

	def write(self):
		"""
		This function will save the log into a file and merge it to the existing context.
		It iwll also clear the current context.
		"""
		# Load the existing content
		raw_data = read_file(DatabaseLog.LOG_PATH)
		existing_context = json.loads(raw_data)
		# Merge the new elements to the existing context
		for element in self.context:
			self.merge_element(existing_context, element)
		# Save the new context
		write_file(DatabaseLog.LOG_PATH, json.dumps(existing_context))
		# Clear the current context
		self.clear_context()
		# Message
		self.info("Updated database log `%s'." % (DatabaseLog.LOG_PATH), 2)

	def get_timestamp_from_element(self, element):
		return element['d'] if 'd' in element else None
	def get_trustability_from_element(self, element):
		return element['t'] if 't' in element else None
	def get_item_name_from_element(self, element):
		return element['i'] if 'i' in element else None
	def get_param_from_element(self, element):
		return element['p'] if 'p' in element else None
	def get_value_from_element(self, element):
		return element['v'] if 'v' in element else None
	def get_previous_value_from_element(self, element):
		return element['o'] if 'o' in element else None

	def merge_element(self, context, element):
		"""
		Add a new element to an existing context
		"""
		inserted = False
		for index, e in enumerate(context):
			# timestamp context[index] <= timestamp element
			if self.get_timestamp_from_element(e) <= self.get_timestamp_from_element(element):
				context.insert(index, element)
				inserted = True
				break
		if not inserted:
			context.append(element)

	def add(self, item_name, param, value = "", previous_value = "", trustability = TRUSTABILITY_AUTO):
		if isinstance(item_name, str):
			item_name = [item_name]
		new = {
			'd': self.get_timestamp(),
			't': trustability,
			'i': object_clone(item_name),
			'p': str(param),
			'v': value,
			'o': previous_value
		}
		# Add the element to the list if recording is enabled
		if self.record:
			self.merge_element(self.context, new)
		# Display a message
		if param == DatabaseLog.NEW_MCU_PARAM:
			self.info("[CREATE] Creating a new MCU: `%s'" % (str("::".join(item_name))), LOG_DEFAULT_LEVEL_UPDATE)
		elif param == DatabaseLog.NEW_ALIAS_PARAM:
			self.info("[ALIAS] Creating a new ALIAS: `%s'" % (str("::".join(item_name))), LOG_DEFAULT_LEVEL_UPDATE)
		elif param == DatabaseLog.DELETE_MCU:
			self.info("[DELETE] Delete MCU: `%s'" % (str("::".join(item_name))), LOG_DEFAULT_LEVEL_UPDATE)
		elif param == DatabaseLog.DELETE_ALIAS:
			self.info("[DELETE] Delete ALIAS: `%s'" % (str("::".join(item_name))), LOG_DEFAULT_LEVEL_UPDATE)
		else:
			self.message("VALUE", item_name, param, previous_value, value)

	def add_comment(self, item_name, param, comment, previous_comment = ""):
		self.message("COMMENT", item_name, param, previous_comment, comment)

	def add_trustability(self, item_name, param, trustability, previous_trustability = TRUSTABILITY_AUTO):
		self.message("TRUSTABILITY", item_name, param, previous_trustability, trustability)

	def add_source(self, item_name, param, source, previous_source = ""):
		self.message("SOURCE", item_name, param, previous_source, source)

	def get_timestamp(self):
		"""
		Return the current timestamp
		"""
		return int(time.time())

	def from_timestamp(self, timestamp):
		"""
		Update the selection from the specified timestamp to now
		"""
		previous_index = 0
		for index, e in enumerate(self.context):
			if self.get_timestamp_from_element(e) < timestamp:
				self.context_selection = self.context[:previous_index]
				return self
			previous_index = index
		return self

	def until_timestamp(self, timestamp):
		"""
		Update the selection until the specified timestamp
		"""
		pass

	def delete(self, element = None):
		"""
		Remove the selected elements, or the one specified.
		"""
		if element != None:
			self.context.remove(element)
		else:
			for element in self.context_selection:
				self.context.remove(element)
			self.context_selection = []

	def get_element_list(self):
		return self.context_selection

	def get_param(self, param_type = None):
		"""
		Returns a list of the updated parameters. If param_type is specified,
		returns the list of prameters which names match the name spoecified.
		"""
		if param_type != None:
			return [e for e in self.context_selection if self.get_param_from_element(e) == param_type]
		return [e for e in self.context_selection if self.get_param_from_element(e) not in [DatabaseLog.NEW_MCU_PARAM, DatabaseLog.NEW_ALIAS_PARAM, DatabaseLog.DELETE_MCU] and not re.match(r"^an_.*$", self.get_param_from_element(e))]

	def message(self, update_type, mcu_name, param_name, old_value, new_value, level = LOG_DEFAULT_LEVEL_UPDATE):
		"""
		Print a custom message to log an update.
		"""
		if isinstance(mcu_name, str):
			mcu_name = [mcu_name]
		if old_value:
			old_value = "\33[0;31m%s\33[m" % str(old_value)
		if new_value:
			new_value = "\33[0;31m%s\33[m" % str(new_value)
		param_name = "\33[0;31m%s\33[m" % str(param_name)
		for index, name in enumerate(mcu_name):
			mcu_name[index] = "\33[0;31m%s\33[m" % str(name)

		if old_value and new_value:
			message = "[UPDATE] [%s] %s::%s: `%s' -> `%s'" % (str(update_type.upper()), str("::".join(mcu_name)), str(param_name), str(old_value), str(new_value))
		elif new_value:
			message = "[NEW] [%s] %s::%s: `%s'" % (str(update_type.upper()), str("::".join(mcu_name)), str(param_name), str(new_value))
		else:
			message = "[DELETE] [%s] %s::%s with value `%s'" % (str(update_type.upper()), str("::".join(mcu_name)), str(param_name), str(old_value))

		Log.log_print("custom", self, message, level)

class DatabaseAnalyze(DatabaseLog):
	LOG_ANALYZE_PATH = "analyze.log"
	AN_NEW_MCU = "an_new_mcu"
	AN_EOL_MCU = "an_eol_mcu"
	AN_PRICE_CHANGE = "an_price_change"

	def __init__(self):
		self.analyze_context = None
		super(DatabaseAnalyze, self).__init__()

	def read(self):
		"""
		Load the existing analyzation report.
		"""
		if self.analyze_context != None:
			raise error("Current analyzation report is not empty", self)
		# Load the existing content
		raw_data = read_file(DatabaseAnalyze.LOG_ANALYZE_PATH)
		self.analyze_context = json.loads(raw_data)
		# Load the full database log
		super(DatabaseAnalyze, self).read()

	def write(self):
		# Save the new context
		write_file(DatabaseAnalyze.LOG_ANALYZE_PATH, json.dumps(self.analyze_context))
		# Message
		self.info("Wrote analyzation report `%s'." % (DatabaseAnalyze.LOG_ANALYZE_PATH), 2)

	def analyze_add_data(self, db, analyze, element, uniq = None, arg_list = None, group_by_manufacturer = True, merge_uniq = None):
		"""
		This function is generic to add data to the analyzation structure
		{
			'an_new_mcu': {
				'microchip': {
					"report_week": "",
					"report_month": "",
					"report_quarter": "",
					"report_semester": "",
					"report_year": "",
					"data": [
						[timestamp, 'pic18fxxx', "production"]
					]
				}
			}
		}
		"""
		item_name = self.get_item_name_from_element(element)
		# Make sure the MCU still exists
		if db.find_item(item_name) == None:
			# This MCU does not exists anymore, remove the entry
			self.warning("This item `%s' does not exists." % str(item_name))
			return
		# Group by anaylze type
		if not self.analyze_context.has_key(analyze):
			self.analyze_context[analyze] = {}
		context = self.analyze_context[analyze]
		# If groupped by manufacturer
		if group_by_manufacturer:
			manufacturer = db.get_item_param_value(item_name, "CategoryDeviceManufacturer")
			if manufacturer == "":
				manufacturer = "unknown"
			if not context.has_key(manufacturer):
				context[manufacturer] = {}
			context = context[manufacturer]
		# Make sure there is a "data" element
		if not context.has_key("data"):
			context["data"] = []
		# Format the current data
		timestamp = self.get_timestamp_from_element(element)
		data = [timestamp]
		if uniq != None: data.append(uniq)
		if arg_list != None: data.extend(arg_list)
		# If there is a uniq ID, look for it in the list
		found = False
		if uniq != None:
			for d in context["data"]:
				if d[1] == uniq:
					if merge_uniq != None:
						merge_uniq(data, d)
					context["data"].remove(d)
					found = True
		# Add the current data and sort the list by timestamp
		inserted = False
		for index, d in enumerate(context["data"]):
			# timestamp context[index] <= timestamp element
			if d[0] <= data[0]:
				context["data"].insert(index, data)
				inserted = True
				break
		if not inserted:
			context["data"].append(data)
		# Print a message
		if not found:
			self.info("Adding `%s' to be analyzed." % (str(data)), 3)

	def analyze_get_data(self, data, timestamp):
		"""
		Retrieve the raw data from a group
		"""
		previous_index = 0
		for index, d in enumerate(data):
			if d[0] < timestamp:
				return data[:previous_index]
			previous_index = index
		return data

	def analyze_add_new_mcu(self, db, element, value = None):
		item_name = self.get_item_name_from_element(element)
		if value == None:
			value = self.get_value_from_element(element)
		self.analyze_add_data(db, DatabaseAnalyze.AN_NEW_MCU, element, uniq = item_name, arg_list = [value], group_by_manufacturer = True)

	def analyze_generate_report_new_mcu(self, db, key, timestamp):
		string_list = []
		device_string_list = []
		for manufacturer, raw_data in self.analyze_context[DatabaseAnalyze.AN_NEW_MCU].iteritems():
			data = self.analyze_get_data(raw_data["data"], timestamp)
			if len(data) == 0:
				continue
			device_list = [x[1] for x in data]
			device_string_list.append("%s: %s" % (str(manufacturer), ", ".join(device_list)))
			report_list = self.analyze_similarities(db, device_list, manufacturer)
			report = "%s: %i new device(s)" % (str(manufacturer), len(data))
			if len(report_list) > 0:
				report = "%s (%s)" % (report, ", ".join(report_list))
			string_list.append(report)
		self.info("For `%s', %s\n%s" % (str(key), ", ".join(string_list), "\n".join(device_string_list)), 1)

	def analyze_add_eol_mcu(self, db, element, value = None):
		item_name = self.get_item_name_from_element(element)
		if value == None:
			value = self.get_value_from_element(element)
		self.analyze_add_data(db, DatabaseAnalyze.AN_EOL_MCU, element, uniq = item_name, arg_list = [value], group_by_manufacturer = True)

	def analyze_generate_report_eol_mcu(self, db, key, timestamp):
		string_list = []
		device_string_list = []
		for manufacturer, raw_data in self.analyze_context[DatabaseAnalyze.AN_EOL_MCU].iteritems():
			data = self.analyze_get_data(raw_data["data"], timestamp)
			if len(data) == 0:
				continue
			device_list = [x[1] for x in data]
			device_string_list.append("%s: %s" % (str(manufacturer), ", ".join(device_list)))
			report_list = self.analyze_similarities(db, device_list, manufacturer)
			report = "%s: %i End Of Life device(s)" % (str(manufacturer), len(data))
			if len(report_list) > 0:
				report = "%s (%s)" % (report, ", ".join(report_list))
			string_list.append(report)
		self.info("For `%s', %s\n%s" % (str(key), ", ".join(string_list), "\n".join(device_string_list)), 1)

	def analyze_add_pricing_change(self, db, element):
		item_name = self.get_item_name_from_element(element)
		price = self.get_value_from_element(element)
		previous_price = self.get_previous_value_from_element(element)
		self.analyze_add_data(db, DatabaseAnalyze.AN_PRICE_CHANGE, element, uniq = item_name, arg_list = [previous_price, price], group_by_manufacturer = True)

	def analyze_generate_report_pricing_change(self, db, key, timestamp):
		string_list = []
		for manufacturer, raw_data in self.analyze_context[DatabaseAnalyze.AN_PRICE_CHANGE].iteritems():
			data = self.analyze_get_data(raw_data["data"], timestamp)
			if len(data) == 0:
				continue
			device_list = [x[1] for x in data]
			old_values = [x[2] for x in data]
			new_values = [eval(x[3]) for x in data]
			sum_change = 0
			count = 0
			for i in range(len(data)):
				old = to_number(old_values[i][0][0])
				new = to_number(new_values[i][0][0])
				if old and new:
					sum_change += (new - old) / old * 100
					count = count + 1
			change = 0
			if count:
				change = sum_change / count
			report_list = self.analyze_similarities(db, device_list, manufacturer)
			report = "%s: %i device(s) had their pricing revisited (average: %i.2%%)" % (str(manufacturer), len(data), change)
			if len(report_list) > 0:
				report = "%s (%s)" % (report, ", ".join(report_list))
			string_list.append(report)
		self.info("For `%s', %s" % (str(key), ", ".join(string_list)), 1)

	def analyze_similarities(self, db, mcu_list, manufacturer=".*"):
		"""
		This function will find similarities accross the MCUs specified in the mcu_list
		"""

		def populate(string):
			"""
			This closure replaces the %...% strings by there values
			"""
			string = string.replace("%MANUFACTURER%", manufacturer)
			string = string.replace("%VALUE%", value)
			string = string.replace("%TOTAL%", str(len(mcu_list)))
			string = string.replace("%WEIGHT%", str(weight))
			if 'result' in locals():
				string = string.replace("%RESULT%", str(result))
			return str(string)

		parameters_to_analyze = {
			"CategoryDeviceFamily": [
				{'select': "CategoryDiscovered=automatic;CategoryDeviceManufacturer=%MANUFACTURER%;CategoryDeviceFamily=%VALUE%",
				'compare': 'number', 'eval': "%WEIGHT% == %RESULT%", 'report': "Family `%VALUE%'"},
				{'select': "CategoryDiscovered=automatic;CategoryDeviceManufacturer=%MANUFACTURER%;CategoryDeviceFamily=%VALUE%",
				'compare': 'number', 'eval': "%RESULT% > 0 and %WEIGHT%. / %RESULT%. > 0.3", 'report': "%WEIGHT% `%VALUE%' out of %RESULT%"}
			],
			"CategoryDeviceTopFamily": [
				# If there is more than 70% of the device that are part of this top family
				# and this concerns more than 10 devices
				{'select': "CategoryDiscovered=automatic;CategoryDeviceManufacturer=%MANUFACTURER%;CategoryDeviceTopFamily=%VALUE%",
				'compare': 'number', 'eval': "%WEIGHT%. / %TOTAL%. > 0.7 and %WEIGHT% > 10", 'report': "%WEIGHT% `%VALUE%'"}
			],
		}
		report_list = []
		# Group the data by similarities and sort them
		for param in parameters_to_analyze.keys():
			similarity = []
			for mcu_name in mcu_list:
				value = db.get_item_param_value(mcu_name, param)
				# Empty values are discarded
				if value == "":
					continue
				# Add the value to the list
				found = False
				for v in similarity:
					if v[1] == value:
						found = True
						v[0] = v[0] + 1
						break
				if not found:
					similarity.append([1, value])
			similarity = sorted(similarity, key = lambda s: s[0], reverse = True)
			# Analyze the data
			# Loop through the values added
			for v in similarity:
				weight = v[0]
				value = v[1]
				# Loop through the conditions for this parameter
				condition_list = parameters_to_analyze[param]
				for condition in condition_list:
					device_selector = populate(condition["select"])
					# Select the devices from the database
					selector = DatabaseSelector(str(device_selector))
					selector.select(db)
					match_list = selector.get_match_list()
					# Compare selection
					if condition['compare'] == "number":
						result = len(match_list)
					else:
						raise error("Unknown comparing keyword.", self)
					# Compare with the threshold
					evaluate = populate(condition["eval"])
					if eval(str(evaluate)):
						report = populate(condition["report"])
						report_list.append(report)
						# Only the first valid condition is taken into account
						break
		return report_list

	def analyze(self, db):
		# Handle new MCUs
		# A new MCU is either a MCU which changed status
		for e in self.get_param("CategoryDeviceStatus"):
			if self.get_value_from_element(e) in ["announced", "sampling", "production"]:
				self.analyze_add_new_mcu(db, e)
		# Or a MCU which tagged as new
		for e in self.get_param(DatabaseLog.NEW_MCU_PARAM):
			self.analyze_add_new_mcu(db, e, "new")

		# Handle EOL MCUs
		# A new MCU is either a MCU which changed status
		for e in self.get_param("CategoryDeviceStatus"):
			if self.get_value_from_element(e) in ["mature"]:
				self.analyze_add_eol_mcu(db, e)

		# Handle pricing change
		# A price change must have a valid price before
		for e in self.get_param("CategoryPricing"):
			previous = self.get_previous_value_from_element(e)
			if previous and len(previous):
				self.analyze_add_pricing_change(db, e)

		# Generate the reports
		t = self.get_timestamp()
		for info in [['report_week', t-7*24*3600],
				['report_month', t-30*24*3600],
				['report_quarter', t-3*30*24*3600],
				['report_semester', t-6*30*24*3600],
				['report_year', t-365*24*3600]]:
			key = info[0]
			timestamp = info[1]
			self.analyze_generate_report_new_mcu(db, key, timestamp)
			self.analyze_generate_report_eol_mcu(db, key, timestamp)
			self.analyze_generate_report_pricing_change(db, key, timestamp)

	def cleanup(self):
		"""
		This function will remove old data and keep only the recent and important one.
		"""
		# Cleanup all the parameters older than 1 week.
		pass

class Database(MCULibClass):
	xsd_path = "mculib/schema.xsd"
	xml_pattern = ".*.xml"
	basedir_tag = "basedir"
	fromfile_tag = "fromfile"
	mcu_tag = "mcu"
	name_attr = "name"
	param_attr = "param"
	group_tag = "group"
	param_tag = "param"
	alias_tag = "alias"
	database_log = None

	def __init__(self, database_path = ".", record = True):
		# Initialize the tracking change interface
		self.database_log = DatabaseLog(record)

		# Database path
		self.database_path = database_path

		# XML schema
		xsd = ET.parse(self.xsd_path)
		self.schema = ET.XMLSchema(xsd)

		# Parse all XML files
		self.root = ET.Element("mculib")
		self.tree = ET.ElementTree(self.root)
		self._include_all_subdirs(self.root, database_path)

	def log(self, activate = True):
		self.database_log.reset()
		return self.database_log

	def get_mcu_list(self):
		"""
		Retrieve the list of MCUs
		"""
		return self.root.findall(".//%s" % (self.mcu_tag))

	def get_group_list(self):
		"""
		Retrieve the list of group
		"""
		return self.root.findall(".//%s" % (self.group_tag))

	def get_alias_list(self, item = None):
		"""
		Retrieve the list of alias for a specific item
		"""
		if item == None:
			return self.root.findall(".//%s" % (self.alias_tag))
		return item.findall("%s" % (self.alias_tag))

	def create_mcu(self, mcu_name):
		"""
		Create a new MCU. If it already exists, return the existing
		instance.
		"""
		# If the device does not exists, create it
		mcu = self.find_mcu(mcu_name)
		if mcu == None:
			mcu = ET.Element(self.mcu_tag)
			mcu.set(self.name_attr, mcu_name)
			self.root.append(mcu)
			self.database_log.add(self.get_name(mcu), DatabaseLog.NEW_MCU_PARAM)
		# Return the instance
		return mcu

	def create_group(self, group_name, group_param):
		"""
		Create a new group. If it already exists, return the existing
		instance.
		"""

		# If group_name is not specified or null, try to generate one
		if group_name == "" or not group_name:
			group_name = self.param_to_class(group_param).get_default_value()
			# If its is null or this generated group name already exists, skip
			if group_name == "" or self.find_group(group_name, group_param) != None:
				raise error("The group generated is null or already exists, this should not happend.")

		# If the device does not exists, create it
		group = self.find_group(group_name, group_param)
		if group == None:
			self.info("[CREATE] Creating a new group: `%s::%s'" % (str(group_param), str(group_name)), 1)
			group = ET.Element(self.group_tag)
			group.set(self.name_attr, group_name)
			group.set(self.param_attr, group_param)
			self.root.append(group)

		# Return the instance
		return group

	def create_alias(self, item, alias_name):
		"""
		This function creates an alias to the current item.
		If the alias already exists, returns it.
		"""
		# If the device does not exists, create it
		alias = self.find_alias(item, alias_name)
		if alias == None:
			alias = ET.Element(self.alias_tag)
			alias.set(self.name_attr, alias_name)
			item.append(alias)
			self.database_log.add([self.get_name(item), alias_name], DatabaseLog.NEW_ALIAS_PARAM)
		# Return the instance
		return alias

	def has_param(self, mcu, param_type):
		"""
		Test if a device has a parameter and this parameter value is not null
		"""
		param_list = self.get_parameters(mcu, param_type)
		for param in param_list:
			value = self.get_param_value(param)
			if value != "" and value != []:
				return True
		return False

	def get_parameters(self, item, param_type = None):
		"""
		Return a list of parameters for the specific item.
		"""
		param_list = []
		if param_type:
			# Look for parameters owned by the entity
			param_list = item.findall("%s[@type='%s']" % (self.param_tag, param_type))
			# Check if this parameter is part of a group
			if self.param_to_class(param_type).is_group_item():
				group_param = self.param_to_class(param_type).get_group_param()
				# Find the name of the group
				group_name = self.get_parameter(item, group_param)
				if group_name != None:
					group_name = self.get_param_value(group_name)
					# Look for the group
					group = self.find_group(group_name, group_param)
					if group != None:
						param_list.extend(self.get_parameters(group, param_type))
		else:
			param_list = item.findall("%s" % (self.param_tag))
			# Include group parameters as well
			for param in param_list:
				if self.param_to_class(param).is_group():
					# Find the group parameter and includes its parameters
					group = self.find_group(self.get_param_value(param), self.param_to_class(param).get_group_param())
					if group != None:
						# Add recursively items from this group
						param_list.extend(self.get_parameters(group))

		return param_list

	def get_item_param_value(self, item, param_type, include_aliases = True, first_if_multi = False):
		"""
		Helper function.
		From an item, returns the parameter value
		"""
		if isinstance(item, str) or isinstance(item, list):
			results = self.find_item(item, allow_multiple = True, include_aliases = include_aliases)
			if len(results) == 0:
				raise error("This MCU (%s) cannot be identified." % (str(item)), self)
			item = results
		# Make sure the item is not a list
		if isinstance(item, list):
			if len(item) > 1 and first_if_multi == False:
				raise error("Multiple MCU identified, there should be only 1.", self)
			item = item[0]
		# Return the first item of the list
		param = self.get_parameter(item, param_type)
		if param == None:
			return ""
		return self.get_param_value(param)

	def get_parameter(self, mcu, param_type):
		"""
		Helper function.
		Return the parameter. If more than 1 parameter of the same type is present,
		return an error. If none is found. return None.
		"""
		param_list = self.get_parameters(mcu, param_type)
		if len(param_list) == 0:
			return None
		elif len(param_list) == 1:
			return param_list[0]
		raise error("%i parameters of the type `%s' has been found for this device (%s), there should be only 1." % (len(param_list), str(param_type), str(self.get_name(mcu))), self)

	def create_param(self, item, param_type):
		"""
		This function creates a parameter and associate it to an item
		"""
		# If the parameter is part of a group
		param_class = self.param_to_class(param_type)
		if param_class.is_group_item():
			group_param = param_class.get_group_param()
			# Find out the group name or generate it if it does not exists
			group_name = self.get_parameter(item, group_param)
			if group_name == None:
				group = self.create_group("", group_param)
				# Link this group with the item
				self.set_item_parameter(item, self.param_to_class(group_param).to_param(), self.get_name(group))
				item = group
			else:
				# If the group name already exists, get the group
				group_name = self.get_param_value(group_name)
				item = self.create_group(group_name, group_param)

		# Create a parameter and associate it to the item
		param = ET.Element(self.param_tag)
		param.set('type', param_type)
		item.append(param)

		return param

	def delete_param(self, param):
		"""
		Delete a parameter from the tree
		"""
		item = self.get_param_parent(param)
		item.remove(param)
		self.set_change_value(item)
		value = ""
		name = ""
		type = ""
		try:
			name = self.get_name(item)
			# Update the name if possible
			mcu = self.get_mcu(item)
			if mcu != item:
				name = "%s::%s" % (self.get_name(mcu), name)
			type = self.get_param_type(param)
			value = self.get_param_value(param)
		except:
			pass
		self.database_log.add(name, type, "", value)

	def delete_alias(self, alias):
		"""
		Delete a parameter from the tree
		"""
		name = ""
		item = self.get_param_parent(alias)
		try:
			name = [self.get_name(item), self.get_name(alias)]
		except:
			pass
		item.remove(alias)
		self.set_change_value(item)
		self.database_log.add(name, DatabaseLog.DELETE_ALIAS)

	def merge_param_value(self, param, original, new, trustability):

		# Identify the type of the parameter
		param_type = self.get_param_type(param)
		# Identify the merging strategy
		if int(trustability) > self.get_param_trustability(param):
			strategy = self.param_to_class(param_type).config_merge_trust_strategy
		else:
			strategy = self.param_to_class(param_type).config_merge_with_original_strategy
		# Identify the merging conflict
		options = self.param_to_class(param_type).config_merge_options
		# Merge the value according to their format
		if self.is_param_list(param_type):
			return merge_lists(original, new, strategy | MERGE_REMOVE_DUPLICATES, options)
		else:
			return merge_values(original, new, strategy, options)

	def get_param_info(self, param):
		"""
		This function will pack all parameter information into a structure and return it
		"""
		return {
			'param_type': self.get_param_type(param),
			'value': self.get_param_value(param),
			'trustability': self.get_param_trustability(param),
			'source': self.get_param_source(param)
		}

	def set_mcu_info(self, mcu, param_info):
		"""
		This function will set MCU information from a param_info structure
		"""
		self.set_item_parameter(mcu, param_info["param_type"], param_info["value"], param_info["trustability"], param_info["source"])

	def set_item_parameter(self, item, param_type, value = None, trustability = TRUSTABILITY_AUTO, source = None, force = False, allow_timestamp_update = True, timestamp = None):
		"""
		Set a new parameter or update an existing parameter.
		Item must be valid and exists.
		force: Set to True if you don't want the funciton to check any previous values.
		"""
		# By default the timestamp will not be modified
		update_timestamp = False

		# Look for the parameter
		param = self.get_parameter(item, param_type)

		# Get the MCU associated to this param
		mcu = self.get_mcu(item)

		# Update the values
		if value != None:

			# Debug
			if debug_trace_match(param_type):
				value_before_merge = value

			# Merge the new value with the previous one
			if param != None:
				original_value = self.get_param_value(param)
				# Merge only if force is set to False
				if not force:
					# Merge the values
					value = self.merge_param_value(param, original_value, value, trustability)
			else:
				original_value = self.get_param_empty_value(param_type)

			# Debug
			if debug_trace_match(param_type):
				self.debug("Original value: `%s' - New value before merge: `%s' - New value after merge: `%s'" % (str(original_value), str(value_before_merge), str(value)))

			# Param class
			param_class = self.param_to_class(param_type)

			# Clean-up list categories: remove duplicate values
			if self.is_param_list(param_class) and len(value) > 1:
				# Loop through the values and merge them 1 by 1
				new_value = [value[0]]
				for v in value[1:]:
					new_value = merge_lists(new_value, v, strategy = MERGE_STRATEGY_REPLACE | MERGE_REMOVE_DUPLICATES, options = param_class.config_merge_options)
				value = new_value

			# Clean-up multi-value categories: apply the cleaning rules
			if self.is_param_multi(param_class):
				if not self.is_param_list(param_class):
					value = [value]
				new_value = []
				# Clean the values if needed
				for v in value:
					v = clean_list(v, options = param_class.config_merge_options)
					new_value.append(v)
				# Set back the value if needed
				if not self.is_param_list(param_class):
					new_value = new_value[0]
				value = new_value

			# Clean the value itself
			value = clean_value(value)

			# If from an alias, look if it needs to be merged with MCU
			if self.is_item_alias(item):
				# Merge the parameter with the parent one
				if param_class.config_alias_merge_with_mcu:
					self.set_item_parameter(mcu, param_type, value, TRUSTABILITY_AUTO_REDUCED, source)
				# Delete the parameter if the parent one is the same
				if param_class.config_alias_delete_if_duplicate:
					mcu_param = self.get_parameter(mcu, param_type)

					# If the value registered to the parent MCU has more info or if they are equal:
					if mcu_param != None:
						if self.is_param_list(param_class):
							r = list_compare(self.get_param_value(mcu_param), value)
						else:
							r = value_compare(self.get_param_value(mcu_param), value)
						if r in [-1, 0]:
							# Delete the parameter if it exists
							if param != None:
								self.delete_param(param)
							return

			# If it does not exists, create a new one
			if param == None:
				param = self.create_param(item, param_type)

			# Set the new value
			param.set('value', str(value))

			# Notify if the value has changed
			if str(value) != str(original_value) or self.is_param_force_update(param_type):
				self.set_change_value(mcu)
				update_timestamp = True
				# When a value has been set manually but for some reason it has been modified, notify that it needs to be checked
				if self.get_param_trustability(param) != TRUSTABILITY_AUTO and int(trustability) > self.get_param_trustability(param):
					trustability = str(TRUSTABILITY_NEED_CHECK)
					force = True
				if str(value) != str(original_value) and not self.is_param_silent(param_type):
					str_name_log = [self.get_name(item)]
					if mcu != item:
						str_name_log.insert(0, self.get_name(mcu))
					self.database_log.add(str_name_log, self.get_param_type(param), str(value), original_value, trustability)

		# If the param does not exists at this point, create it
		if param == None:
			param = self.create_param(item, param_type)

		# Check the trustability index of this data
		update = False
		if force or int(trustability) <= self.get_param_trustability(param):
			update = True

		# Update extra parameters (trustability/source)
		if update and source != None and self.get_param_source(param) != str(source):
			self.set_param_source(param, source)
		if update and trustability != None and str(self.get_param_trustability(param)) != str(trustability):
			self.set_param_trustability(param, trustability)

		# Update the timestamp only if the value has been modified
		if allow_timestamp_update and update_timestamp:
			self.set_change_value(mcu)
			if timestamp == None:
				timestamp = time.time()
			date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timestamp))
			param.set('date', date_str)

	def param_to_class(self, param):
		"""
		Convert a parameter type to a class
		"""
		if isinstance(param, str):
			return eval(param)
		if isinstance(param, type) and issubclass(param, GenericCategory):
			return param
		try:
			return eval(self.get_param_type(param))
		except:
			raise error("Unknown param type argument `%s'." % (str(self.get_param_type(param))))

	def is_param_list(self, param):
		"""
		Check if this parameter is a list
		"""
		return issubclass(self.param_to_class(param), GenericListCategory) or issubclass(self.param_to_class(param), GenericMultiListCategory)

	def is_param_multi(self, param):
		"""
		Check if this parameter is a multiple-value parameter
		"""
		return issubclass(self.param_to_class(param), GenericMultiCategory) or issubclass(self.param_to_class(param), GenericMultiListCategory)

	def is_param_silent(self, param):
		"""
		Return True if the parameter is silent, False otherwise
		"""
		return self.param_to_class(param).config_silent

	def is_param_force_update(self, param):
		"""
		Check if this parameter needs requires allways updates
		"""
		return self.param_to_class(param).config_always_update

	def get_param_type(self, param):
		"""
		Get the parameter type
		"""
		return param.attrib["type"]

	def get_param_value(self, param):
		"""
		Get the parameter value
		"""
		# Handle the list cases
		if self.is_param_list(param) or self.is_param_multi(param):
			if param.attrib.has_key("value"):
				try:
					return eval(param.attrib["value"])
				except:
					raise error("The value of " + self.get_param_type(param) + " is not correctly formated.", self)
			return []
		# Handle the normal string cases
		elif param.attrib.has_key("value"):
			return param.attrib["value"]
		return ""

	def get_param_empty_value(self, param):
		"""
		Get the empty value of a parameter
		"""
		if self.is_param_list(param) or self.is_param_multi(param):
			return []
		return ""

	def get_param_date(self, param):
		"""
		Get the parameter date.
		Returns a timestamp.
		"""
		if param.attrib.has_key("date"):
			time_tuple = time.strptime(param.attrib["date"], "%Y-%m-%d %H:%M:%S")
			return time.mktime(time_tuple)
		return None

	def get_param_comment(self, param):
		"""
		Get the parameter comment.
		"""
		if param.attrib.has_key("comment"):
			return param.attrib["comment"]
		return ""

	def set_param_comment(self, param, comment):
		"""
		Set the comment of a parameter
		"""
		self.set_change_value(self.get_param_parent(param))
		self.log().add_comment(self.get_name(self.get_param_parent(param)), self.get_param_type(param), comment, self.get_param_comment(param))
		param.set('comment', str(comment))

	def set_param_source(self, param, source):
		"""
		Set the source of a parameter
		"""
		self.set_change_value(self.get_param_parent(param))
		self.log().add_source(self.get_name(self.get_param_parent(param)), self.get_param_type(param), source, self.get_param_source(param))
		param.set('source', str(source))

	def get_param_source(self, param):
		"""
		Get the parameter source
		"""
		if param.attrib.has_key("source"):
			return param.attrib["source"]
		return ""

	def get_param_trustability(self, param):
		"""
		Get the parameter source
		"""
		if param.attrib.has_key("trustability"):
			return int(param.attrib["trustability"])
		return TRUSTABILITY_AUTO

	def set_param_trustability(self, param, trustability):
		"""
		Set the trustability parameter
		"""
		# Make sure this is a number
		if str(to_number(trustability)) != str(trustability):
			raise error("The trustability index is not a number.")
		if int(trustability) > TRUSTABILITY_AUTO or int(trustability) < TRUSTABILITY_OK:
			raise error("The trustability value (=%i) is out of range." % (trustability))
		self.set_change_value(self.get_param_parent(param))
		self.log().add_trustability(self.get_name(self.get_param_parent(param)), self.get_param_type(param), trustability, self.get_param_trustability(param))
		param.set('trustability', str(trustability))

	def get_param_parent(self, param):
		"""
		Get the item associated with this MCU
		"""
		return param.getparent()

	def get_mcu(self, param):
		"""
		This function returns the MCU associated with the parameter.
		If the parameter is a child of an alias, it will look up and find the MCU.
		"""
		if param.tag == self.param_tag:
			mcu = self.get_param_parent(param)
			if self.is_item_alias(mcu):
				mcu = self.get_param_parent(mcu)
		elif param.tag == self.alias_tag:
			mcu = self.get_param_parent(param)
		elif param.tag == self.mcu_tag:
			mcu = param
		else:
			raise error("This item is from an unknown type.")
		# Make sure this is a MCU
		if not self.is_item_mcu(mcu):
			raise error("The parent item %s::`%s' of %s::`%s' is not a MCU." % (str(mcu.tag), self.get_name(mcu), str(param.tag), self.get_name(param)))
		return mcu

	def move_param_to_mcu(self, param, mcu):
		"""
		This function will move a parameter from an item to another
		"""
		param_info = self.get_param_info(param)
		self.delete_param(param)
		self.set_mcu_info(mcu, param_info)

	def get_name(self, mcu):
		"""
		Get the MCU name
		"""
		if mcu.attrib.has_key(self.name_attr):
			return mcu.attrib[self.name_attr]
		return None

	def is_item_mcu(self, item):
		"""
		Returns True if the item is a MCU, False otherwise.
		"""
		return (str(item.tag) == self.mcu_tag)

	def is_item_alias(self, item):
		"""
		Returns True if the item is an alias, False otherwise.
		"""
		return (str(item.tag) == self.alias_tag)

	def is_item_group(self, item):
		"""
		Returns True if the item is a group, False otherwise.
		"""
		return (str(item.tag) == self.group_tag)

	def has_changed(self, mcu):
		"""
		Returns True if the mcu has been changed, False otherwise.
		"""
		return bool(mcu.tail)

	def set_change_value(self, mcu, value = True):
		"""
		Set the change value to true or false
		"""
		if not isinstance(value, bool):
			raise error("The value argument is not a boolean.")
		if not value:
			mcu.tail = None
		else:
			mcu.tail = str(value)

	def delete_item(self, item):
		"""
		Delete the selected item
		"""
		file_name = self.get_item_filename(item)
		self.database_log.add(self.get_name(item), DatabaseLog.DELETE_MCU)
		os.remove(file_name)

	def write_all(self):
		"""
		Write all items that have changed
		"""
		self.info("Write to database.", 1)
		for mcu in self.get_mcu_list():
			self._write(mcu)
		for group in self.get_group_list():
			self._write(group)
		# Write the database log as well
		self.log().write()

	def get_item_filename(self, item):
		"""
		Return the filename of an item
		"""
		# Use the existing file name or generate a default one
		if item.attrib.has_key(self.fromfile_tag):
			file_name = item.attrib[self.fromfile_tag]
		else:
			base_path = self.database_path
			# If this is a group, use the config_group_path
			if self.is_item_group(item):
				group_param_type = item.get(self.param_attr)
				group = self.param_to_class(group_param_type)
				base_path = os.path.join(base_path, group.config_group_path)
			else:
				# If the device has a manufacturer, store the file under its manufacturer directory name
				manufacturer = self.get_item_param_value(item, "CategoryDeviceManufacturer")
				if manufacturer != "":
					base_path = os.path.join(base_path, manufacturer.lower())
			# Create the directory architecture if it does not exists
			if not os.path.exists(base_path):
				os.makedirs(base_path)
			file_name = os.path.join(base_path, self.get_name(item) + ".xml")
		return file_name

	def _write(self, item):
		"""
		Write the XML file describing an item. This function is private.
		"""
		# Write to the file only if the item has changed
		if not self.has_changed(item):
			return
		# Clear the changed flag
		self.set_change_value(item, False)
		# Use the existing file name or generate a default one
		file_name = self.get_item_filename(item)
		if item.attrib.has_key(self.fromfile_tag):
			del item.attrib[self.fromfile_tag]
		# Message
		self.info("Write `%s' to file `%s'." % (self.get_name(item), file_name), 3)
		ET.write(file_name, item)
		# Add the fromfile tag
		item.attrib[self.fromfile_tag] = file_name

	def find_item(self, name, allow_multiple = False, include_aliases = False):
		"""
		Look for an item, name can be then a list
		"""
		if isinstance(name, str):
			return self.find_mcu(name, allow_multiple = allow_multiple, include_aliases = include_aliases)
		elif isinstance(name, list)and len(name) == 1:
			return self.find_mcu(name[0], allow_multiple = allow_multiple, include_aliases = False)
		elif isinstance(name, list) and len(name) == 2:
			item_list = self.find_mcu(name[0], allow_multiple = True, include_aliases = False)
			if len(name) == 2:
				match_list = []
				for item in item_list:
					alias_list = self.find_alias(item, name[1], allow_multiple = True)
					match_list.extend(alias_list)
				item_list = match_list
			if allow_multiple:
				return item_list
			if len(item_list) == 0:
				return None
			elif len(item_list) != 1:
				raise error("Device selection map contains %s nodes with name `%s', expected 1" % (len(item_list), str(name)))
			else:
				return item_list[0]
		else:
			raise error("Unknown type for `%s'." % (str(name)))
		return None

	def find_mcu(self, name, allow_multiple = False, include_aliases = False):
		"""
		Find a MCU in the database
		"""
		node = self.root.findall("%s[@%s='%s']" % (self.mcu_tag, self.name_attr, name))
		# Include the aliases in the research
		if include_aliases:
			node_bis = self.root.findall(".//%s[@%s='%s']" % (self.alias_tag, self.name_attr, name))
			node = node + node_bis
		if allow_multiple:
			return node
		if len(node) == 0:
			return None
		elif len(node) != 1:
			raise error("Device selection map contains %s nodes with name `%s', expected 1" % (len(node), name))
		else:
			return node[0]

	def find_mcu_match(self, name, include_aliases = False):
		"""
		Find a MCUs in the database
		"""
		node = self.root.xpath("%s[contains(@%s,'%s')]" % (self.mcu_tag, self.name_attr, name))
		# Include the aliases in the research
		if include_aliases:
			node_bis = self.root.xpath(".//%s[contains(@%s,'%s')]" % (self.alias_tag, self.name_attr, name))
			node = node_bis + node
		return node

	def find_group(self, name, param, allow_multiple = False):
		"""
		Find a group in the database
		"""
		node = self.root.findall(".//%s[@%s='%s'][@%s='%s']" % (self.group_tag, self.name_attr, name, self.param_attr, param))
		if allow_multiple:
			return node
		if len(node) == 0:
			return None
		elif len(node) != 1:
			raise error("Group selection map contains %s nodes with name `%s' and id `%s', expected 1" % (len(node), name, param))
		else:
			return node[0]

	def find_alias(self, item, name, allow_multiple = False):
		"""
		Find an alias in the item
		"""
		node = item.findall("%s[@%s='%s']" % (self.alias_tag, self.name_attr, name))
		if allow_multiple:
			return node
		if len(node) == 0:
			return None
		elif len(node) != 1:
			raise error("Alias selection map contains %s nodes with name `%s' and id `%s', expected 1" % (len(node), name, param))
		else:
			return node[0]

	def merge_item(self, item_dst, item_src):
		"""
		Merge an item into another.
		"""
		for param in self.get_parameters(item_src):
			param_type = self.get_param_type(param)
			# Do not merge certain parameters
			if param_type in ["CategoryDeviceName"]:
				continue
			value = self.get_param_value(param)
			trustability = self.get_param_trustability(param)
			source = self.get_param_source(param)
			self.set_item_parameter(item_dst, param_type, value, trustability, source)

	def print_mcu(self, mcu):
		"""
		Print information about a specific MCU
		"""
		# Print the name (ID) of the MCU
		self.info(self.get_name(mcu), 0)
		for param in self.get_parameters(mcu):
			self.info("\t" + self.get_param_type(param) + ": " + str(self.get_param_value(param)), 0)
		# Print the alias
		alias_list = self.get_alias_list(mcu)
		for alias in alias_list:
			self.info("\t" + self.get_name(alias), 0)
			for param in self.get_parameters(alias):
				self.info("\t\t" + self.get_param_type(param) + ": " + str(self.get_param_value(param)), 0)

	def print_all_mcus(self):
		"""
		Print the device list in a readable way
		"""
		# Iterate through the mcus
		for mcu in self.get_mcu_list():
			self.print_mcu(mcu)

	def sanity_check(self):
		"""
		Make sure all elements in the database validate
		"""
		# Iterate through the MCUs
		for mcu in self.get_mcu_list():
			# Make sure all MCUs have certain mandatory attributes and that it is not empty
			mcu_name = self.get_name(mcu)
			if not mcu_name:
				raise error("This MCU (%s) has no name (%s)" % (self.get_name(mcu), mcu.attrib[self.fromfile_tag]))
			# Make sure it is uniq
			self.find_mcu(mcu_name)
			# Iterate through the attributes
			for param in self.get_parameters(mcu):
				# Make sure all attributes have a type
				if not self.get_param_type(param):
					raise error("This MCU (%s) has an attribute with no type." % (self.get_name(mcu)))
				if param.attrib.has_key("value"):
					# Make sure the list parameters have a correctly formatted value
					if self.is_param_list(param) or self.is_param_multi(param):
						try:
							eval(param.attrib["value"])
						except:
							raise error("This MCU (%s) has a wrong value format for %s (%s)" % (self.get_name(mcu), self.get_param_type(param), param.attrib["value"]))

	def clean_up(self, mcu_list):
		"""
		This function will clean up the database by merging redudant
		information or other tricks.
		"""
		alias_limit_date = time.time() - (1.5 * 30 * 24 * 3600) # 1.5 months
		def is_alias_expired(alias):
			"""
			If this alias is considered as expired, returns the date when last seen
			otherwise, return None.
			"""
			# If the device has not been seen before 3 month
			param = self.get_parameter(alias, "CategoryDiscovered")
			if param != None:
				date = self.get_param_date(param)
				# Check if the date is older than the limit
				if date < alias_limit_date:
					return date
			return None

		#mcu_limit_date = time.time() - (10 * 24 * 3600) # 10 days
		mcu_limit_date = time.time() - (3 * 30 * 24 * 3600) # 3 months
		def is_mcu_expired(mcu):
			"""
			If this MCU is considered as expired, returns the date when last seen
			otherwise, return None.
			"""
			# If the device has not been seen before 3 month
			param = self.get_parameter(mcu, "CategoryDiscovered")
			# If no param, it means that the devices has set manually
			if param == None:
				# Then check when it was set
				param = self.get_parameter(mcu, "CategoryDeviceName")

			date = self.get_param_date(param)
			# Check if the date is older than the limit
			if date < mcu_limit_date:
				last_seen = date
				# Look at the aliases as well
				alias_list = self.get_alias_list(mcu)
				for alias in alias_list:
					date = is_alias_expired(alias)
					if date != None and date > last_seen:
					        last_seen = date
				if last_seen < mcu_limit_date:
					return last_seen

			return None


		def new_mcu():
			# Load the existing content
			log = DatabaseLog()
			log.read()
			# From last week
			log.from_timestamp(int(time.time()) - 7*24*3600)

			selection = log.get_param(DatabaseLog.NEW_MCU_PARAM)
			# Loop through the devices
			for element in selection:
				item_name = log.get_item_name_from_element(element)
				# Read the timestamp
				item_timestamp = log.get_timestamp_from_element(element)
				# Look for the item
				item = self.find_item(item_name)
				# Make sure the MCU still exists
				if item == None:
					# This MCU does not exists anymore, remove the entry
					self.warning("This item `%s' does not exists." % str(item_name))
				self.info("[%s] New device this week `%s'." % (time.strftime("%Y-%m-%d", time.gmtime(item_timestamp)), self.get_name(item)), 1)

		new_mcu()

		self.info("Cleaning-up the database for %i device(s)." % (len(mcu_list)), 1)

		# 0. Make sure the translation table is applied to all categories
		category_translation = [c for c in get_category_list() if len(c.config_translation_table) > 0]
		self.info("Apply translation table in %s." % (", ".join([c.to_param() for c in category_translation])), 2)
		for mcu in mcu_list:
			item_list = [mcu] + self.get_alias_list(mcu)
			for item in item_list:
				for c in category_translation:
					param = self.get_parameter(item, c.to_param())
					if param == None:
						continue
					value = self.get_param_value(param)
					if c.is_list():
						new_value = []
						for v in value:
							new_v = c.parse_translation_table(v)
							# If the output is empty
							if new_v == None or new_v == "":
								new_value.append(v)
							else:
								new_value.append(new_v)
						value = new_value
					self.set_item_parameter(item, c.to_param(), value, trustability = self.get_param_trustability(param), force = True, allow_timestamp_update = False)

		#	for param in param_list:
		#		if self.param_to_class(param).is_group_item():
		#			# Delete the param and re-add it
		#			self.move_param_to_mcu(param, mcu)

		# 1. Move group parameters into their respective groups
		self.info("Move parameters into their respective groups.", 2)
		for mcu in mcu_list:
			param_list = mcu.findall(".//%s" % (self.param_tag))
			for param in param_list:
				if self.param_to_class(param).is_group_item():
					# Delete the param and re-add it
					self.move_param_to_mcu(param, mcu)

		# 2. Set pin count
		self.info("Identify the pin count of the device if not already set.", 2)
		for mcu in mcu_list:
			pin_count = self.get_item_param_value(mcu, "CategoryPin")
			# If the pin count is not set
			if pin_count == "":
				package_list = self.get_item_param_value(mcu, "CategoryPackage")
				for package in package_list:
					if is_number(package[0]):
						if pin_count == "":
							pin_count = package[0]
						elif not is_number(package[0]) or to_number(pin_count) != to_number(package[0]):
							pin_count = "-1"
							break
				if pin_count != "-1" and is_number(pin_count):
					self.set_item_parameter(mcu, "CategoryPin", pin_count)

		# 2. Remove unused groups
	#	self.info("Remove unused groups.", 2)
	#	for group in self.get_group_list():
	#		pass
		# 3. Remove legacy aliases
		limit_date = time.time() - (1.5 * 30 * 24 * 3600) # 1.5 months
		self.info("Removes aliases that have not been seen before `" + time.strftime("%Y-%m-%d", time.gmtime(alias_limit_date)) + "'.", 2)
		for mcu in mcu_list:
			# Retrieve the alias list and loop through it
			alias_list = self.get_alias_list(mcu)
			for alias in alias_list:
				date = is_alias_expired(alias)
				if date != None:
					self.info("Flag `%s::%s' as legacy, last time seen `%s'" % (self.get_name(alias), self.get_name(mcu), time.strftime("%Y-%m-%d", time.gmtime(date))), 0)
					self.delete_alias(alias)

		# 3. Flag as a legacy device if the device has not been updated
		# since 3 months and been discovered automatically.
		# Make sure also that all its aliases have not been discovered for 3 month
		self.info("Flag as legacy devices discovered and not updated before `" + time.strftime("%Y-%m-%d", time.gmtime(mcu_limit_date)) + "'.", 2)
		for mcu in mcu_list:

			# Default value
			set_as_legacy = False
			message = ""

			# Check if it has been discovered automatically
			param = self.get_parameter(mcu, "CategoryDiscovered")

			# If the MCU is considered as expired
			date = is_mcu_expired(mcu)
			if date != None:
				set_as_legacy = True
				message = "last time seen `" + time.strftime("%Y-%m-%d", time.gmtime(date)) + "'"
			# The MCU has been seen in the last x days (not expired) and has been discovered automatically
			elif param != None and self.get_param_value(param) == "automatic":
				# If the device has been set as legacy automatically
				legacy = self.get_parameter(mcu, "CategoryLegacy")
				if legacy != None and self.get_param_value(legacy) == "yes" and self.get_param_source(legacy) == "automatic":
					date = self.get_param_date(param)
					self.info("LEGACY  " + self.get_name(mcu) + " (" + time.strftime("%Y-%m-%d", time.gmtime(date)) + ")", 0)
		#		status = self.get_parameter(mcu, "CategoryDeviceStatus")
		#		if status != None and self.get_param_value(status) == "mature" and self.get_param_source(status) == "automatic":
		#			self.info("MATURE  " + self.get_name(mcu), 0)
			# If the device has been set randomly here and not seen after 3 month
			if param == None or self.get_param_value(param) == "":
				param = self.get_parameter(mcu, "CategoryDeviceName")
				date = self.get_param_date(param)
				# Check if the date is older than the limit
				if date < limit_date:
					set_as_legacy = True
					message = "registered to the database in `" + time.strftime("%Y-%m-%d", time.gmtime(date)) + "', not seen after."

			# Set the device as legacy
			if set_as_legacy:
				param = self.get_parameter(mcu, "CategoryLegacy")
				if param == None or self.get_param_value(param) != "yes":
					self.info("Flag `" + self.get_name(mcu) + "' as a legacy device, " + message, 0)
					self.set_item_parameter(mcu, "CategoryLegacy", "yes", source = "automatic")
					self.set_item_parameter(mcu, "CategoryDeviceStatus", "mature", source = "automatic")

		# 6. Clear prices that have not been updated for 3 month
		limit_date = time.time() - (3 * 30 * 24 * 3600) # 3 month
		self.info("Clear pricing not updated before `" + time.strftime("%Y-%m-%d", time.gmtime(limit_date)) + "'.", 2)
		for mcu in mcu_list:
			# If the price has not been updated before 1 month
			param = self.get_parameter(mcu, "CategoryPricing")
			# If pricing is set and there is at least one value
			if param != None and len(self.get_param_value(param)) >= 1:
				date = self.get_param_date(param)
				# Check if the date is older than the limit
				if date < limit_date:
					self.info("Clear outdated pricing for `" + self.get_name(mcu) + "'", 0)
					self.set_item_parameter(mcu, "CategoryPricing", "[]", source = "automatic", force = True)

		# Call for port-specific actions

		# Look at the the available parser ports
		available_ports = {}
		for parser_port in parser_ports_list:
			parser_class = parser_port['common']
			# Look for the manufacturer name
			manufacturer = parser_class.get_manufacturer()
			available_ports[manufacturer] = parser_class

		self.info("Port specific clean-up actions for %s." % (', '.join([i for i in available_ports.keys()])), 2)

		# Loop through the selected devices
		for mcu in mcu_list:
			# Identify the specific parser port if any
			manufacturer = self.get_item_param_value(mcu, "CategoryDeviceManufacturer")
			if manufacturer in available_ports:
				port = available_ports[manufacturer]
				Log.info("Identified specific device parser (%s) for device `%s'." % (port.__name__, str(mcu)), 3)
				# Call the port function if available
				port.check_device(mcu, self)

	def _all_subdirs_iter(self, basedir):
		all_files = []

		skip_folders = ('.svn', '.git')

		for dirpath, dirnames, files in os.walk(basedir):

			# Remove folders that we do not need to walk into
			for skip_folder in skip_folders:
				if skip_folder in dirnames:
					dirnames.remove(skip_folder)

			for filename in files:
				if not re.match(self.xml_pattern, filename):
					continue
				filename = os.path.join(dirpath, filename)
				pair = (dirpath, filename)
				all_files.append(pair)
				yield pair

	def _include_all_subdirs(self, root_element, basedir):
		"""
		Read all *.xml files in the tree and include them under the root_element
		"""
		self.info("Loading database (%s)..." % (str(basedir)), 2)

		for dirpath, filename in self._all_subdirs_iter(basedir):

			if os.path.getsize(filename) == 0:
				continue

			try:
				subtree = ET.parse(filename)
			except Exception as e:
				raise error(filename + ": " + str(e))
			element = subtree.getroot()

			# Validate XML
			try:
				self.validate_xml(element)
			except ET.DocumentInvalid as e:
				raise error("XML file %s does not validate. Error: %s" % (filename, str(e)))

			# self.info("Parsing XML `" + filename + "'", 3)

			# Add the MCU element to the list
			element.attrib[self.fromfile_tag] = filename
			root_element.append(element)

	def validate_xml(self, tree):
		"""
		Validate the given ElementTree XML tree using the XML schema that is loaded.
		The function raises an ET.DocumentInvalid if the tree does not validate.
		"""
		#if self.schema:
		#	self.schema.assertValid(tree)
