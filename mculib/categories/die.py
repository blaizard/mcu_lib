#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from generic import *
from mculib.log import *
import re

class CategoryBus(GenericMultiListCategory):
	"""
	This category gives details on the buses architecture
	"""
	config_nb_values = 4

	@classmethod
	def get_type(cls):
		return [
			cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE,                         # Number of buses
			CategoryBusType.get_type()[0],                                    # Bus type (external memory, ...)
			cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE | cls.TYPE_EXT_NOT_NULL, # Bus width (in bit)
			CategoryBusMode.get_type()[0]                                     # Bus mode (read/write)
		]

	def parse(self, string):
		# Parse the string using a classic pattern
		(value_list, left_string) = self.parse_list(string, [ "@n0{pi}x", CategoryBusType.config_translation_table, "@n0{pi}(?=-?(BIT|bit))", CategoryBusMode.config_translation_table ])
		self.set_value(value_list)

class CategoryBusType(GenericCategory):
	"""
	Define the type of a bus
	"""
	config_translation_table = [
		[ r".*\b(int).*\b(mem).*", "int_memory" ],
		[ r".*\b(ext).*\b(mem).*", "ext_memory" ],
		[ r".*\b(periph).*", "peripheral" ],
		[ r".*\b(coproc).*", "coprocessor" ],
		[ r".*", "" ],
	]

class CategoryBusMode(GenericCategory):
	"""
	Define the mode of a bus (read/write)
	"""
	config_translation_table = [
		[ r".*\b(w|write)\b.*(r|read)\b.*", "r/w" ],
		[ r".*\b(r|read)\b.*(w|write)\b.*", "r/w" ],
		[ r".*\b(r|read)\b.*", "r" ],
		[ r".*\b(w|write)\b.*", "w" ],
		[ r".*", "" ],
	]

class CategoryProcess(GenericCategory):
	"""
	Process size of the device.
	"""
	# Default ratio is 'nm'
	config_convert_ratio = 0.000000001

	@classmethod
	def get_type(cls):
		return [cls.TYPE_DECIMAL | cls.TYPE_EXT_POSITIVE | cls.TYPE_EXT_NOT_NULL]

	def parse(self, string):
		values = self.parse_format(string, ["@n0{px9}m", "@n0{px9}"])
		if len(values) > 0:
			self.set_value(values[0][0])

class CategoryMinVoltage(GenericCategory):
	config_resolution = 1
	config_merge_strategy = MERGE_STRATEGY_MIN
	config_multiple_categories = True
	# This value is kept for the alias
	config_alias_delete_if_duplicate = False

	@classmethod
	def get_type(cls):
		return [cls.TYPE_DECIMAL | cls.TYPE_EXT_POSITIVE]

	def get_category_regexpr(self):
		return ".*(supply.*voltage|voltage.*supply|voltage.*range|operating\s*voltage|min.*voltage|vcc.*min|vdd.*min).*"
	def get_category_regexpr_exclude(self):
		return [r".*max.*", r".*peak.*"]
	def parse(self, string):
		self.set_value(self.parse_number_min(string))

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 5:
			return GenericCategory.ERROR
		return GenericCategory.PASS

class CategoryMaxVoltage(GenericCategory):
	config_resolution = 1
	config_merge_strategy = MERGE_STRATEGY_MAX
	config_multiple_categories = True
	# This value is kept for the alias
	config_alias_delete_if_duplicate = False

	@classmethod
	def get_type(cls):
		return [cls.TYPE_DECIMAL | cls.TYPE_EXT_POSITIVE]

	def get_category_regexpr(self):
		return ".*(supply.*voltage|voltage.*supply|voltage.*range|operating\s*voltage|max.*voltage|vcc.*max|vdd.*max).*"
	def get_category_regexpr_exclude(self):
		return [r".*min.*", r".*peak.*"]
	def parse(self, string):
		self.set_value(self.parse_number_max(string))

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb < 0.5:
			return GenericCategory.ERROR
		return GenericCategory.PASS

class CategoryMinTemperature(GenericCategory):
	config_merge_strategy = MERGE_STRATEGY_MIN
	config_multiple_categories = True
	# This value is kept for the alias
	config_alias_delete_if_duplicate = False

	@classmethod
	def get_type(cls):
		return [cls.TYPE_DECIMAL | cls.TYPE_EXT_NEGATIVE]

	def get_category_regexpr(self):
		return [".*(operating|min).*(temperature|temp).*", ".*(temperature|temp).*(range).*"]
	def get_category_regexpr_exclude(self):
		return [r".*max.*"]

	def parse(self, string):
		self.set_value(self.parse_number_min(string))

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 0:
			return GenericCategory.ERROR
		return GenericCategory.PASS

class CategoryMaxTemperature(GenericCategory):
	config_merge_strategy = MERGE_STRATEGY_MAX
	config_multiple_categories = True
	# This value is kept for the alias
	config_alias_delete_if_duplicate = False
	@classmethod
	def get_type(cls):
		return [cls.TYPE_DECIMAL | cls.TYPE_EXT_POSITIVE]

	def get_category_regexpr(self):
		return [".*(operating|max).*(temperature|temp).*", ".*(temperature|temp).*(range).*"]
	def get_category_regexpr_exclude(self):
		return [r".*min.*"]

	def parse(self, string):
		self.set_value(self.parse_number_max(string))

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb < 25:
			return GenericCategory.ERROR
		return GenericCategory.PASS



class CategoryCurrent(GenericMultiListCategory):
	"""
	This category will have the following format:
	0. Current in A
	1. Voltage in V
	2. Temperature in C
	"""
	config_nb_values = 3

	config_merge_options = {
		'conflict': [0, 1, 1]
	}

	@classmethod
	def get_type(cls):
		return [
			cls.TYPE_DECIMAL | cls.TYPE_EXT_POSITIVE,
			cls.TYPE_DECIMAL | cls.TYPE_EXT_POSITIVE,
			cls.TYPE_DECIMAL,
		]

	@classmethod
	def get_parsing_fields(cls):
		return [
			"@n0{9x}@e(A|a)",
			"@n0{2x}@e(V|v)",
			"@n0@e(\\??C|\\??c)",
		]

	def parse(self, string):
		(value_list, string) = self.parse_list(string, self.get_parsing_fields())
		if string:
			raise error("Error while parsing `%s'." % (string))
		self.set_value(value_list)

class CategoryCurrentActive(CategoryCurrent):
	"""
	Current in active mode with code running from the program memory and all peripherals disabled.
	3. Frequency
	4. Type
	"""
	config_nb_values = 5

	config_merge_options = {
		'conflict': [0, 1, 1, 1, 1]
	}

	@classmethod
	def get_type(cls):
		type_list = CategoryCurrent.get_type()
		type_list.extend([
			cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE,
			CategoryCurrentActiveCodeType.get_type()[0],
		])
		return type_list

	@classmethod
	def get_parsing_fields(cls):
		parsing_fields = CategoryCurrent.get_parsing_fields()
		parsing_fields.extend([
			"@n0{xp}@e(HZ|Hz|hz|hZ)",
			CategoryCurrentActiveCodeType.config_translation_table
		])
		return parsing_fields

	def parse(self, string):
		# Handle µA/MHz if set
		temp = self.get_parsing_fields()
		temp.extend(["@n0{9x}@e(A|a)/MHz"])
		(value_list, string) = self.parse_list(string, temp)
		if string:
			raise error("Error while parsing `%s'." % (string))
		for value in value_list:
			if value[3] and value[5]:
				value[0] = str(to_number(value[3]) / 1000000. * to_number(value[5]))
			value.pop(5)
		self.set_value(value_list)

class CategoryCurrentActiveCodeType(GenericSubCategory):
	config_value_index = 4
	config_parent_category = CategoryCurrentActive
	config_translation_table = [
		[ r".*\b(coremark).*", "coremark" ],
		[ r".*\b(dhrystone)\b.*", "dhrystone" ],
		[ r".*\b(fibo).*", "fibonacci" ],
		[ r".*\b(while)\b.*", "while(1)" ],
		[ r".*\b(min).*", "min" ],
		[ r".*\b(max).*", "max" ],
		[ r".*\b(typ).*", "typical" ],
		[ r".*", "" ]
	]

class CategoryFunctionalMode(GenericCategory):
	"""
	This category contains the name of the functional mode
	0. name
	1. wakeup time from this mode in seconds
	"""
	def parse(self, string):
		self.set_value(string)

class CategoryWakeUpTime(GenericMultiCategory):
	"""
	This category contains the wakeup time from a sleep mode in seconds
	0. min
	1. max
	"""
	config_nb_values = 2
	def parse(self, string):
		self.set_value([self.parse_number_min(string, ["@n0{9xp}s", "@n0{9xp}"]), self.parse_number_max(string, ["@n0{9xp}s", "@n0{9xp}"])])

class CategoryCurrentDeepsleep(CategoryCurrent):
	"""
	Current in the deepest sleep mode where the CPU can be woken up by external peripheral.
	"""
	pass
class CategoryWakeUpTimeDeepsleep(CategoryWakeUpTime):
	pass
class CategoryNameDeepsleep(CategoryFunctionalMode):
	pass

class CategoryCurrentSleepRAMRTC(CategoryCurrent):
	"""
	Current in the deepest sleep mode with all RAM retention and RTC running.
	"""
	pass
class CategoryWakeUpTimeSleepRAMRTC(CategoryWakeUpTime):
	pass
class CategoryNameSleepRAMRTC(CategoryFunctionalMode):
	pass

class CategoryCurrentSleepRAM(CategoryCurrent):
	"""
	Current in the deepest sleep mode with all RAM retention.
	"""
	pass
class CategoryWakeUpTimeSleepRAM(CategoryWakeUpTime):
	pass
class CategoryNameSleepRAM(CategoryFunctionalMode):
	pass

class CategoryCurrentSleepRTC(CategoryCurrent):
	"""
	Current in the deepest sleep mode with RTC (or any other similar peripheral, TC, WDT) running.
	"""
	pass
class CategoryWakeUpTimeSleepRTC(CategoryWakeUpTime):
	pass
class CategoryNameSleepRTC(CategoryFunctionalMode):
	pass

class CategoryCurrentPeripheral(CategoryCurrent):
	"""
	Current in active mode with code running from the program memory and all peripherals disabled.
	"""
	pass
