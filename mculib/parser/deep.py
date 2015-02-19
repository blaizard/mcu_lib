#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from generic import *
from mculib.helper import *
from bs4 import BeautifulSoup
import json

class DeepParser(GenericParser):

	options = {}

	def category_mapping_action(self, data, key, level):
		# By default, if we reach the last tag level, this is the parameters
		(name, string) = self.get_category_mapping(data, key)
		self.category_mapping_add(name, string)

	def get_category_mapping(self, param, key):
		"""
		Map the name (or ID) of the category with its text.
		"""
		category = ""
		text = ""
		if self.options.has_key("param_category_tag"):
			category = param[self.options["param_category_tag"]]
		if self.options.has_key("param_category_text_tag"):
			text = param[self.options["param_category_text_tag"]]
		return (category, text)

	def format_value(self, data):
		if isinstance(data, (str, unicode)):
			return data.encode('ascii', 'replace')
		elif isinstance(data, (int, long, float, complex)):
			return str(data)
		elif isinstance(data, list) or isinstance(data, dict):
			value_list = []
			for d in data:
				value_list.append(self.format_value(d))
			return ", ".join(value_list)
		else:
			raise error("Unhandled value type: `%s'." % (str(data)), self)

	def get_value(self, param, key, options, options_preffix_key):
		"""
		This function will read out a parameter value
		"""
		param_tag = options_preffix_key + "_tag"
		param_optional_tag = options_preffix_key + "_optional_tag"
		param_attr = options_preffix_key + "_attr"

		nb_multi = 1
		if options.has_key(param_tag) and isinstance(options[param_tag], list) and len(options[param_tag]) and isinstance(options[param_tag][0], list):
			nb_multi = len(options[param_tag])

		# Helper function
		def read_options(options, key, is_multi, index, required, default = None):
			if required and not options.has_key(key):
				raise error("This parser is missing the attribute `%s'." % (key), self)
			o = default
			if options.has_key(key):
				o = options[key]
				if is_multi:
					o = o[index]
			return o

		value = None
		for index in range(nb_multi):

			# Read the parameters
			tag = read_options(options, param_tag, nb_multi > 1, index, False, None)
			optional_tag = read_options(options, param_optional_tag, nb_multi > 1, index, False, None)
			attr = read_options(options, param_attr, nb_multi > 1, index, True)

			# If we need to dig into the architecture
			# Identify the tags
			param_list = [ param ]
			if tag:
				param_list = self.parse_deep_architecture(param, tag)
				if len(param_list) == 0:
					if index == 0:
						raise error("One or more tags should be found with `%s', 0 found instead." % (param_tag), self)
					continue

			# Look for optional digging rules
			if optional_tag:
				for index, param in enumerate(param_list):
					temp_param = self.parse_deep_architecture(param, optional_tag)
					if len(temp_param) == 1:
						param_list[index] = temp_param[0]

			sub_value = None
			# Loop through the parameter list
			for p in param_list:
				tmp_value = None
				if isinstance(attr, bool) and attr:
					tmp_value = self.format_value(key)
				elif isinstance(attr, bool) and not attr:
					tmp_value = self.format_value(p)
				elif attr:
					if p.has_key(attr):
						tmp_value = self.format_value(p[attr])
				else:
					tmp_value = self.format_value(p.get_text())

				# Make sure this is the only valid value found
				if tmp_value != None:
					if sub_value != None:
						raise error("Only 1 value should be found for this attribute (%s), found: `%s', `%s'." % (str(attr), str(sub_value), str(tmp_value)), self)
					sub_value = str(tmp_value)

			if sub_value != None:
				if value:
					value = value + " " + sub_value
				else:
					value = sub_value

		# If no value has been found, raise an error
		if value == None:
			o_error = []
			for key in options.keys():
				if key.find(options_preffix_key) == 0:
					o_error.append("%s: `%s'" % (key, str(options[key])))
			raise error("No value has been identified for this attribute (%s) while parsing `%s'." % (", ".join(o_error), str(param)), self)

		return str(value)

	def get_category(self, param, key):
		"""
		Read the categories information (id and value) for a device.
		"""
		if not self.options.has_key("category_param"):
			raise error("This parser is missing the attribute `category_param'.", self)
		category_param = self.options['category_param']

		# Get the data out of the tree
		category_id = self.get_value(param, key, category_param, "id")
		category_value = self.get_value(param, key, category_param, "value")

		# Hack
		category_value = re.sub(r'\[\/?pf\]', "", category_value)
		category_value = re.sub(r'\^', "\n", category_value)

		self.info("Adding device entry `%s' -> `%s'." % (str(category_id), str(category_value)), 3)

		return (category_id, category_value)

	def category_tag_action(self, data, key, level):
		# Found a category, retriees its ID and its value
		(category, value) = self.get_category(data, key)
		if not category:
			raise error("The category of this parameter cannot be identified (`%s', `%s')." % (str(category), str(value)), self)
		self.element_add_value(str(value), str(category))

	def device_tag_action(self, data, key, level):
		# This is a potential device, create an entry
		self.element_create()
		# Populate the categories
		if not self.options.has_key("category_tag"):
			raise error("This parser is missing the `%s' option." % ('category_tag'), self)
		self.parse_deep_architecture(data, self.options["category_tag"], self.category_tag_action)

	def get_category_mapping(self, param, key):
		"""
		Read the category mapping information (id and text).
		"""
		if not self.options.has_key("category_map_param"):
			raise error("This parser is missing the attribute `category_map_param'.", self)
		category_map_param = self.options['category_map_param']

		# Get the data out of the tree
		category_map_id = self.get_value(param, key, category_map_param, "id")
		category_map_value = self.get_value(param, key, category_map_param, "value")

		self.info("Adding mapping entry `%s' -> `%s'." % (str(category_map_id), str(category_map_value)))

		return (category_map_id, category_map_value)

	def parse_deep_architecture(self, data, tag_key, tag_action, level = 0):
		pass

	def parse_deep(self, data):
		# Look for the devices
		if self.options.has_key("device_tag"):
			self.parse_deep_architecture(data, self.options["device_tag"], self.device_tag_action)

		# Look for the category mapping tags
		if self.options.has_key("category_map_tag"):
			self.parse_deep_architecture(data, self.options["category_map_tag"], self.category_mapping_action)

	def load(self, data, options = {}):
		pass

class XMLParser(DeepParser):
	"""
	Options:
		For the following to make it more clear, we will use the following example:
		Example 1:
			<Product>
				<param name="device1">
					<category name="000001">Blaise</category>
				</param>
				...
			</Product>
			<category_mapping>
				<map id="000001">
					<param text="Product Name" />
					<param info="No non no" />
				</map>
				...
			</category>
		'device_tag': A list of tags that relates to the devices.
			In example 1, the following will match the device(s): ["Product", "param"].
		'category_tag': A list containing the tags that relates to the device categories.
			In example 1, the string would be: ["category"].
		'category_param': An object describing the category architecture:
			{
				'id_tag': [],  // The tags leading to the category ID (can be empty)
				'id_optional_tag': [], // The optional tags leading to the category ID (can be empty)
				'id_attr': "", // The attribute containing the category ID. If None is specified, the category ID will be the value of the tag.
				'value_tag': [[]],
				'value_optional_tag': [[]],
				'value_attr': [""],
			}
			In example 1, the object would be:
			{
				'id_tag': [],
				'id_attr': "name",
				'value_tag': [],
				'value_attr': None,
			}
		'category_map_tag': A list of tags that relates to the category mapping tags.
			In example 1, the following will match the device(s): ["category_mapping", "map"].
		'category_map_param': An object describing the category mapping architecture (same as 'category_param'):
			In example 1, the object would be:
			{
				'id_tag': [],
				'id_attr': "id",
				'value_tag': ["param"],
				'value_attr': "text",
			}
	"""

	def parse_deep_architecture(self, data, tag_list, tag_action = None, level = 0):
		"""
		Parsea XML architecture and return the tag list found (the one at the deepest level).
		If a tag_action callback is defined, call it once an element has been identified.
		"""
		# Special case, when the tag_list is empty, return directly the data
		if len(tag_list) == 0:
			return [ data ]
		if len(tag_list) <= level:
			raise error("The `%s' option must contain at least %i element." % (str(tag_list), level + 1), self)

		return_data_list = []

		# Fetching data
		data_list = data.find_all(tag_list[level].lower())
		self.info("Found %i entries for `%s' (level %i/%i)" % (len(data_list), tag_list[level], level, len(tag_list)), 3)
		for index, d in enumerate(data_list):
			# If it did not reach the lower level, continue the iteration
			if len(tag_list) > level + 1:
				return_data_list.extend(self.parse_deep_architecture(d, tag_list, tag_action, level + 1))
			elif tag_action != None:
				tag_action(d, index, level)

		# Return the list of the data found
		if level == len(tag_list) - 1:
			return data_list
		return return_data_list

	def load(self, data, options = {}):
		if options.has_key('data'):
			self.options = options['data']
		soup = BeautifulSoup(data)
		self.parse_deep(soup)

class JSONParser(DeepParser):

	"""
	Options:
		For the following to make it more clear, we will use the following example:
		Example 1:
			{
				'products':
					[
						{ '000001' : "Blaise", '0778' : "yes", ... },
						...
					],
				'category_mapping':
					{
						'000001': { 'name': "Product Name" },
						'0778': { 'name': "RTC" },
						...
					}
			}
		'device_tag': A list of tags that relates to the devices.
			In example 1, the following will match the device(s): ["products"].
		'category_tag': A list containing the tags that relates to the device categories (from a device).
			In example 1, the string would be: [].
		'category_param': An object describing a category architecture:
			{
				'id_tag': [],  // The tags leading to the category ID (can be empty)
				'id_optional_tag': [], // The optional tags leading to the category ID (can be empty)
				'id_attr': "", // True if the value is the key, False otherwise.
				'value_tag': [],
				'value_optional_tag': [],
				'value_attr': "",
			}
			In example 1, the object would be:
			{
				'id_tag': [],
				'id_attr': True,
				'value_tag': [],
				'value_attr': False,
			}
		'category_map_tag': A list of tags that relates to the category mapping tags.
			In example 1, the following will match the device(s): ["category_mapping"].
		'category_map_param': An object describing the category mapping architecture (same as 'category_param'):
			In example 1, the object would be:
			{
				'id_tag': [],
				'id_attr': True,
				'value_tag': ["name"],
				'value_attr': False,
			}
	"""

	def parse_deep_architecture(self, data, tag_list, tag_action = None, level = 0):
		"""
		Parse a XML architecture and return the tag list found (the one at the deepest level).
		If a tag_action callback is defined, call it once an element has been identified.
		"""
		if len(tag_list) == level:
			if tag_action != None:
				tag_action(data, None, 0)
			return data

		return_data_list = []

		# Fetching data
		# If the data is a list
		if isinstance(data, list) or (isinstance(data, dict) and not tag_list[level]):

			if is_number(tag_list[level]):
				index_list = [ to_number(tag_list[level]) ]
			elif not tag_list[level]:
				if isinstance(data, list):
					index_list = range(len(data))
				else:
					index_list = data.keys()
			else:
				raise error("Unable to identify the list identifier `%s'." % (str(tag_list[level])), self)

			self.info("Found %i entries for the list identified by `%s' (level %i/%i)" % (len(index_list), tag_list[level], level, len(tag_list)), 3)
			data_list = [ data[index] for index in index_list ]

			for index in index_list:
				d = data[index]
				# If it did not reach the lower level, continue the iteration
				if len(tag_list) > level + 1:
					return_data_list.extend(self.parse_deep_architecture(d, tag_list, tag_action, level + 1))
				elif tag_action != None:
					tag_action(d, str(index), level)

		# If the data is a dict
		elif isinstance(data, dict):
			if data.has_key(tag_list[level]):
				self.info("Found 1 entry for `%s' (level %i/%i)" % (tag_list[level], level, len(tag_list)), 3)
				data_list = [ data[tag_list[level]] ]
				# If it did not reach the lower level, continue the iteration
				if len(tag_list) > level + 1:
					return_data_list.extend(self.parse_deep_architecture(data_list[0], tag_list, tag_action, level + 1))
				elif tag_action != None:
					tag_action(data_list[0], str(tag_list[level]), level)
			else:
				data_list = []

		# Return the list of the data found
		if level == len(tag_list) - 1:
			return data_list
		return return_data_list

	def load(self, data, options = {}):
		if options.has_key('data'):
			self.options = options['data']
		json_data = json.loads(data)
		self.parse_deep(json_data)

