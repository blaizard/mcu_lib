#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from generic import *
import math
import re

class CategoryMemory(GenericCategory):
	memory_type = ""

	@classmethod
	def get_type(cls):
		return [cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE]

	def parse(self, string):
		"""
		Parse a number.
		"""
		value = self.parse_format(string, ["@n0{yp}(bit|b)", "@n0{yp}"])
		if len(value):
			value = int(value[0][0])
			# If the value is already a power of 2, don't both
			if (int(value / 256) * 256) != value:
				# Make sure the value is a multiple of 1024
				mul = int(float(value) / 500)
				if mul:
					# Get the closest power of 2
					mul = pow(2, int(math.log(mul, 2) + 0.5))
					value = int(round(float(value) / (mul * 128)) * (mul * 128))
			self.set_value(self.format_value(str(value)))

class CategoryMemoryFlash(CategoryMemory):
	config_multiple_categories = True
	config_merge_strategy = MERGE_STRATEGY_MAX

	def get_category_regexpr(self):
		return r".*\b(flash|program.*memory)\b.*"
	def get_category_regexpr_exclude(self):
		return [r".*data.*"]

class CategoryMemoryEEPROM(CategoryMemory):

	def get_category_regexpr(self):
		return r".*\b(eeprom|e2prom|data.*memory)\b.*"

class CategoryMemoryFRAM(CategoryMemory):

	def get_category_regexpr(self):
		return r".*\b(fram|feram)\b.*"

class CategoryMemorySRAM(CategoryMemory):

	def get_category_regexpr(self):
		return r".*\b(sram|ram)\b.*"

class CategoryMemorySelfWrite(GenericBinaryFeatureCategory):

	def get_feature_regexpr(self):
		return [""]

	def get_category_regexpr(self):
		return r".*\b(self.*write)\b.*"

class CategoryMemoryCache(GenericBinaryFeatureCategory):

	def get_feature_regexpr(self):
		return [""]

	def get_category_regexpr(self):
		return r".*\b(cache)\b.*"

class CategoryMemoryDualBank(GenericBinaryFeatureCategory):

	def get_feature_regexpr(self):
		return [""]

	def get_category_regexpr(self):
		return r".*\b(dual\s*bank)\b.*"
