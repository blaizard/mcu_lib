#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from mculib.parser.merge import *
from mculib.categories import *
from mculib.helper import *
from mculib.log import *
from mculib.config import *
import re
import socket
import urllib
import urllib2
import copy
import sys
import unicodedata
import inspect

def parserFetchMerge(env, parser_list, id_list, options):
	"""
	This function will fetch data from multiple parser and merge them into the database
	"""

	# Clone the parser list
	parser_list = [] + parser_list
	# Call the parser
	i = 0

	# Setup the progress log
	Log.log_setup_progress(len(parser_list), identifier = "parser_list")

	# Create an empty parsert that will contain everything
	parser = GenericParserPort()

	while i < len(parser_list):

		# Increase the progress
		Log.log_progress(identifier = "parser_list")

		# Retrieve the class
		manufacturer = parser_list[i]
		# Check if it is a class or an instance
		if inspect.isclass(manufacturer):
			manufacturer = manufacturer()
		# Fetch the data
		manufacturer.fetch(options, id_list = id_list)
		# Add a new parser if needed
		parser_list.extend(GenericParserPort.next_parser_list)

		# Merge the devices into the main parser
		for d in manufacturer.get_devices():
			parser.add_device_to_list(d)

		# Next item
		i = i + 1

	# Merge the parser with the database
	merge_parser_to_db(parser, env.get_db(), trustability = env.get_trustability(), source = env.get_source(), force = env.get_force(), record = env.get_record(), onlyexisting = env.get_only_existing(), onlyMCUorAlias = True)

class Parser(MCULibClass):
	# Device list
	device_list = []
	# Allowable hook names
	hook_names = [
		"pre_discovery",
		"post_discovery",
		"pre_category_discovery",
		"post_category_discovery",
		"pre_device_discovery",
		"post_device_discovery",
		# This covers only modified items
		"post_param_merge_to_db"
	]

	def __init__(self):
		self.clear_device_list()
		# Initialize the hook table
		self.hook_table = {}
		for name in self.hook_names:
			self.hook_table[name] = []
		# Add default hook(s)
		self.hook("post_param_merge_to_db", merge_param_to_db_default_hook)

	def hook_proceed(self, name, *args):
		if name not in self.hook_names:
			raise error("This hook name `%s' is not allowed." % (str(name)), self)
		for fct in self.hook_table[name]:
			fct(*args)

	def hook(self, name, hook_function):
		"""
		Hook a function
		"""
		if name not in self.hook_names:
			raise error("This hook name `%s' is not allowed." % (str(name)), self)
		self.hook_table[name].append(hook_function)

	def add_device_to_list(self, device):
		"""
		Add a new MCU to the device list
		"""
		device_name = device.get_device_name(strict = True, fullname = False)
		# Check if this MCU already exists in the list
		for d in self.device_list:
			if d.get_device_name(strict = True, fullname = False) == device_name:
				self.info("Merge the devices `" + device_name + "' together", 3)
				# List all categories of the device to merge
				for category in device.get_device_categories():
					# 2 cases, either the device (`d') to be merged in already has the category
					c = d.get_device_category(category.to_param(), False)
					if c != None:
						# If so, the 2 values need to be merged
						c.merge(category, c.config_merge_with_original_strategy)
					# Otherwise, it does not have the category and this latter needs to be added
					else:
						# Add the category to this device
						# Hack to bypass the add_category function
						d.categories.append(category)
				# This device has now been merged, so no need to continue the loop or add it to the list
				return

		self.device_list.append(device)

	def add_param(self, mcu_name, param_type, value):
		"""
		Create a MCU with a specific parameter and a specific value and
		add it to the device list.
		"""
		device = Device()
		# If the mcu_name is a list, it measn this is an alias
		if isinstance(mcu_name, list):
			if len(mcu_name) == 2:
				device.add_category("CategoryAlias", mcu_name[0])
				mcu_name = mcu_name[1]
			elif len(mcu_name) == 1:
				mcu_name = mcu_name[0]
			else:
				raise error("The MCU name is not valid, received this `%s'." % (str(mcu_name)))
		# Make sure the mcu_name is a non-empty string
		if not isinstance(mcu_name, str) or mcu_name == "":
			raise error("The MCU name should be a non empty string, received this instead `%s'." % (str(mcu_name)))
		device.add_category("CategoryDeviceName", mcu_name)
		device.add_category(param_type, value)
		self.add_device_to_list(device)

	def get_devices(self):
		"""
		Return the list of MCUs
		"""
		return self.device_list

	def clear_device_list(self):
		"""
		Clear the current device list
		"""
		self.device_list = []

class GenericParserPort(Parser):
	"""
	High level layer
	"""
	# Common options to fetch all the data
	common_options = {}
	# Specific options. This list will be looped through and each item should
	# contain the location where to find the data, plus an 'id' to refer to
	# a 'parser', which is a parser class to tell which kind of data we are
	# dealing with and a 'display' which is a displaying name.
	specific_options_list = []
	# Options
	nb_retries = 2
	# Allow retries in case of failure
	allow_retry = True
	# Ignore the test in case of failure
	allow_ignore = True
	# The next parsers to be executed
	next_parser_list = []

	def __init__(self, options = {}):
		"""
		Initialize the common options
		"""
		self.common_options = options
		super(GenericParserPort, self).__init__()

	@staticmethod
	def get_manufacturer():
		"""
		Return the name of the manufacturer associated with this parser.
		Return an empty string if none is associated.
		"""
		return ""

	@staticmethod
	def check_device(mcu, db):
		"""
		This function is called to check devices and clean up info about a certain device.
		It is also used to set specific info on a device with its name and other paramters.
		"""
		pass

	def get_options(self, options):
		"""
		Returns the common options for this parser, this function must be set
		"""
		raise error("`get_options' is missing for this parser, you must add it.")

	def update_options(self, page, options):
		"""
		Update the data of the page
		"""
		return {}

	@classmethod
	def add_next_parser(cls, parser = None):
		"""
		This function adds a new parser to be executed next
		"""
		if parser == None:
			cls.next_parser_list = []
		else:
			cls.next_parser_list.append(parser)

	def fetch(self, global_options = {}, id_list = None):
		"""
		Fetch data from this port.
		"""
		# Clean the results
		GenericParserPort.add_next_parser()

		# Setup the progress log
		Log.log_setup_progress(len(self.specific_options_list), identifier = "specific_options")

		# Loop through all the options
		for index, specific_options in enumerate(self.specific_options_list):

			# Increase the progress
			Log.log_progress(identifier = "specific_options")

			# If an ID list is specified, parse only those
			if id_list:
				is_match = False
				for id_regexpr in id_list:
					if re.search(id_regexpr, specific_options['id']):
						is_match = True
			 	if not is_match:
					continue

			# --------------- OPTIONS
			# Merge the common options this specific options
			options = object_clone(global_options)
			options = object_merge(options, self.common_options)
			options = object_merge(options, self.get_options(options))
			options = object_merge(options, specific_options)

			# Ensure that all required data are present
			for key in ["id", "display", "data"]:
				if not options.has_key(key) or not options[key]:
					raise error("This parser is missing its `%s' attribute." % (str(key)), self)

			# Ignore this parser if needed
			if options.has_key("ignore") and options["ignore"] == True:
				return

			# Print message
			msg_append = ""
			if options.has_key("device"):
				msg_append = "(`%s')" % (options["device"])
			self.info("Fetching data from %s::%s%s" % (str(self.__class__.__name__), str(options["display"]), msg_append), 1)
			GenericParser.set_log_context(parser = "%s::%s%s" % (str(self.__class__.__name__), str(options["display"]), msg_append))

			# -----------------------

			# Support paging
			reiterate = True
			page_current = 0
			page_total = 1
			abort = False
			while page_current < page_total:

				# Create the main parser
				main_parser = GenericParser()

				# Load the specific configuration
				self.setup_parser_rules(main_parser)

				# Update the options
				options = object_merge(options, self.update_options(page_current, options))

				# Handle paging
				if options.has_key("paging") and options["paging"]:
					if page_total == 1:
						self.info("Fetching data for page %i" % (page_current + 1), 1)
					else:
						self.info("Fetching data for page %i/%i" % (page_current + 1, page_total), 1)

				# Make sure the options["data"] is a list
				if not isinstance(options["data"], list):
					options["data"] = [options["data"]]

				for data_index, data_options in enumerate(options["data"]):

					# --------------- OPTIONS
					common_options = self.get_options(options)
					# Make sure common options have a 'data' key
					if not common_options.has_key("data"):
						common_options['data'] = {}
					# Merge the data global options
					if global_options.has_key('data'):
						if isinstance(common_options['data'], dict):
							common_options['data'] = object_merge(common_options['data'], global_options['data'])
						elif data_index < len(common_options["data"]):
							common_options['data'][data_index] = object_merge(common_options['data'][data_index], global_options['data'])
						else:
							raise error("The `data' attribute in the common options does not have enough entries.", self)
					# Merge data options with the common data options (if there is)
					if isinstance(common_options["data"], dict):
						data_options = object_merge(common_options["data"], data_options)
					elif isinstance(common_options["data"], list):
						if data_index >= len(common_options["data"]):
							raise error("The `data' attribute in the common options does not have enough entries.", self)
						data_options = object_merge(common_options["data"][data_index], data_options)
					# Ensure that all required data are present
					for key in ["parser"]:
						if not data_options.has_key(key) or not data_options[key]:
							raise error("This parser is missing its `%s' attribute." % (str(key)), self)
					# build the full options
					seq_options = object_clone(options)
					seq_options['data'] = data_options
					# -----------------------

					# Handles retries
					for retry in range(self.nb_retries):

						# Create the temporary parser
						parser = data_options["parser"]()

						try:
							# Fetch the data and parse them
							data = parser.fetch_data(data_options);

							# Backup data - used for debug
							#write_file("%i_dump_%s_%i" % (index, options["id"], data_index), data)

							#exit()

							# Load the parser data
							result = parser.load(data, seq_options)
							if isinstance(result, bool) and result == False:
								# Ignore this parser
								abort = True
								break

							# Merge the data found into the main parser
							main_parser.merge_data(parser)

						except Exception as e:

							# Display the error message
							error(str(e), self)
							# Retry if allowed
							if self.allow_retry and retry < (self.nb_retries - 1):
								self.info("Retrying %s::%s (#%i)..." % (str(self.__class__.__name__), str(options["display"]), retry + 1), 1)
								continue
							# Ignore this parser if allowed
							elif self.allow_ignore:
								abort = True
								self.info("Ignoring this parser (%s::%s)." % (str(self.__class__.__name__), str(options["display"])), 0)
							# Else display an error
							else:
								raise

						# Update the total page count
						if options.has_key("paging") and options["paging"]:
							page_total = parser.page_total()
							if parser.page_current() != -1 and page_current != parser.page_current():
								# Skip the page
								error("The estimated current page number does not matches the one retrieved (it should be: %i, read: %i), skip this parser." % (page_current, parser.page_current()), self)
								if not self.allow_ignore:
									raise
								page_total = -1
						break

				# Ignore this parser
				if abort:
					break
				# Parse
				main_parser.parse(options)

				# Merge the device lists
				for d in main_parser.get_devices():
					self.add_device_to_list(d)

				# Update the page number
				page_current = page_current + 1

			# Reset the parser log context
			GenericParser.set_log_context("", "", "")

		# Print total number of devices found
		self.info("Found %i device(s)." % (len(self.device_list)), 1)

	@classmethod
	def get_ids(cls):
		"""
		Return the list of IDs
		"""
		return [s['id'] for s in cls.specific_options_list]

	def setup_parser_rules(self, parser):
		"""
		Setup specific rules for the parser
		"""
		pass

class GenericParser(Parser):
	log_context = {}

	def __init__(self):
		self.reset()

	@staticmethod
	def parser_log_hook(message, args):
		(parser, device, param) = GenericParser.get_log_context()
		if parser:
			message = "%s - %s" % (parser, message)
		if device and param:
			return "%s::%s - %s" % (device, param, message)
		elif device:
			return "%s - %s" % (device, message)
		elif param:
			return "%s - %s" % (param, message)
		else:
			return message

	@staticmethod
	def set_log_context(parser = None, device = None, param = None):
		if parser != None:
			GenericParser.log_context["parser"] = parser
		if device != None:
			GenericParser.log_context["device"] = device
		if param != None:
			GenericParser.log_context["param"] = param

	@staticmethod
	def get_log_context():
		return (str(GenericParser.log_context["parser"]), str(GenericParser.log_context["device"]), str(GenericParser.log_context["param"]))

	# Paging functions
	def page_current(self):
		return -1
	def page_total(self):
		raise error("This function must be implemented", self)

	def reset(self):
		"""
		Reset the parser and clear its data
		"""
		super(GenericParser, self).__init__()
		self.categories = []
		self.category_mapping = {}
		self.elements = []
		self.element_index = -1
		# Initialize the log context
		GenericParser.set_log_context(param = "", device = "")
		Log.log_set_hook(GenericParser.parser_log_hook, self)

	def merge_data(self, parser):
		"""
		This function will merge the data from the target parser to the current parser
		"""
		self.categories = merge_lists(self.categories, parser.categories)
		self.category_mapping = object_merge(self.category_mapping, parser.category_mapping)
		self.elements = merge_lists(self.elements, parser.elements)
		self.device_list = merge_lists(self.device_list, parser.device_list)

	def fetch_data(self, options):
		"""
		Fetch the data from any location.
		"""
		data = ""

		# If it needs to be fetched from a file
		if options.has_key("file"):
			self.info("Fetching data from file: `%s'" % (str(options["file"])), 2)
			data = str(read_file(options["file"]))
		# If it needs to be fetched from a string
		elif options.has_key("string"):
			self.info("Fetching data from string: `%s'" % ((str(options["string"])[:75] + '..') if len(str(options["string"])) > 75 else str(options["string"])), 2)
			data = str(options["string"])
		# If the data need to be fetched from a URL
		elif options.has_key("url"):
			proxy = None
			data = ""
			timeout = 10

			# Default headers
			headers = {
				'Accept': '*/*',
				'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
				'Accept-Language': 'en-US,en;q=0.8',
				'Proxy-Connection': 'keep-alive',
				'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.102 Safari/537.36'
			}

			# Handle proxy
			if options.has_key("proxy"):
				proxy = urllib2.ProxyHandler(options["proxy"])
				opener = urllib2.build_opener(proxy)
				urllib2.install_opener(opener)

			data = None
			# Handle POST data
			if options.has_key("post"):
				if isinstance(options['post'], str):
					data = options['post']
				else:
					data = urllib.urlencode(options['post'])
				headers["Content-Type"] = 'application/x-www-form-urlencoded';
				headers["Content-Length"] = len(data);

			# Handle XML data
			elif options.has_key("xml"):
				data = options['xml']
				headers["Content-Type"] = 'application/xml';
				headers["Content-Length"] = len(data);

			# Handle headers
			if options.has_key("headers"):
				headers = object_merge(headers, options['headers'])

			#print str(options["url"])
			#object_print(headers)
			#print data
			#exit()

			# Build the request
			request = urllib2.Request(str(options["url"]), data, headers)

			# Handle timeout in seconds
			if options.has_key("timeout"):
				timeout = options['timeout']
			# Build the request and process
			self.info("Fetching data from url: `%s'" % (str(options["url"])), 2)
			try:
				response = urllib2.urlopen(request, timeout = timeout)
			except urllib2.URLError, e:
				raise error("Error while retreiving the page `%s' (timeout [%is]): %r: %s" % (str(options["url"]), timeout, e, str(e)), self)
			except socket.timeout:
				raise error("Timeout error (%is)" % (timeout), self)
			data = str(response.read())
		# Apply encoding if any
		if options.has_key("encoding"):
			data = data.decode(options["encoding"], 'replace')
		data = unicode(data)
		# At this point, data must be in unicode
		# Character transaltion table for some strange unicode charcaters
		data = unicodedata.normalize('NFKD', data)
		data = data.replace(u"\u2013", u"-")
		# Convert to ascii
		data = data.encode('ascii', 'replace')
		return data

	def map_categories(self, options):
		self.info("Category mapping:", 2)
		for key in self.category_mapping.keys():
			index = self.get_category_index(key)
			if index != -1 and self.category_mapping[key]:
				self.category_set_string(index, self.category_mapping[key])
				self.info("Map: `%s' -> `%s'" % (str(key), str(self.category_get_string(index))), 2)

	def discover_categories(self, options):
		"""
		This function will go through the categories and try to identify
		which category it belongs to.
		"""
		self.info("Discovering categories:", 2)
		for category_obj in get_category_list():
			# Check if this category is allowed
			if options.has_key('ignore_categories_obj') and category_obj in options['ignore_categories_obj']:
				self.info("Ignore category `%s'." % (str(category_obj.to_param())), 2)
				continue
			for index, category in enumerate(self.categories):
				# If this category is ignore from the autodiscovery
				if not category['autodiscover']:
					continue
				# Create an empty category object
				c = category_obj()
				# Set the index to this category, the category number
				c.set_index(index)
				if c.is_match(category['string']) >= 0:
					# Set the category
					self.category_set_class(index, c)
					self.info("Discovered `%s' (%i) -> `%s'" % (category['string'], index, c.to_param()), 2)

	def discover_devices(self, options):
		"""
		This function will generate devices object out of elements
		"""
		# Post processing category hook
		for index, category in enumerate(self.categories):
			for c in category["index"]:
				self.hook_proceed("post_category_discovery", c, options)

		self.info("Discovering devices:", 2)
		for element in self.elements:
			GenericParser.set_log_context(device = "", param = "")
			device = Device()
			for index, string in enumerate(element):
				for c in self.category_from_device_by_index(device, index):
					GenericParser.set_log_context(param = c.to_param())
					# Trace
					if debug_trace_category and debug_trace_match(c.to_param()):
						self.debug("Class <%s>, Category String: '%s', Value: '%s', Index '%s', Regexpr Index '%s'" % (str(c.to_param()), str(self.category_get_string(index)), str(string), str(index), str(c.get_global_config("category_regex_index"))), 0)
					device.add_category(c.to_class(), string, index)
					if c.to_param() == "CategoryDeviceName":
						GenericParser.set_log_context(device = device.get_device_name(strict = False, fullname = True))
			GenericParser.set_log_context(param = "")
			# Merge categories
			device.merge_categories()
			# Post processing
			self.device_post_processing(device, options)
			# Make sure the device has a name
			device_name = device.get_device_name(strict = False, fullname = False)
			if device_name == None:
				self.error("Device found with no name, ignoring this device.", 0)
				# Ignore the device
				continue
			# Add the device to the list
			self.add_device_to_list(device)
			# Print the device name
			self.info("Found device: `%s'" % (str(device_name)), 2)
			# Print the device
			device.print_categories()

		GenericParser.set_log_context(device = "", param = "")
		# Sanity check after the completion of the parsing
		self.sanity_check()
		# Print message
		if len(self.device_list) == 0:
			self.warning("Nothing has been parsed with this parser.", 0)
		else:
			self.info("Discovered %i device(s)." % (len(self.device_list)), 1)

	def parse(self, options = {}):
		# Set the category mapping
		self.map_categories(options)
		# Post-process the data
		self.post_processing(options)
		# Preprocess categories if needed
		for c in get_category_list():
			self.hook_proceed("pre_category_discovery", c, options)
		# Pre parser discovery hook
		self.hook_proceed("pre_discovery", self, options)
		# Discover categories
		self.discover_categories(options)
		# Discover devices
		self.discover_devices(options)

		# Exclude some devices
		new_device_list = []
		for d in self.device_list:
			if options.has_key("device_exclude") and len(options["device_exclude"]):
				# Get the device name
				device_name = d.get_device_name(strict = True, fullname = False)
				# If the device match the exclude list, exclude this device
				m = re.search("(" + "|".join(options["device_exclude"]) + ")", device_name)
				if m:
					self.info("Excluding `%s' as it matches with `%s'." % (device_name, m.group(1)), 1)
					continue
			new_device_list.append(d)
		self.device_list = new_device_list

		# Post parser discovery hook
		self.hook_proceed("post_discovery", self, options)

	def device_post_processing(self, device, options):
		"""
		This function is called to excecute any post processing
		"""
		# Set custom values
		if options.has_key("custom"):
			for category in options["custom"].keys():
				device.add_category(eval(category), options["custom"][category])
				self.info("Adding custom category for device %s::%s `%s'" % (device.get_device_name(strict = False, fullname = False), category, options["custom"][category]), 3)
		# Hook
		self.hook_proceed("post_device_discovery", device, options)

	def category_from_device_by_index(self, device, index):
		"""
		Get the category instance for a specific device at a specific
		element or category index
		"""
		c = []
		if len(self.categories) <= index:
			self.warning("There is no category at this index (%i) for this device. This probably happens because the number of categories does not match the number of element per devices." % (index))
			return None
		for category_class in self.categories[index]['index']:
			c.append(category_class)
		return c

	def category_class_by_index(self, index):
		"""
		Get the category classes from at a specific element or category
		index
		"""
		return self.categories[index]['index']

	def category_mapping_add(self, identifier, text):
		"""
		Make a category identified by `identifier' match with a text
		"""
		self.category_mapping[str(identifier)] = str(text)

	def category_add(self, name):
		"""
		This function will add a new category to the element.
		It returns the index of the category created.
		"""
		category = {
			'string': "",
			'index': [],
			'autodiscover': True
		}
		# Add the empty category
		self.categories.append(category)
		index = len(self.categories) - 1
		# Set the string or class
		if isinstance(name, str):
			self.category_set_string(index, name)
		elif isinstance(name, list):
			for class_name in name:
				self.category_set_class(index, class_name)
		elif issubclass(name, GenericCategory):
			self.category_set_class(index, name)
		else:
			raise error("Unkown argument type, not supported", self)
		# Retuns the index of the category created
		return index

	def format_raw_string(self, string):
		"""
		Format a raw srting coming from the wild
		"""
		# Replace html tags
		string = re.compile("<br>").sub("\n", string)
		# Delete other html tags
		string = re.compile("<[^>]*>").sub("", string)
		# Remove trailing spaces
		string = re.sub(r"(^\s+|\s+$)", "", string)
		return string

	def category_set_string(self, index, string):
		"""
		Set the string of a category
		"""
		self.categories[index]['string'] = self.format_raw_string(string.lower())

	def category_set_class(self, index, category_obj):
		"""
		Set a class for a category
		"""
		if isinstance(category_obj, type) and issubclass(category_obj, GenericCategory):
			# Create an empty category object
			c = category_obj()
		else:
			# Re-use the one passd into argument
			c = category_obj
		# Set the index to this category, the category number
		c.set_index(index)
		# If this category is a not a multi instance, check if it has been assigned somewhere else
		if not c.is_multi_instance():
			for i, category in enumerate(self.categories):
				if i != index:
					for other_c in category["index"]:
						if other_c.to_param() == c.to_param():
							raise error("Only one category of the same type must be found. It matches for: `%s' (%i) and `%s' (%i). Please check the regular expression for `%s'" % (self.categories[index]['string'], index, category['string'], i, c.to_param()), self)
		unique = True
		# Assign the category class and make sure it is not already assigned
		for current_c in self.categories[index]['index']:
			if current_c.to_param() == c.to_param():
				unique = False
		if unique:
			self.categories[index]['index'].append(c)

	def category_get_string(self, index):
		"""
		Return the string of the category
		"""
		return self.categories[index]['string']

	def get_category_index(self, name):
		"""
		Return the category index or -1 if the category does not exists
		"""
		for index, category in enumerate(self.categories):
			if isinstance(name, str):
				if category['string'] == name.lower():
					return index
			elif issubclass(name, GenericCategory):
				for class_instance in category['index']:
					if isinstance(class_instance, name):
						return index
			else:
				raise error("Unkown argument type, not supported", self)
		return -1

	def element_add_value(self, value, category = None):
		"""
		This function adds a new value to a category of an element.
		If no category is specified, it will assign the value to the
		next category.
		"""
		index = -1
		# If a category is specified
		if category:
			# Look for the index of the category
			index = self.get_category_index(str(category))
			# If there is no category, add it
			if index == -1:
				index = self.category_add(category)
		# Insert the element at the given position
		if index == -1:
			# Get the current element
			element = self.element_current()
			element.append(str(value))
		else:
			# Update the maximal size of the current element
			element = self.element_current_update_size(index + 1)
			# Insert the value at the right place
			element[index] = str(value)

	def element_create(self):
		"""
		This function will create a new empty element.
		"""
		self.elements.append([])
		self.element_index = len(self.elements) - 1

	def element_current_index(self):
		"""
		Get the index of the current element.
		"""
		return self.element_index

	def element_current(self):
		"""
		Get the current element.
		"""
		return self.elements[self.element_current_index()]

	def element_select(self, index):
		"""
		Select the element at the specified index
		"""
		if index >= len(self.elements):
			raise error("Noi element exists at this index (%i)." % (index), self)
		self.element_index = index

	def element_current_update_size(self, size):
		"""
		Update the maximum size of the current element and return the
		current element.
		"""
		index = self.element_current_index()
		element = self.element_current()
		self.elements[index] = element + [''] * (size - len(element))
		return self.element_current()

	def element_print(self, print_elements = True, print_categories = True):
		"""
		Print the element table.
		"""

		if print_categories:
			data = ""
			for index, category in enumerate(self.categories):
				if len(category['index']):
					category_string = ""
					for c in category['index']:
						if category_string:
							category_string = category_string + " "
						category_string = category_string + c.to_param()
				else:
					category_string = category['string']
				data = data + "[" + category_string + " (" + str(index) + ")]\t"

			print data + "\n"

		if print_elements:
			for element in self.elements:
				data = ""
				for value in element:
					data = data + value + "\t|"
				print data + "\n"

	def select_categories(self, identifier_list):
		"""
		Helper function to select categories
		"""
		# If identifier is not a list, make it as a lit
		if not isinstance(identifier_list, list):
			identifier_list = [identifier_list]

		# Loop through the identifiers
		index_list = []
		for i, identifier in enumerate(identifier_list):
			# Identify the index of the category(ies) to be removed
			if isinstance(identifier, str):
				for j, category in enumerate(self.categories):
					if re.search(identifier.lower(), category['string']):
						index_list.append(j)
			elif isinstance(identifier, int):
				if len(self.categories) <= identifier:
					self.warning("Impossible to select the category #%i, index out-of-bound (there are only %i categorie(s))." % (identifier, len(self.categories)))
					continue
				index_list.append(identifier)
			else:
				raise error("Cannot use the identifer `%s' to determine the index of the category to be removed" % (str(identifier)), self)
		# Remove duplicates and keep the list order
		new_index_list = []
		for v in index_list:
			if v not in new_index_list:
				new_index_list.append(v)
		return new_index_list

	def ignore_categories(self, identifier_list):
		"""
		This function will ignore a category from the auto discovery.
		identifier can be a number or a string.
		"""
		index_list = self.select_categories(identifier_list)
		# Remove the categories
		index_list = sorted(index_list, key = int, reverse = True)
		for index in index_list:
			self.categories[index]['autodiscover'] = False
			self.info("Ignoring category `%s' (%s) (%i) from auto-discovery." % (str(self.categories[index]['string']), str(self.categories[index]['index']), index), 2)

	def remove_categories(self, identifier_list):
		"""
		This function will remove a category from raw and update
		the element accordingly.
		identifier can be a number or a string.
		"""
		index_list = self.select_categories(identifier_list)
		# Remove the categories
		index_list = sorted(index_list, key = int, reverse = True)
		for index in index_list:
			self.categories.pop(index)
			for i, element in enumerate(self.elements):
				element.pop(index)
		self.info("Removed %i categorie(s) at index(es) %s." % (len(index_list), str(index_list)), 2)

	def remove_devices(self, identifier_list):
		"""
		An identifier can either be an index or a list containing the index of the category and the value to match.
		"""
		index_list = []
		for i, identifier in enumerate(identifier_list):
			# element index
			if isinstance(identifier, int):
				if len(self.elements) <= identifier:
					raise error("The index is out-of-bound", self)
				index_list.append(identifier)
			# [category index, regexpr]
			elif isinstance(identifier, list):
				# Get identifier data
				category_index = identifier[0]
				value_regexpr = identifier[1]
				if len(identifier) != 2 or not isinstance(category_index, int) or not isinstance(value_regexpr, str):
					raise error("The list identifier has a wrong format", self)
				if len(self.categories) <= identifier[0]:
					raise error("The index is out-of-bound", self)
				for j, element in enumerate(self.elements):
					if re.search(value_regexpr, element[category_index]):
						index_list.append(j)
			else:
				raise error("Cannot use this identifer to determine the index of the device to be removed", self)

		# Remove the devices
		index_list = list(set(index_list))
		index_list = sorted(index_list, key = int, reverse = True)
		for index in index_list:
			self.elements.pop(index)
		self.info("Removed %i element(s)." % (len(index_list)), 2)

	def merge_categories(self, merging_rules):
		"""
		Merge multiple categories together.
		"""
		# Loop through the different merging rules
		for merging_rule in merging_rules:
			if not merging_rule.has_key("category_selector"):
				raise error("This merging rule is missing the `category_selector' attribute.", self)
			# Get the category list
			index_list = self.select_categories(merging_rule['category_selector'])

			# If less than 2 categories have been identified, skip
			if len(index_list) < 2:
				continue

			# The target category will be the one replaced by the merged value
			# The other categories will be removed
			target_index = index_list[0]
			index_list = index_list[1:]

			# List all devices
			for i, element in enumerate(self.elements):
				value = element[target_index]
				for index in index_list:
					if merging_rule.has_key("merge_options"):
						value = merge_strings(value, element[index], MERGE_CONCATENATE | MERGE_MULTILINE | MERGE_KEEP_ORDER, merging_rule["merge_options"])
					else:
						value = merge_strings(value, element[index], MERGE_CONCATENATE | MERGE_MULTILINE | MERGE_KEEP_ORDER)
				element[target_index] = value

			# Remove the other categories
			index_list = sorted(index_list, key = int, reverse = True)
			for index in index_list:
				self.categories.pop(index)
				for i, element in enumerate(self.elements):
					element.pop(index)

			# Reselect the target_index since it might have changed becasue of the deletion
			target_index = self.select_categories([merging_rule['category_selector'][0]])
			if len(target_index) != 1:
				continue
			target_index = target_index[0]

			# Rename the merged category
			if merging_rule.has_key("category_name"):
				self.category_set_string(target_index, merging_rule['category_name'])
			if len(index_list):
				self.info("Merged categorie(s) %s." % (str(merging_rule['category_selector'])), 2)

	def assign_categories(self, mapping_list):
		# List each mapping instruction
		for mapping in mapping_list:
			if len(mapping) != 2:
				raise error("The mapping entry should have 2 entities.", self)
			# Get the category list
			index_list = self.select_categories(mapping[0])
			# Select the categories and assign the new text
			for index in index_list:
				if isinstance(mapping[1], str):
					self.category_set_string(index, mapping[1])
					self.info("Category Map: (%i) -> `%s'" % (index, str(mapping[1])), 2)
				else:
					self.category_set_class(index, mapping[1])
					self.info("Category Map: (%i) -> `%s'" % (index, mapping[1].to_param()), 2)

	def post_processing(self, config = {}):
		"""
		`config' handles the following values
			ignore_categories: Skip certain categories from the auto discovery.
			                   It can be an index: (0 to ...) or string
			                   matching the name of the category.
			remove_categories: Remove certain categories from the raw data.
			                   It can be an index: (0 to ...) or string
			                   matching the name of the category.
			ignore_devices: Skip certain devices from the raw data.
			                It can be an index: (0 to ...) or a list containing
					the index of the category and a string which matches
			                the category value for the device to be ignored.
			merge_categories: Merge multiple categories together.
					  It must be a table which contains the merge rules.
					  Each merging rule is an object with the following attributes:
					  'category_selector': the category selector. The categories will be merged
					  in the same order has the list is set (mandatory).
					  'category_name': the name of the category, if none is set, it will keep the
					  name of the 1rst category specified in the category selector (optional).
					  'merge_options': the merging options (optional).
			map_categories: Manually map some categories with a specific
					parameter.
					Each mapping is an object with the following attributes:
					'category_selector': the category selector. The categories will be merged
					in the same order has the list is set (mandatory).
					'text': The replacement text
					Structure: [[selector, text/class], ...]
		"""
		# Remove empty elements from the list
		self.elements = filter(len, self.elements)
		if config.has_key("ignore_devices"):
			self.remove_devices(config["ignore_devices"])
		if config.has_key("ignore_categories"):
			self.ignore_categories(config["ignore_categories"])
		if config.has_key("remove_categories"):
			self.remove_categories(config["remove_categories"])
		if config.has_key("merge_categories"):
			self.merge_categories(config["merge_categories"])
		if config.has_key("map_categories"):
			self.assign_categories(config["map_categories"])

	def sanity_check(self):
		"""
		This function must be called after the parsing is done
		It will check several rules:
		1. Make sure each devices have a name
		"""
		# Go through all the new elements
		for device in self.get_devices():
			# Get the name of the device, raise an error if not present
			device_name = device.get_device_name(strict = True, fullname = True)

	# Default page numbers, this should be overwritten
	def page_current(self):
		return 0
	def page_total(self):
		return 1
