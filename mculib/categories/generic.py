#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import re
import unicodedata
from mculib import *
from mculib.helper import *
from mculib.log import *
from mculib.config import *

def category_is_group(category):
	# Convert the category to a class
	category = object_to_class(category)
	return category.is_group()

def category_is_list(category):
	# Convert the category to a class
	category = object_to_class(category)
	return category.is_list()

def category_is_multi(category):
	# Convert the category to a class
	category = object_to_class(category)
	return category.is_multi()

def category_is_normal(category):
	# Convert the category to a class
	category = object_to_class(category)
	return not category.is_multi() and not category.is_list()

def category_is_multilist(category):
	# Convert the category to a class
	category = object_to_class(category)
	return category.is_multi() and category.is_list()

class GenericCategory(MCULibClass):

	# Constants
	ERROR = -1
	PASS = 1
	WARNING = 0

	# Type constants
	TYPE_ANY = 0 # data, 0, yes, -5.2, ...
	TYPE_INTEGER = 1 # -2, -1, 0, 1, yes, ...
	TYPE_DECIMAL = 2 # -1.05, 0.45, 10 ...
	TYPE_BINARY = 3 # yes, 0
	TYPE_STRING = 4 # data, hello, ...
	TYPE_DATE = 5 # [DD-][MM-]YYYY
	TYPE_URL = 6 # http://xxxx
	TYPE_MASK = 7 # Mask to retrieve the data type
	TYPE_EXT_POSITIVE = 8
	TYPE_EXT_NEGATIVE = 16
	TYPE_EXT_NOT_NULL = 32
	TYPE_EXT_BINARY = 64

	# The category regular expression that matches
	category_regex_index = -1
	# List of extra category regular expression, mostly used for hooks
	extra_category_regexpr = []
	# Give the pattern of a string, by default everything is usefull
	string_pattern = "^(.*)$"
	# Number of deciaml after the coma
	config_resolution = 0
	# A ratio to be multiplied by the result
	config_convert_ratio = 1
	# Will expand the k, m, M, ... units to a integer
	config_expand_units = False
	# Defines if multiple instances are allowed for this category
	config_multiple_categories = False
	# Default options for the merge
	config_merge_options = {}
	# When 2 values have to be merge, define the strategy. It can be "add", "max", "min"
	config_merge_strategy = MERGE_STRATEGY_REPLACE
	# When merging with the previously stored value
	config_merge_with_original_strategy = MERGE_STRATEGY_REPLACE
	# When merging with a higher trustability value
	config_merge_trust_strategy = MERGE_STRATEGY_FILL
	# Merge the alias with the MCU
	config_alias_merge_with_mcu = True
	# Delete the alias parameter if the MCu already has this value
	config_alias_delete_if_duplicate = True
	# Defines if a category is common with other devices. If common, its value will contain the
	# id with which category it is common
	config_group = None
	config_group_master = False
	# This option defines the relative path of the group, i.e. where the group file will be stored
	config_group_path = "common/"
	# Ignore the '-' character
	config_ignore_minus_char = False
	# Ignore the empty cells
	config_ignore_empty = True
	# This flag is used to set a lower trustability to the value when the minus char or empty cell is taken into account
	config_reduced_trustability = False
	# This value is replaced if a value is not null
	config_fixed_value = None
	# Table used to translate a value if it matches a regular expression
	config_translation_table = []
	# This option prevent the database to log the record. This can be used to avoid pollution on the output.
	config_silent = False
	# This option will force the database to always update the value, even if the previous one was identical.
	# This can be used to force the time to be updated.
	config_always_update = False
	# By default the category values are case insensitive
	config_case_sensitive = False

	def __init__(self, index = -1):
		self.value = self.get_default_value()
		self.index = index
		# Set the initial value of the category_regexpr_index if not set already
		if self.category_regex_index == -1:
			if isinstance(self.get_category_regexpr(), list):
				self.category_regex_index = len(self.get_category_regexpr()) - 1
			else:
				self.category_regex_index = 0
		# Generate the zero match list
		self.zero_match_list = ['no', 'none', 'empty', 'void', 'null', 'false', '0', 'n/a', 'n']
		if not self.config_ignore_minus_char:
			self.zero_match_list.append('-')
		if not self.config_ignore_empty:
			self.zero_match_list.append('')

	def trace(self, string):
		"""
		This function prints the message (string) only for the category traced
		"""
		if debug_trace_category and debug_trace_match(self.to_param()):
			self.debug(str(string), 0)

	def set_index(self, index):
		"""
		Set the index of the category
		"""
		self.index = index

	def set_global_config(self, name, value):
		"""
		Set an attribute to the class
		"""
		if self.index != -1:
			name = name + str(self.index)
		setattr(self.__class__, name, value)

	def get_global_config(self, name):
		"""
		Return an attribute from the class
		"""
		if self.index != -1:
			try:
				return getattr(self, name + str(self.index))
			except AttributeError:
				pass
		return getattr(self, name, "")

	def is_sub_category(self):
		"""
		Check if this category is a sub_category
		"""
		return False

	@classmethod
	def is_list(cls):
		"""
		Tell if this category is a list
		"""
		return False

	@classmethod
	def is_multi(cls):
		"""
		Tell if this category is a multi-value category
		"""
		return False

	def is_multi_instance(self):
		"""
		Returns True if this category allows multiple instance, False otherwise.
		"""
		return self.config_multiple_categories

	def to_param(self):
		return self.__class__.__name__

	@classmethod
	def to_param(cls):
		return cls.__name__

	def to_class(self):
		return self.__class__

	@classmethod
	def to_class(cls):
		return cls

	@classmethod
	def is_group(cls):
		return (cls.config_group_master == True)

	@classmethod
	def is_group_item(cls):
		return (cls.config_group != None)

	@classmethod
	def get_group_param(cls):
		if cls.config_group:
			return cls.config_group.to_param()
		if cls.config_group_master == True:
			return cls.to_param()
		return None

	@classmethod
	def get_default_value(cls):
		return ""

	def get_value(self):
		return self.value

	def set_value(self, value):
		"""
		Set the value of this category
		"""
		value = self.format_value(value)
		self.info("Value Discovered: %s" % (str(value)), 3)
		if value and self.sanity_check_internal(value):
			self.value = value

	def set_list_value(self, value):
		"""
		Set the value of a list.
		The value must be a list containing string arguments.
		"""
		if not isinstance(value, list):
			raise error("value is not a list.")
		# Generate and format the value list
		temp_value_list = []
		for sub_value in value:
			new_value = self.format_value(sub_value)
			# If the value is empty, discard it
			if isinstance(new_value, str) and new_value == "":
				continue
			elif isinstance(new_value, list):
				discard = True
				for n in new_value:
					if n != "":
						discard = False
				if discard:
					continue
			temp_value_list = merge_lists(temp_value_list, [new_value])
		value_list = []
		for sub_value in temp_value_list:
			if sub_value and self.sanity_check_internal(sub_value, temp_value_list):
				value_list.append(sub_value)
		# Store the value
		self.value = value_list

	def parse_list_format(self, string, regexpr_list, separator_list = ['\n', ';', '|', '+', ',', ' ']):

		"""
		Cut the string into pieces with the different possible separators and keep the one
		that returns the more result.
		"""

		# Results
		value_list = []
		string_list = []

		# Loop through all possible separators
		for i, separator in enumerate(separator_list):

			# To store the values
			value_list.append([])
			string_left_over = []

			# Cut the string into pieces
			for string_item in string.split(separator):

				# Read values for each pieces of string
				value = self.parse_format(string_item, regexpr_list)

				# Store the value if any
				if len(value) > 0:
					value_list[i] = merge_lists(value_list[i], value)
				else:
					string_left_over.append(string_item)

			# Build the string of left overs
			string_list.append(separator.join(string_left_over))

		# When it is done, loop for the row with the most items
		value = []
		for i, v in enumerate(value_list):
			if len(value) < len(v):
				value = value_list[i]
				string = string_list[i]

		return (value, string)

	def parse_list(self, string, regexpr_list, separator_list = ['\n', ';', '|', '+', ',']):
		"""
		This function will parse a list and run a regular expression on each item of this list.
		It will return the matched elements and the rest of the string where no elements has been found.

		force_parse_format This varaible will force the use of force_parse_format even if the argument is a list
		"""

		for separator in separator_list:

			# Clear all the previous information
			next_separator = False
			value_list = []

			# This list will contain the strings that have not been parsed
			strings_not_parsed = []

			# Cut the string into pieces
			for string_item in string.split(separator):

				# Look for values
				value_item = []
				value_found = False
				for regexpr in regexpr_list:
					value = ""
					# Update the Current
					if isinstance(regexpr, str):
						values = self.parse_format(string_item, regexpr)
					elif isinstance(regexpr, list):
						values = [[self.parse_translation_table(string_item, regexpr)]]
					else:
						raise error("Unknown argument type (%s) for parse_list." % (str(regexpr)), self)
					# If more than 1 result has been found, it means that this is not a proper separator
					if len(values) > 1:
						next_separator = True
						break
					# If one result has been found, store it
					if len(values) == 1 and len(values[0]) == 1:
						value_found = True
						value = values[0][0]
					value_item.append(value)

				# If no value has been found for this sub-string, add it to the list
				if value_found == False:
					strings_not_parsed.append(string_item)

				# Get the next separator
				if next_separator:
					break

				# Or update the value
				if value_found:
					value_list.append(value_item)

			# Get the next separator
			if not next_separator:
				break

		return (value_list, separator.join(strings_not_parsed))

	def get_category_regexpr(self):
		"""
		This function should return the category regular expression.
		"""
		return None

	def get_category_regexpr_exclude(self):
		"""
		This function should return the category regular expression for excluded patterns.
		All the patterns will be tested, and an a match, the category will be ignored.
		"""
		return None

	def get_fixed_value_regexpr(self):
		"""
		This function return a regular format expression that will parse the category
		string to find the fixed value (if any).
		Note that this is done during the category discovey, therefore, the string will
		be in lower case. this must be considered for the unit.
		"""
		return None

	@classmethod
	def set_fixed_value(cls, value):
		cls.config_fixed_value = value

	@classmethod
	def get_type(cls):
		"""
		Defines the type of data expected, must be a list to handle multi-value data.
		The values are either a constant TYPE_* or a category class
		"""
		if len(cls.config_translation_table):
			new_list = []
			for element in cls.config_translation_table:
				if element[1] not in new_list:
					new_list.append(element[1])
			return [new_list]
		return [cls.TYPE_ANY]

	"""
	This function is mainly used for hooks to add a regular expression to match a category
	"""
	def add_category_regexpr(self, regexpr):
		if not isinstance(regexpr, list):
			regepxr = [regexpr]
		self.extra_category_regexpr = merge_lists(self.extra_category_regexpr, regexpr)

	@classmethod
	def add_category_regexpr(cls, regexpr):
		if not isinstance(regexpr, list):
			regepxr = [regexpr]
		cls.extra_category_regexpr = merge_lists(cls.extra_category_regexpr, regexpr)

	@classmethod
	def add_translation_table(cls, translation_table):
		"""
		This function will add element at the beginning of the translation table
		"""
		cls.config_translation_table = translation_table + cls.config_translation_table

	def is_match(self, string, regexpr_start_index = 0):
		"""
		This function tests if a category matches a category name.
		It will also update the ratio.
		start_index is the category rexpr starting index.
		"""
		regexpr_start_index = self.is_category_match(string.lower(), regexpr_start_index)

		# If the category matched
		if regexpr_start_index >= 0:

			# Check if this is a sub-value, in that case, detect its position and pattern
			# A sub-value is something like this: I/Os (AC|PWM)
			p = re.compile("\([^\)]*\)")
			# If the category still matches the stripped string, it means that it is not a sub-value, skip the rest
			if self.is_category_match(p.sub("", string), regexpr_start_index - 1) == -1:
				pattern = ""
				is_sub_match = False
				for m in re.findall(p, string):
					pattern += ".*\("
					# Separate the string with separators
					s = re.search(r"[|\/\\,;]", m)
					value = [m]
					if s:
						s = str(s.group(0))
						value = m.split(s)
					for index, sub_category in enumerate(value):
						if index and s:
							pattern += s
						# Check which sub-category matches the category
						if self.is_category_match(sub_category, regexpr_start_index - 1) >= 0:
							pattern += "(.*)"
							if is_sub_match:
								raise error("2 sub-matches in the same category is not supported!", self)
							is_sub_match = True
						else:
							pattern += ".*"
					pattern += "\).*"
				# If there is a sub-match, save the pattern
				if is_sub_match:
					self.set_global_config("string_pattern", "^" + pattern + "$")

			# Identify the unit if any
			if re.search(r"\b(b|byte|bytes)\b", string):
				self.set_global_config('config_convert_ratio', 1)
			elif re.search(r"\b(kb|kbyte|kbytes)\b", string):
				self.set_global_config('config_convert_ratio', 1024)
			elif re.search(r"\b(kw|kword|kwords)\b", string):
				self.set_global_config('config_convert_ratio', 2048)
			elif re.search(r"\b(mb|mbyte|mbytes)\b", string):
				self.set_global_config('config_convert_ratio', 1024 * 1024)
			elif re.search(r"\b(khz|ksps|kbps)\b", string):
				self.set_global_config('config_convert_ratio', 1000)
			elif re.search(r"\b(mhz|msps|mbps)\b", string):
				self.set_global_config('config_convert_ratio', 1000 * 1000)

			# Identify the fixed value if any.
			if self.get_fixed_value_regexpr():
				values = self.parse_format(string, self.get_fixed_value_regexpr())
				if len(values) and len(values[0]):
					if self.is_multi():
						self.info("Found a fixed value: `%s'" % (str(values[0])))
						self.set_global_config('config_fixed_value', self.format_value(values[0]))
					else:
						self.info("Found a fixed value: `%s'" % (str(values[0][0])))
						self.set_global_config('config_fixed_value', self.format_value(values[0][0]))

		return regexpr_start_index

	def is_category_match(self, string, start_index = 0):
		"""
		Parses the string to determine if the category is a match or not.
		Returns a number greater or equal to 0 if the category is a match, -1 otherwise.
		If a number greater than 0 is returned, corresponds to the start_index value of
		the next call for the same category, this to detect mutliple instance of the same category.
		Note, the string passed in argument is in lower case.
		start_index This is the index from which the regular expression is looked for
		"""
		# Exclude the categories
		if isinstance(self.get_category_regexpr_exclude(), str):
			if re.search(self.get_category_regexpr_exclude(), string, flags=re.IGNORECASE|re.DOTALL):
				return -1
		elif isinstance(self.get_category_regexpr_exclude(), list):
			for regex in self.get_category_regexpr_exclude():
				if re.search(regex, string, flags=re.IGNORECASE|re.DOTALL):
					return -1

		# Test the regular expression
		if isinstance(self.get_category_regexpr(), str):
			if re.match(self.get_category_regexpr(), string, flags=re.IGNORECASE|re.DOTALL):
				return 0
		elif isinstance(self.get_category_regexpr(), list):
			c = self.get_category_regexpr()
			for index in range(start_index, len(c)):
				regex = c[index]
				if re.match(regex, string, flags=re.IGNORECASE|re.DOTALL):
					self.set_global_config("category_regex_index", index)
					return index + 1

		# Handles extra regular expression
		if len(self.extra_category_regexpr):
			for regex in self.extra_category_regexpr:
				if re.match(regex, string, flags=re.IGNORECASE|re.DOTALL):
					return 0

		return -1

	def sanity_check(self, value, complete_list_value = []):
		"""
		Check the value, make sure the value is not to high or too low.
		"""
		return GenericCategory.PASS

	def sanity_check_internal(self, value, complete_list_value = []):

		# Sanity check according to the type
		check_value = value
		if not isinstance(value, list):
			check_value = [value]
		# Get the value type
		value_type = self.get_type()
		# Format everything as a list and loop through
		for i, v in enumerate(check_value):
			# If the value is not defined, skip
			if v == "":
				continue
			type_pass = False
			v_type = value_type[i]

			if isinstance(v_type, list):
				if v in v_type:
					type_pass = True

			elif isinstance(v_type, str):
				l_check = v_type.split("/")
				l_v = v.split("/")
				# Make sure that all the values from l_v are contained into l_check
				type_pass = True
				# Loop through the values
				for v_to_check in l_v:
					if v_to_check not in l_check:
						type_pass = False
						break

			else:
				# Test extented types first
				if v_type & self.TYPE_EXT_BINARY:
					if v in ["yes", "0"]:
						type_pass = True

				# Test base type
				if (v_type & self.TYPE_MASK) == self.TYPE_ANY:
					type_pass = True
				elif (v_type & self.TYPE_MASK) == self.TYPE_INTEGER:
					if is_number(v) and isinstance(to_number(v), int):
						type_pass = True
				elif (v_type & self.TYPE_MASK) == self.TYPE_DECIMAL:
					if is_number(v):
						type_pass = True
				elif (v_type & self.TYPE_MASK) == self.TYPE_BINARY:
					if v in ["yes", "0"]:
						type_pass = True
				elif (v_type & self.TYPE_MASK) == self.TYPE_STRING:
					if re.search(r"\w\w+", v):
						type_pass = True
				elif (v_type & self.TYPE_MASK) == self.TYPE_DATE:
					if re.match(r"([0-9]{1,2}-)?([0-9]{1,2}-)?[0-9]{4}", v):
						type_pass = True
				elif (v_type & self.TYPE_MASK) == self.TYPE_URL:
					if re.match(r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", v):
						type_pass = True

				# Test extented types then
				if v_type & self.TYPE_EXT_POSITIVE:
					if is_number(v) and to_number(v) < 0:
						type_pass = False
				if v_type & self.TYPE_EXT_NEGATIVE:
					if is_number(v) and to_number(v) > 0:
						type_pass = False
				if v_type & self.TYPE_EXT_NOT_NULL:
					if is_number(v) and to_number(v) == 0:
						type_pass = False
					if v in ["0"]:
						type_pass = False

			# Throw an error if the value did not passed the tests
			if not type_pass:
				self.error("The type (%s) for this value (%s) is not in accordance with the type defined for this category." % (str(value_type), str(value)))
				return False

		if self.is_list():
			result = self.sanity_check(value, complete_list_value)
		else:
			result = self.sanity_check(value)

		if result == GenericCategory.ERROR:
			self.error("This value (%s) for %s is invalid, please double check." % (str(value), self.to_param()))
			return False
		elif result == GenericCategory.WARNING:
			self.warning("This value (%s) for %s is suspicious, please double check." % (str(value), self.to_param()), 2)
			return False
		return True

	def format_value(self, value):
		"""
		Format the value before storing it. Value must be a string.
		"""
		# Convert unicode to str
		if isinstance(value, unicode):
			value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
		# Value must be a string
		if not isinstance(value, str):
			raise error("The value (" + str(value) + ") is not a string, it is `%s'." % (str(type(value))))
		# Remove trailing spaces
		value = re.sub(r"(^\s+|\s+$)", "", str(value))
		# Set to lower case
		if not self.config_case_sensitive:
			value = value.lower()
		# If there is a transaltion table and this is not a multi category
		if len(self.config_translation_table) and not self.is_multi():
			value_temp = self.parse_translation_table(value, self.config_translation_table)
			if value_temp != None:
				value = value_temp
		# If there is a fixed value, return it if the value is not null, else return an empty string
		if self.get_global_config('config_fixed_value') and isinstance(self.get_global_config('config_fixed_value'), str):
			if value not in ["", "0"]:
				return self.get_global_config('config_fixed_value')
			return ""
		# return the value
		return value

	def parse_string(self, string):
		"""
		This value must be called by the device parser
		"""
		p = re.compile(self.get_global_config("string_pattern"), flags=re.S)
		m = p.match(string)

		if m:
			if m.group(1) != string:
				self.info("Parse this sub-string `%s' out-of `%s'" % (m.group(1), string), 3)
			string = m.group(1)
			self.parse(string)

	def parse(self, string):
		self.set_value(string)

	@classmethod
	def parse_translation_table(cls, value, translation_table = None):
		"""
		Loop through the elements of the translation table and look if there is a match.
		If so, returns the item at the position 1. The regular expression to be checked is at the
		postion 0.
		"""
		# By default use the transaltion table of the class (if none specified)
		if translation_table == None:
			translation_table = cls.config_translation_table

		# If this is a multi value translation table
		if isinstance(value, list):
			new_value = object_clone(value)
			for i, sub_value in enumerate(value):
				if i < len(translation_table) and translation_table[i]:
					value_temp = cls.parse_translation_table(sub_value, translation_table[i])
					if value_temp != None:
						new_value[i] = value_temp
			return new_value
		# If this is a simple string
		elif isinstance(value, str):
			for translation in translation_table:
				if re.match(translation[0], value):
					return translation[1]
			return None
		# Otherwise, unsupported value
		else:
			raise error("Unknown value type for the translation table.")

	@classmethod
	def get_list_from_translation_table(cls, translation_table, value = True):
		"""
		This function generates a list from a translation table.
		By default the list is generated from the values, but it can as
		well be generated from the regexpr by setting value to False
		"""
		t_list = []
		for translation in translation_table:
			if isinstance(value, int):
				t_list.append(translation[value])
			elif value:
				t_list.append(translation[1])
			else:
				t_list.append(translation[0])
		return t_list

	def parse_format(self, string, format_list):
		"""
		Parse a string and extract data according to a specific format.
		The format string is reaplaced by a regular expression, following these rules:
		- '@,' is replaced to match any delimiters (,;\n ...)
		- '@n' tells there must be a number
		- '@s' tells there must be a string (a string is a word without spaces and with
		       at least 1 non-numerical character, length must be at least 2 characters)
		- '@e' empty regular expression to enable a custom match. This should be followed
		       by a regular expression and some parenthesis to match.
		- '{..}' after a '@n0{...}' for example, defines the options
		- Options for a number:
			- 0-9: the resolution of a number
			- x: if the number should be expanded
			- y: if the number should be expanded with a power of 2
			- i: the number is an integer
			- d: the number is a decimal
			- p: match only positive numbers
			- n: match only negative numbers
		- Options for a empty tag:
			- 0-9: number of position it should jump. See "current_position_jump".
			       If none is specificed, the default value is 1.
		- '@n0', '@n1', ... tells this number will be returned
		The other characters are kept intact
		The result will have the form: [[@n0, @n1, ...], [@n0, '', ...], ...]
		"""

		# Options parser
		def option_number(options, default = 0):
			"""
			This generic function returns the number from the option parameter
			"""
			m = re.match(r"\{[^\}0-9]*([0-9]+)[^\}0-9]*\}", options)
			if m:
				return m.group(1)
			return default
		def option_is_match(options, character, default = False):
			"""
			This generic function True if the option exists, "default" otherwise
			"""
			m = re.match(r"\{[^\}]*" + str(character) + "[^\}]*\}", options)
			if m:
				return True
			return default
		def get_number_resolution(options):
			"""
			This funtion test the option arguments and return the resolution of a number
			"""
			return option_number(options, self.config_resolution)
		def is_expandable(options):
			"""
			This funtion test if the argument is expandable
			"""
			return option_is_match(options, "x", self.config_expand_units)
		def is_expandable_pow2(options):
			"""
			This funtion test if the argument is expandable and should be expanded with power of 2
			"""
			return option_is_match(options, "y", self.config_expand_units)
		def is_integer(options):
			"""
			This funtion test if the number must be an integer
			"""
			return option_is_match(options, "i", False)
		def is_decimal(options):
			"""
			This funtion test if the number must be an decimal
			"""
			return option_is_match(options, "d", False)
		def is_positive(options):
			"""
			This funtion test if the number must be positive
			"""
			return option_is_match(options, "p", False)
		def is_negative(options):
			"""
			This funtion test if the number must be negative
			"""
			return option_is_match(options, "n", False)
		def get_number_jump(options):
			"""
			This funtion test the option arguments and return the number of jump
			"""
			return option_number(options, 1)

		# Handle strings for format_list
		if isinstance(format_list, str):
			format_list = [format_list]

		# Calculate the maximum number of items
		nb_items = 0
		for format in format_list:
			for v in re.findall("@([,nse])([0-9]*)", format):
				if v[1]:
					nb_items = max([nb_items, int(v[1]) + 1])

		# Start the main loop. Convert the format string to a regexpr and test if it matches
		output = []
		for format in format_list:
			info = {}
			current_position = 0
			# Parse the format string to convert it to a regular expression
			regexpr_format = format
			for v in re.findall("@([,nse])([0-9]*)(\{[0-9xyipnd]+\}){0,1}", format):

				regexpr_format_sub = ""
				current_position_jump = 0

				# If it is a number
				if v[0] == "n":
					if is_positive(v[2]):
						regexpr_sign = "(?<!-)"
					elif is_negative(v[2]):
						regexpr_sign = "-"
					else:
						regexpr_sign = "-{0,1}"
					if is_integer(v[2]):
						regexpr_format_sub = "\s*(?<!,|\.|[0-9])(" + regexpr_sign + "[0-9]+)(?!,|\.|[0-9])\s*"
					elif is_decimal(v[2]):
						regexpr_format_sub = "\s*(?<![0-9])(" + regexpr_sign + "[0-9]+[\.,][0-9]*)(?![0-9])\s*"
					else:
						regexpr_format_sub = "\s*(?<![0-9])(" + regexpr_sign + "[0-9]+[\.,]{0,1}[0-9]*)(?![0-9])\s*"
					current_position_jump = 1
					if is_expandable(v[2]) or is_expandable_pow2(v[2]):
						regexpr_format_sub = regexpr_format_sub + "[\s\(]*(k|m|M|K|T|n|u|\xb5)?[\)\s]*"
						current_position_jump = 2
				# If it is a separator
				elif v[0] == ",":
					regexpr_format_sub = "([\s,;-@]+)"
					current_position_jump = 1
				# If it is a string
				elif v[0] == "s":
					regexpr_format_sub = "\s*((?=[a-zA-Z])[\w\-_]{2,})\s*"
					current_position_jump = 1
				# If it is an empty match
				elif v[0] == "e":
					regexpr_format_sub = ""
					current_position_jump = get_number_jump(v[2])
				# Unknown format
				else:
					raise error("Unknown format: (@" + v[0] + v[1] + v[2] + ").")

				# Update the position
				if v[1]:
					info[v[1]] = {
						'index': current_position,
						'type': v[0],
						'options': v[2]
					}
				# Update the current position
				current_position = current_position + current_position_jump

				# Replace the format string
				regexpr_format = regexpr_format.replace("@" + v[0] + v[1] + v[2], "(?:" + regexpr_format_sub + ")", 1)

			# Execute the regular expression on the string
			for values in re.findall(regexpr_format, string, flags=re.IGNORECASE|re.MULTILINE|re.DOTALL):

				# Initialize the sub-output list
				sub_output = [''] * nb_items
				for result_number in info:
					index = int(info[result_number]['index'])
					# Read the value
					value = values
					if  isinstance(values, (list, tuple)):
						value = values[index]
					# Format number
					if info[result_number]['type'] == "n" and is_number(value):
						value = to_number(value)
						is_expanded = False
						if is_expandable(info[result_number]['options']):
							try:
								value = {
									'T': lambda x : x * 1000000000,
									'M': lambda x : x * 1000000,
									'k': lambda x : x * 1000,
									'K': lambda x : x * 1000,
									'm': lambda x : x / 1000.,
									'u': lambda x : x / 1000000.,
									'\xb5': lambda x : x / 1000000.,
									'n': lambda x : x / 1000000000.
								}[values[index + 1]](value)
								is_expanded = True
							except:
								pass
						if is_expandable_pow2(info[result_number]['options']):
							try:
								value = {
									'T': lambda x : x * (1024 * 1024 * 1024),
									'M': lambda x : x * (1024 * 1024),
									'k': lambda x : x * 1024,
									'K': lambda x : x * 1024,
									'm': lambda x : x / 1024.,
									'u': lambda x : x / (1024. * 1024.),
									'\xb5': lambda x : x / (1024. * 1024.),
									'n': lambda x : x / (1024. * 1024. * 1024.)
								}[values[index + 1]](value)
								is_expanded = True
							except:
								pass
						# Multipy by the ratio not already expanded
						if not is_expanded:
							value = value * self.get_global_config('config_convert_ratio')
						# Set the resolution
						res_format = "%." + str(get_number_resolution(info[result_number]['options'])) + "f"
						value =  res_format % float(value)

					# Store the result
					sub_output[int(result_number)] = value

				# Update the original string
				string = re.sub(regexpr_format, "", string, 1)
				# Store the result into the main table
				output.append(sub_output)

			if len(output):
				break

		return output

	def parse_binary(self, string, regexpr_yes = None, regexpr_no = None):
		"""
		Return 'yes', '0' or '' if unknown.
		"""
		if regexpr_yes and re.search(regexpr_yes, string.lower()):
			return "yes"
		if regexpr_no and re.search(regexpr_no, string.lower()):
			return "0"
		v = self.to_binary(string)
		if v == None:
			return ""
		if v:
			return "yes"
		return "0"

	def parse_feature(self, string, feature_name = ""):
		"""
		This function will return a number reflecting the number of the same feature
		contained in this string. It will return a null string if nothing is found.
		If feature_name has a value equal to "", it will return either "yes", a number or
		an empty string.
		The feature name can be a list or a string in lower case only.
		"""
		check_naked = False
		check_regexpr = True
		# Generate the regular expression for the feature list
		if isinstance(feature_name, list):
			if "" in feature_name:
				feature_name = list(feature_name)
				feature_name.remove("")
				check_naked = True
			feature_name = '|'.join(feature_name)
		elif feature_name == "":
			check_naked = True
		if feature_name == "":
			check_regexpr = False
		feature_name_regexpr = "(" + feature_name + ")"

		values = []
		# Check regular expression value
		if check_regexpr:
			feature_name_regexpr = "(?:[a-z_-]*[\\(\\[\\)\\]/\\\\-])*" + feature_name_regexpr + "\\b"

			# Try to identify separators
			# For example: 2xSPI/2xI2C/4xUART/HDLC/SC/CAN/USB
			# 2xSSP/I2C/3xHS-UART/CAN/USB
			separator_list = ['\n', ';', '\\', '/']
			for separator in separator_list:
				element_list = string.split(separator)
				# If there is no match, discard
				if len(element_list) == 1:
					continue
				is_valid = True
				shortened_string = []
				for element in element_list:
					# If one of the element does not match the following regular expression, discard
					if not re.match(r".*[a-z0-9_\-]{2,}.*", element.lower()):
						is_valid = False
						break
					# If one of the element matches with the features
					if re.search(feature_name_regexpr, element.lower()):
						shortened_string.append(element)
				# If all the elements are valid and it found matches in the shortened strings, then update the string
				if is_valid and len(shortened_string):
					string = separator.join(shortened_string)
					break

			values = self.parse_format(string.lower(), ["@n0{0i}[x-]?\s*@e" + feature_name_regexpr, "@e" + feature_name_regexpr + "\s*:@n0{0i}", "@n0{0i}@,@e" + feature_name_regexpr])
			if len(values) == 0 and re.search("(?!bit\s*)\\b" + feature_name_regexpr + "(?!\s*resolut)", string.lower()):
				values = [["yes"]]
		# Check naked value
		if len(values) == 0 and check_naked:
			# Select only the raw value (no parenthesis, etc.)
			string = re.sub(r'\([^)]*\)', '', string)
			if is_number(string.lower()):
				values = [[str(to_number(string.lower()))]]
			else:
				values = [[self.parse_binary(string.lower())]]

		# If no result was founded
		if len(values) == 0 or len(values[0]) == 0 or not values[0][0]:
			return ""

		# Addition the same feature number if any
		value = "";
		for v in values:
			value = self.merge_numbers(value, v[0])

		# Check the value and format it if needed
		if is_float(value):
			if to_number(value) > 0:
				value = "yes"
			else:
				# Else cast it to an integer
				value = str(int(to_number(value)))

		return str(value)

	def parse_number(self, string, regexpr = ["^@n0$"]):
		"""
		Return the number
		"""
		values = self.parse_format(string, regexpr)
		if len(values):
			return values[0][0]
		return ""

	def parse_number_list(self, string, regexpr = ["@n0"]):
		"""
		Parse a list of numbers.
		Return a list with numbers formated as strings.
		"""
		values = self.parse_format(string, regexpr)
		value_list = []
		for value in values:
			value_list.append(value[0])
		return value_list

	def parse_number_min(self, string, regexpr = ["@n0"]):
		"""
		Return the minimal number in a string
		"""
		value_range = self.parse_number_list(string, regexpr)
		value_range.sort(lambda a,b: cmp(float(a), float(b)))
		if len(value_range):
			return value_range[0]
		return ""

	def parse_number_max(self, string, regexpr = ["@n0"]):
		"""
		Return the maximal number in a string
		"""
		value_range = self.parse_number_list(string, regexpr)
		value_range.sort(lambda a,b: cmp(float(a), float(b)))
		if len(value_range):
			return value_range[-1]
		return ""

	def to_binary(self, v):
		zero_regexpr = "^\s*(" + '|'.join(self.zero_match_list) + ")\s*$"
		if re.search(r"^\s*(yes|true|[1-9][0-9]*|one|ok)\s*$", str(v).lower()):
			return 1
		elif re.search(zero_regexpr, str(v).lower()):
			# If it matched one of the 'ignore' config, then change the merging scheme to the lowest intrusive one
			if re.search("^\s*(-|)\s*$", str(v).lower()):
				self.config_reduced_trustability = True
			return 0
		return None

	@classmethod
	def ignore_minus_char(cls):
		cls.config_ignore_minus_char = True

	@classmethod
	def consider_empty_values(cls):
		cls.config_ignore_empty = False

	def merge_numbers(self, value1, value2):
		return merge_numbers(value1, value2, strategy = self.config_merge_strategy, options = self.config_merge_options)

	def merge(self, new_c, merge_strategy = None):
		"""
		Merge the values of the current category with 'new_c'
		"""
		# Default value for merge_strategy
		if merge_strategy == None:
			merge_strategy = self.config_merge_strategy
		v1 = self.get_value()
		v2 = new_c.get_value()
		# List vs. List
		if category_is_list(self) and category_is_list(new_c):
			merged_v = merge_lists(v1, v2, strategy = merge_strategy, options = self.config_merge_options)
			self.set_list_value(merged_v)
		else:
			merged_v = merge_values(v1, v2, strategy = merge_strategy, options = self.config_merge_options)
			self.set_value(merged_v)
		# DEBUG
		if debug_trace_match(self.to_param()) or debug_trace_match(new_c.to_param()):
			self.debug("Merging Categories `%s' into `%s': `%s' and `%s' (strategy=%s|options=%s) -> `%s'" % (str(new_c.to_param()), str(self.to_param()), str(v1), str(v2), str(merge_strategy), str(self.config_merge_options), str(merged_v)))


class GenericListCategory(GenericCategory):
	config_merge_trust_strategy = MERGE_STRATEGY_FILL | MERGE_LIST_NO_ADD

	@classmethod
	def is_list(cls):
		return True

	@classmethod
	def get_default_value(cls):
		return []

	def set_value(self, value):
		self.set_list_value(value)

	def parse(self, string):
		self.set_value([string])

class GenericMultiCategory(GenericCategory):
	# Number of values by default
	config_nb_values = 0

	def __init__(self, index = -1):
		if self.config_nb_values == 0:
			raise error("`config_nb_values' is not defined for this class", self)
		if len(self.get_type()) != self.config_nb_values:
			raise error("`get_type' is not properly defined for this class: `%s'" % (str(self.get_type())), self)
		self.default_value = self.get_default_value()
		super(GenericMultiCategory, self).__init__(index)

	@classmethod
	def get_default_value(cls):
		return [''] * cls.config_nb_values

	@classmethod
	def is_multi(cls):
		return True

	def format_value(self, value):
		"""
		Format the value of a category.
		The value must be a list containing string arguments.
		"""
		if not isinstance(value, list):
			raise error("This value (%s) is not a list." % (str(value)), self)
		# Generate and format the value list
		value_list = []
		for sub_value in value:
			value_list.append(super(GenericMultiCategory, self).format_value(sub_value))

		# Handle the fixed value for multi value type.
		if self.get_global_config('config_fixed_value'):
			is_null = True
			for sub_value in value_list:
				if sub_value:
					is_null = False
					break
			if not is_null:
				value_list = merge_values(value_list, self.get_global_config('config_fixed_value'))

		# If there is a transaltion table
		if len(self.config_translation_table):
			for i, sub_value in enumerate(value_list):
				if i < len(self.config_translation_table) and self.config_translation_table[i]:
					value_temp = self.parse_translation_table(sub_value, self.config_translation_table[i])
					if value_temp != None:
						value_list[i] = value_temp

		# Return the multiple value list
		return value_list

class GenericMultiListCategory(GenericMultiCategory):
	config_merge_trust_strategy = MERGE_STRATEGY_FILL | MERGE_LIST_NO_ADD

	def __init__(self, index = -1):
		super(GenericMultiListCategory, self).__init__(index)

	@classmethod
	def get_default_value(cls):
		return [super(GenericMultiListCategory, cls).get_default_value()]

	@classmethod
	def is_multi(cls):
		return True

	@classmethod
	def is_list(cls):
		return True

	def set_value(self, value):
		self.set_list_value(value)

class GenericFeatureCategory(GenericCategory):
	config_multiple_categories = True
	extra_feature_regexpr = []
	config_category_match_extra_feature = True
	config_merge_strategy = MERGE_STRATEGY_ADD
	config_merge_with_original_strategy = MERGE_STRATEGY_REPLACE
	config_binary = False

	@classmethod
	def get_type(cls):
		return [cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE | cls.TYPE_EXT_BINARY]

	@classmethod
	def add_feature_regexpr(cls, regexpr):
		"""
		This function is mainly used for hooks to add a regular expression to match a feature
		"""
		# Register the new f
		if not isinstance(regexpr, list):
			regepxr = [regexpr]
		cls.extra_feature_regexpr = merge_lists(cls.extra_feature_regexpr, regexpr)
		# Add the new features to match the category
		if cls.config_category_match_extra_feature:
			cls.add_category_regexpr(".*\\b(" + "|".join(cls.extra_feature_regexpr) + ")\\b.*")

	def get_feature_regexpr(self):
		"""
		Return a list of words describing the feature
		"""
		raise error("The function `get_feature_regexpr' must be defined for this category.", self)

	def post_value_processing(self, value, string):
		"""
		Hook function to post process the value
		"""
		return value

	def parse(self, string):

		# Check which category has been selected
		index = self.get_global_config("category_regex_index")
		if index == -1:
			raise error("Index cannot not be equal to -1. Unknown error.")

		# Retrieve the regular expression
		feature_regexpr = self.get_feature_regexpr()
		if isinstance(feature_regexpr, list):
			feature_regexpr = feature_regexpr[index]
		if isinstance(feature_regexpr, str):
			feature_regexpr = [feature_regexpr]
		regexpr = merge_lists(self.extra_feature_regexpr, feature_regexpr, strategy = MERGE_KEEP_EMPTY|MERGE_KEEP_ORDER)

		# Parse the features
		value = self.parse_feature(string, regexpr)
		# Test value in order to avoid empty strings
		if value and self.config_binary:
			value = self.parse_binary(value)

		# Process extra code if needed
		value = self.post_value_processing(value, string)

		self.set_value(self.format_value(value))

class GenericBinaryFeatureCategory(GenericFeatureCategory):
	config_binary = True

	@classmethod
	def get_type(cls):
		return [cls.TYPE_BINARY]

class GenericSubCategory(GenericCategory):
	"""
	A Sub-category is a category that will be merged to its parent.
	Its parent category must be a multi-value category
	"""
	# The class of the parent category which it belongs to
	# Must be a multi-value category
	config_parent_category = None
	# The value index of the parent multi-value parameter
	config_value_index = -1

	def is_sub_category(self):
		return True

	def get_parent_category(self):
		"""
		Return the parent category class
		"""
		return self.config_parent_category

	def post_merge_processing(self, value, sub_value):
		"""
		This function will process the value after being merged.
		The value past in argument is therefore the value of the parent element.
		sub_value is this sub category.
		This function must returned the processed value.
		"""
		return value

	def merge_with_parent(self, parent_c):
		"""
		Merge this category with its parent
		"""
		value = parent_c.get_value()

		# Make sure the category has multiple values
		if not category_is_multi(parent_c):
			raise error("The parent category (%s) is not a multi-value category, cannot merge this category (%s)" % (parent_c.to_param(), self.to_param()))
		# If there is a value to set and the parent category has no value, create one
		if len(value) == 0 and self.get_value():
			value = parent_c.get_default_value()
		# Convert the value to a list if not already done
		if not parent_c.is_list():
			value = [value]
		# List each element of the list
		for v in value:
			# Make sure the value index has been set
			if self.config_value_index == -1:
				raise error("The config_value_index for the sub-value `%s' of `%s' has not been set." % (str(self.to_param()), str(parent_c.to_param())))
			# Make sure the length of the multi value is bigger
			if self.config_value_index < 0 or self.config_value_index >= len(v):
				raise error("Merging `%s' into `%s' - The value index for this sub value category is not in the range of the number of values of its parent element. Config issue. (value index: %i, parent value length: %i, value: %s, parent value: %s)" % (str(self.to_param()), str(parent_c.to_param()), self.config_value_index, len(v), self.get_value(), str(v)))

			# Check the existing value if any
			# WHY?! -> if not v[self.config_value_index] or v[self.config_value_index] == self.get_value():
			# Assign the new value
			v[self.config_value_index] = merge_values(v[self.config_value_index], self.get_value(), strategy = self.config_merge_strategy, options = self.config_merge_options)
		# Revert to a non-list
		if not parent_c.is_list():
			value = value[0]
		# Post process the value if needed
		value = self.post_merge_processing(value, self.get_value())

		# DEBUG
		if debug_trace_match(self.to_param()) or debug_trace_match(parent_c.to_param()):
			self.debug("Merging Sub-Category `%s' into `%s': `%s' and `%s' -> `%s'" % (str(self.to_param()), str(parent_c.to_param()), str(self.get_value()), str(parent_c.get_value()), str(value)))

		# Store the new value
		parent_c.set_value(value)

class GenericSubFeatureCategory(GenericSubCategory, GenericFeatureCategory):
	config_merge_strategy = MERGE_STRATEGY_MAX
	config_merge_with_original_strategy = MERGE_STRATEGY_REPLACE

class GenericBinarySubFeatureCategory(GenericSubCategory, GenericBinaryFeatureCategory):
	pass

class GenericFeatureExtendedCategory(GenericFeatureCategory, GenericMultiCategory):
	"""
	A Binary Extended category is a category with 2 values.
	The first one is a boolean, stating yes, this module is available in this device.
	The second one is a string containg the features of this category.
	"""
	config_multiple_categories = True
	config_nb_values = 2

	config_merge_options = {
		'list_rules': [
			# If the item has 0 feature, fill the rest with a dash
			{'pattern': ['0', r'^[0\-]?$'], 'fill': ['0', '-']},
			# If there is at least one non null attribute and the nb peripherals is empty, set it to yes
			{'pattern': [r'^0?$', r'[^-0]+'], 'fill': ['yes']}
		]
	}

	# This needs to be updated with the following format
	translation_table = [[
		# 1. value
		# 2. features or [regular expression] or [class name]
		# 3. Optional. Category regular expression for the sub category
		# 4. Optional. Category class name
		# Ex: ["aes", ["aes"], ".*aes.*"]
	]]

	@classmethod
	def get_type(cls):
		# Return type
		return_type = [
			cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE | cls.TYPE_EXT_BINARY,		# Nb peripherals / yes or no
		]
		for i in range(1, cls.config_nb_values):
			return_type.append('/'.join(cls.get_list_from_translation_table(cls.translation_table[i-1], 0)))	# AES/DES/...

		return return_type

	def string_to_extended(self, string, translation_table):
		extended = ""
		# Loop through the types
		for entry in translation_table:
			# This function retreives the number of features
			feature = self.parse_feature(string, entry[1])
			# Translate feature into binay
			if self.parse_binary(feature) == "yes":
				extended = merge_strings(extended, entry[0], strategy = MERGE_STRATEGY_REPLACE | MERGE_CONCATENATE)
		# Returns the string
		return extended

	def parses(self, string):

		# Check which category has been selected
		index = self.get_global_config("category_regex_index")
		if index == -1:
			raise error("Index cannot not be equal to -1. Unknown error.")

		# Retrieve the regular expression
		feature_regexpr = self.get_feature_regexpr()
		if isinstance(feature_regexpr, list):
			feature_regexpr = feature_regexpr[0]
		if isinstance(feature_regexpr, str):
			feature_regexpr = [feature_regexpr]
		regexpr = merge_lists(self.extra_feature_regexpr, feature_regexpr, strategy = MERGE_KEEP_EMPTY|MERGE_KEEP_ORDER)

	def post_value_processing(self, value, string):

		# Defaults
		value = [ value ]

		# Default values
		empty = True
		for i in range(1, self.config_nb_values):
			value.append(self.string_to_extended(string, self.translation_table[i - 1]))
			if value[i]:
				empty = False

		# If the type is not null, then it means that at least one module is there
		if not empty and not value[0]:
			value[0] = "yes"

		return value

class GenericFeatureExtendedSubCategory(GenericSubCategory):
	# This must be set
	config_multiple_categories = True
	translation_table_item = -1
	config_merge_strategy = MERGE_STRATEGY_REPLACE | MERGE_CONCATENATE

	@classmethod
	def get_type(cls):
		return [ cls.TYPE_STRING ]

	@classmethod
	def extended_classes(cls):
		# This is the empty definition fo the result of this function
		class_list = []
		# Find the translation table
		translation_table = cls.config_parent_category.translation_table
		# Loop Through the mutli values
		for multi_index, table in enumerate(translation_table):
			# Loop through the entries
			for index, entry in enumerate(table):
				# Check if this entry should be added
				if len(entry) > 2:
					# Generates the class name
					if len(entry) > 3:
						name = entry[3]
					else:
						name = cls.config_parent_category.to_param() + entry[0].upper()
					# Generate the class
					class_list.append(type(name, (cls,), dict(config_value_index = multi_index + 1, translation_table_item = index)))
		# Return the class list
		return class_list

	def string_to_extended(self, string, translation_table):
		extended = ""
		# Loop through the types
		for entry in translation_table:
			# This function retreives the number of features
			feature = self.parse_feature(string, entry[1])
			# Translate feature into binay
			if self.parse_binary(feature) == "yes":
				extended = merge_strings(extended, entry[0], strategy = MERGE_STRATEGY_REPLACE | MERGE_CONCATENATE)
		# Returns the string
		return extended

	def post_merge_processing(self, value, sub_value):
		# Set the binary value to yes
		if value[0] == "" and sub_value:
			value[0] = "yes"
		return value

	def get_category_regexpr(self):
		# Find the translation table
		translation_table = self.config_parent_category.translation_table
		# Make sure the config_value_index is within the boundaries
		if self.config_value_index < 1 and self.config_value_index > len(translation_table):
			raise error("The index `config_value_index' (%i) is not within the boundaries" % (self.config_value_index))
		table = translation_table[self.config_value_index - 1]
		# Make sure the index is within the boundaries
		if self.translation_table_item < 0 or self.translation_table_item >= len(table):
			raise error("The index `translation_table_item' (%i) is not within the boundaries" % (self.translation_table_item))

		return table[self.translation_table_item][2]

	def parse(self, string):
		# Retrieve the translation table
		if not self.config_parent_category:
			raise error("The parent category must be set with `config_parent_category'.")
		translation_table = self.config_parent_category.translation_table

		# Make sure the value index is within the boundary of the translation table
		if self.config_value_index < 1 or self.config_value_index > len(translation_table):
			raise error("The config value index `config_parent_category' (%i) is not with the range, please double check." % (self.config_value_index))
		entry = translation_table[self.config_value_index - 1]

		# Make sure the translation_table_item value is within the boundaries
		if self.translation_table_item < 0 or self.translation_table_item >= len(entry):
			raise error("The translation table index `translation_table_item' (%i) is not with the range, please double check." % (self.translation_table_item))
		entry = entry[self.translation_table_item]

		# Get the number of features
		value = self.string_to_extended(string, [entry[0], entry[1] + [""]])

		# Set the value
		self.set_value(self.format_value(value))

