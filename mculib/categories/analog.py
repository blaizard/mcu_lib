#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from generic import *
from mculib.log import *
import re

class CategoryComparator(GenericFeatureCategory):
	config_merge_strategy = MERGE_STRATEGY_MAX
	config_merge_with_original_strategy = MERGE_STRATEGY_REPLACE

	def get_feature_regexpr(self):
		return [["comparator", "comparators", "ac"], ["comparator", "comparators", "ac", ""]]

	def get_category_regexpr_exclude(self):
		return [r".*(digital).*"]

	def get_category_regexpr(self):
		return [r".*\b(analog)\b(?!\s*comp).*", r".*\b(comparator|comparators|ac)\b.*"]

class CategoryOpAmp(GenericFeatureCategory):
	config_merge_strategy = MERGE_STRATEGY_MAX
	config_merge_with_original_strategy = MERGE_STRATEGY_REPLACE

	def get_feature_regexpr(self):
		return [["opamp", "op-amp", "amplifier"], ["opamp", "op-amp", "amplifier", ""]]

	def get_category_regexpr_exclude(self):
		return [r".*(digital).*"]

	def get_category_regexpr(self):
		return [r".*\b(analog)\b.*", r".*\b(opamp|op-amp|amplifier)\b.*"]

class CategoryGenericAnalog(GenericMultiListCategory):

	config_resolution = 0
	config_nb_values = 4
	config_multiple_categories = True

	@classmethod
	def get_type(cls):
		return [
			CategoryGenericAnalogPeripheral.get_type()[0], # Number of periphs
			CategoryGenericAnalogChannel.get_type()[0],    # Number of channels
			CategoryGenericAnalogResolution.get_type()[0], # Number of bits
			CategoryGenericAnalogSpeed.get_type()[0]       # Speed
		]

	# Defines which values are important when we merging
	config_merge_options = {
		'conflict': [0, 0, 1, 0],
		'list_rules': [
			# If the number of channels or the number of interface is 0, and the rest in null, set everything to 0
			{'pattern': ['0', r'^0?$', r'^0?$', r'^0?$'], 'fill': ['0', '0', '0', '0']},
			{'pattern': [r'^0?$', '0', r'^0?$', r'^0?$'], 'fill': ['0', '0', '0', '0']},
			# If the number of ADC is null but the rest not, set the number of ADC to yes
			{'pattern': [r'^0?$', r'[1-9]'], 'fill': ['yes']},
			{'pattern': [r'^0?$', None, r'[1-9]'], 'fill': ['yes']},
			{'pattern': [r'^0?$', None, None, r'[1-9]'], 'fill': ['yes']},
			# If there are zeros that should not be here, simply remove them
			# {'pattern': [r'(yes|[1-9])', r'0$'], 'fill': [None, '']}, Iyt can have 0 channels if only internal channels
			{'pattern': [r'(yes|[1-9])', None, r'0$'], 'fill': [None, None, '']},
			{'pattern': [r'(yes|[1-9])', None, None, r'0$'], 'fill': [None, None, None, '']},
		]
	}

	# Regular expression to parse a ADC or DAC
	regexpr_list = [
		"@n0@,@n1x@n2[-]?(?:b|bit)@,@n3{x}[bs]ps", # 0,1x2-bit,3kbps
		"@n0@,@n1x@n2[-]?(?:b|bit)", # 0,1x2-bit
		"@n1x@n2[-]?(?:b|bit)@,@n3{x}[bs]ps?", # 1x2-bit,3kbps
		"@n0x@n2[-]?(?:b|bit)@,[(\[]?@n1-?ch[)\]]?", #2 x 12-Bit (24ch)
		"@n1x@n2[-]?(?:b|bit)", # 1x2-bit
		"@n0,\s*@n1-ch,\s*@n2-(?:b|bit),\s*@n3{x}sps", # "1 adc, 10-ch, 16-bit, 460ksps"
	]

	def get_category_regexpr_exclude(self):
		return [r".*(num|#).*", r".*(ch).*", r".*(res).*"]
	def get_category_regexpr(self):
		return [r".*\b(analog|data\s*converters?)\b.*", ".*\\b" + self.feature_name + "\\b.*"]

	def parse(self, string):

		# Parse the string using a classic pattern
		(generic_value_list, left_string) = self.parse_list(string, [
			"@n0{pi}(?=[-:x ]" + self.feature_name + ")",
			"@n0{pi}(?=-?(ch|CH))",
			"@n0{pi}(?=-?(BIT|bit|b|B))",
			"@n0{px}(?=(sps|bps|SPS|BPS))" ])

		# It matches the generic categories
		if self.get_global_config("category_regex_index") == 0:

			# Keep only the values with an explicit number of peripheral set
			value_list = []
			for value in generic_value_list:
				if to_number(value[0]) != None:
					value_list.append(value)

			# Also use special patterns
			regexpr_list = []
			for regexpr in self.regexpr_list:
				regexpr_list.append("@e" + self.feature_name + "\s*" + regexpr)
				regexpr_list.append(regexpr + "\s*@e" + self.feature_name)
				regexpr_list.append("@e" + self.feature_name + "@," + regexpr)
				regexpr_list.append(regexpr + "@,@e" + self.feature_name)
			values = self.parse_format(string, regexpr_list)
			# Add the values to the current ones
			value_list.extend(values)

		else:

			# Also use special patterns
			value_list = self.parse_format(string, self.regexpr_list)
			# Add the values to the current ones
			value_list.extend(generic_value_list)

		self.set_value(value_list)

class CategoryGenericAnalogSpeed(GenericSubCategory):
	config_value_index = 3
	config_multiple_categories = True
	config_merge_strategy = MERGE_STRATEGY_MAX

	@classmethod
	def get_type(cls):
		return [cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE]

	def get_category_regexpr(self):
		return r".*" + self.config_parent_category.feature_name + ".*(speed|[km][bs]ps).*"

	def parse(self, string):
		value = self.parse_number(string)
		self.set_value(value)

class CategoryGenericAnalogChannel(GenericSubFeatureCategory):
	config_value_index = 1

	@classmethod
	def get_type(cls):
		return [cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE]

	def get_feature_regexpr(self):
		return [[""]]

	def get_category_regexpr(self):
		return r".*" + self.config_parent_category.feature_name + ".*(channel|ch|output).*"

	def get_category_regexpr_exclude(self):
		return [r".*(bit).*"]

	def sanity_check(self, value):
		# Make sure the value is positive
		if is_number(value):
			if to_number(value) < 0:
				return GenericCategory.ERROR
		return GenericCategory.PASS

class CategoryGenericAnalogPeripheral(GenericSubCategory):
	config_value_index = 0
	config_multiple_categories = True

	@classmethod
	def get_type(cls):
		return [cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE | cls.TYPE_EXT_BINARY]

	def get_category_regexpr(self):
		return [r".*(number|nb|#).*" + self.config_parent_category.feature_name, r".*" + self.config_parent_category.feature_name + ".*(module|unit).*", r"^" + self.config_parent_category.feature_name + "$"]

	def get_category_regexpr_exclude(self):
		return [r".*\b(ch|channel|chs|channels|output|outputs)\b.*"]

	def parse(self, string):
		value = self.parse_number(string)
		self.set_value(value)

class CategoryGenericAnalogResolution(GenericSubCategory):
	config_value_index = 2
	config_multiple_categories = True
	config_merge_strategy = MERGE_STRATEGY_MAX

	@classmethod
	def get_type(cls):
		return [cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE]

	def get_category_regexpr(self):
		return r".*" + self.config_parent_category.feature_name + ".*\b(resolutions?|bits?)\b.*"

	def get_category_regexpr_exclude(self):
		return [r".*(bit).*"]

	def parse(self, string):
		value = self.parse_number(string)
		self.set_value(value)

class CategoryGenericAnalogResolutionBis(GenericBinarySubFeatureCategory):
	config_value_index = 2
	config_multiple_categories = True
	config_merge_strategy = MERGE_STRATEGY_MAX

	@classmethod
	def get_type(cls):
		return [cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE]

	def get_feature_regexpr(self):
		return [[""], [""]]

	def get_category_regexpr_exclude(self):
		return [r".*\b(mode)\b.*"]

	def get_category_regexpr(self):
		return [r".*[0-9]+\s*-?\s*(bits?).*" + self.config_parent_category.feature_name + ".*",
				r".*" + self.config_parent_category.feature_name + ".*[0-9]+\s*-?\s*(bits?).*"]

	def get_fixed_value_regexpr(self):
		return ["@n0{p}-?\s*bits?"]

class CategoryADC(CategoryGenericAnalog):
	feature_name = "(a/d|adc|A/D|ADC)"
class CategoryDAC(CategoryADC):
	feature_name = "(d/a|dac|D/A|DAC)"

class CategoryADCSpeed(CategoryGenericAnalogSpeed):
	config_parent_category = CategoryADC
class CategoryDACSpeed(CategoryGenericAnalogSpeed):
	config_parent_category = CategoryDAC

class CategoryADCChannel(CategoryGenericAnalogChannel):
	config_parent_category = CategoryADC
class CategoryDACChannel(CategoryGenericAnalogChannel):
	config_parent_category = CategoryDAC

class CategoryADCPeripheral(CategoryGenericAnalogPeripheral):
	config_parent_category = CategoryADC
class CategoryDACPeripheral(CategoryGenericAnalogPeripheral):
	config_parent_category = CategoryDAC

class CategoryADCResolution(CategoryGenericAnalogResolution):
	config_parent_category = CategoryADC
class CategoryADCResolutionBis(CategoryGenericAnalogResolutionBis):
	config_parent_category = CategoryADC
class CategoryDACResolution(CategoryGenericAnalogResolution):
	config_parent_category = CategoryDAC
