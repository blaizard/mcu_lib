#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from generic import *
from mculib.log import *
import re

serial_peripheral_regexpr = r".*\b(digital|serial.*interface|com.*interface|connectivity|peripherals)\b.*"
other_features_regexpr = r".*(other|additional).*features?.*"

class CategoryIO(GenericFeatureCategory):
	config_merge_strategy = MERGE_STRATEGY_MAX

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*(general.*purpose)?.*\b(gp)?i[/\\]?os?\b.*"]
	def get_feature_regexpr(self):
		return [["ios", "io", "i/os", "i/o", "gpios", "gpio"], ["ios", "io", "i/os", "i/o", "gpios", "gpio", ""]]
	def get_category_regexpr_exclude(self):
		return [r".*\b(special|5v|strength)\b.*"]

class CategoryIO5VTolerant(GenericBinaryFeatureCategory):

	def get_feature_regexpr(self):
		return [["5v.*tolerant"], [""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(5v.*tolerant)\b.*"]

class CategoryIOStrength(GenericFeatureCategory):

	config_resolution = 3
	config_merge_strategy = MERGE_STRATEGY_MAX

	@classmethod
	def get_type(cls):
		return [cls.TYPE_DECIMAL]

	def get_category_regexpr(self):
		return r".*(drive.*strength|high.*current.*io).*"

	def parse(self, string):
		values = self.parse_format(string, ["@n0{x}A"])
		if len(values) == 1:
			# Set the absolute value (remove the +/-)
			value = str(abs(to_number(values[0][0])))
			self.set_value(value)

	def sanity_check(self, value):
		nb = to_number(value)
		if nb:
			if nb < 0.001 or nb > 0.1:
				return GenericCategory.ERROR
		return GenericCategory.PASS

class CategoryCustomLogic(GenericBinaryFeatureCategory):
	def get_feature_regexpr(self):
		return [[""], ["logic", "ccl", "clc"]]

	def get_category_regexpr(self):
		return [r"^\s*custom\s*logic\s*$", r".*\b(logic)\b.*"]

class CategoryTempSensor(GenericBinaryFeatureCategory):

	def get_feature_regexpr(self):
		return [["temp.* sensor"], ["temp.* sensor", ""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(temp\S*)\b.*\b(sensor)\b.*"]

class CategoryUSART(GenericFeatureCategory):

	def get_feature_regexpr(self):
		return [["uart", "usart"], ["uart", "usart", ""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*(usart|uart).*"]

	def get_category_regexpr_exclude(self):
		return [r".*\b(timers?)\b.*"]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 32:
			return GenericCategory.ERROR
		if nb and nb > 10:
			return GenericCategory.WARNING
		return GenericCategory.PASS

class CategoryI2C(GenericFeatureCategory):

	def get_feature_regexpr(self):
		return [["i2c", "iic", "twi"], ["i2c", "iic", "twi", ""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(i2c|iic|twi|two.*wire|2.*wire)\b.*"]

	def get_category_regexpr_exclude(self):
		return [r".*\b(timers?)\b.*"]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 32:
			return GenericCategory.ERROR
		if nb and nb > 10:
			return GenericCategory.WARNING
		return GenericCategory.PASS

class CategorySPI(GenericFeatureCategory):

	def get_feature_regexpr(self):
		return [["spi"], ["spi", ""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(spi)\b.*"]

	def get_category_regexpr_exclude(self):
		return [r".*\b(timers?|q[-\s]?spi|quad[-\s]?spi)\b.*"]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 32:
			return GenericCategory.ERROR
		if nb and nb > 10:
			return GenericCategory.WARNING
		return GenericCategory.PASS

class CategoryQSPI(GenericFeatureCategory):

	def get_feature_regexpr(self):
		return [["qspi", "quad-spi"], ["qspi", "quad-spi", ""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(qspi|quad\s*spi|quad-spi)\b.*"]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 2:
			return GenericCategory.ERROR
		if nb and nb > 1:
			return GenericCategory.WARNING
		return GenericCategory.PASS

class CategoryLIN(GenericFeatureCategory):

	def get_feature_regexpr(self):
		return [["lin"], ["lin", ""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(lin)\b.*"]

	def get_category_regexpr_exclude(self):
		return [r".*\b(timers?)\b.*"]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 32:
			return GenericCategory.ERROR
		if nb and nb > 10:
			return GenericCategory.WARNING
		return GenericCategory.PASS

class CategoryCAN(GenericFeatureCategory):

	def get_feature_regexpr(self):
		return [["can", "ecan"], ["can", "ecan", ""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(can|ecan)(?!.*buffers)\b.*"]

	def get_category_regexpr_exclude(self):
		return [r".*\b(timers?)\b.*"]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 32:
			return GenericCategory.ERROR
		if nb and nb > 10:
			return GenericCategory.WARNING
		return GenericCategory.PASS

class CategoryI2S(GenericFeatureCategory):

	def get_feature_regexpr(self):
		return [["i2s", "iis"], ["i2s", "iis", ""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(i2s|iis)\b.*"]

	def get_category_regexpr_exclude(self):
		return [r".*\b(timers?)\b.*"]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 32:
			return GenericCategory.ERROR
		if nb and nb > 10:
			return GenericCategory.WARNING
		return GenericCategory.PASS

class CategoryQEI(GenericFeatureCategory):

	def get_feature_regexpr(self):
		return [["qei"], ["qei", ""]]

	def get_category_regexpr(self):
		return [other_features_regexpr, r".*\b(qei|quadrature\s*encoder|quadrature\s*decoder)\b.*"]

	def get_category_regexpr_exclude(self):
		return [r".*\b(timers?)\b.*"]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 32:
			return GenericCategory.ERROR
		if nb and nb > 10:
			return GenericCategory.WARNING
		return GenericCategory.PASS

class CategoryCrypto(GenericFeatureExtendedCategory):

	translation_table = [[
		# value | features | [regular expression] | [class name]
		["aes", ["aes"], r".*\b(aes)\b.*"],
		["des", ["des"], r".*\b(des)\b.*"],
		["ecc", ["ecc"]],
		["sha", ["sha"], r".*\b(sha)\b.*"],
		["md5", ["md5"], r".*\b(md5)\b.*"]
	]]

	def get_category_regexpr(self):
		return [r".*\b(crypto).*"]

	def get_feature_regexpr(self):
		return [[""]]

class CategoryCryptoType(GenericFeatureExtendedSubCategory):
	config_parent_category = CategoryCrypto

class CategoryRNG(GenericBinaryFeatureCategory):

	def get_feature_regexpr(self):
		return [["random", "rng"], [""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(random|rng)\b.*"]

class CategoryTamper(GenericFeatureCategory):

	def get_feature_regexpr(self):
		return [["tamper"], [""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(tamper)\b.*"]

class CategoryUSB(GenericFeatureExtendedCategory):

	config_nb_values = 4
	translation_table = [[
		["ls", ["low\s*speed", "ls"]],
		["fs", ["full\s*speed", "fs"]],
		["hs", ["high\s*speed", "hs"]],
		["ss", ["super\s*speed", "ss"]],
	], [
		["usb 1.0", ["usb\s*1\.0"]],
		["usb 2.0", ["usb\s*2\.0"]],
		["usb 3.0", ["usb\s*3\.0"]],
	], [
		["device", ["device", "d"]],
		["host", ["host", "h"]],
		["otg", ["otg"]],
	]]

	config_merge_options = {
		'list_rules': [
			# If the item has 0 USB, fill the rest with a dash
			{'pattern': ['0', r'^[0\-]?$', r'^[0\-]?$', r'^[0\-]?$'], 'fill': ['0', '-', '-', '-']},
			# If there is at least one non null attribute and the nb peripherals is empty, set it to yes
			{'pattern': [r'^0?$', r'[^-0]+'], 'fill': ['yes']},
			{'pattern': [r'^0?$', None, r'[^-0]+'], 'fill': ['yes']},
			{'pattern': [r'^0?$', None, None, r'[^-0]+'], 'fill': ['yes']},
		]
	}

	def get_category_regexpr(self):
		return [r".*\b(usb).*"]

	def get_feature_regexpr(self):
		return [["usb"]]

	def sanity_check(self, value):
		nb = to_number(value[0])
		if nb and nb > 10:
			return GenericCategory.ERROR
		if nb and nb > 5:
			return GenericCategory.WARNING

class CategoryUSBPeripheral(GenericSubFeatureCategory):
	config_value_index = 0
	config_parent_category = CategoryUSB

	def get_feature_regexpr(self):
		return [["usb"], ["usb", ""], ["usb", ""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*(usb.*periph).*", r"^(usb)$"]

	def get_category_regexpr_exclude(self):
		return [r".*\b(timers?)\b.*"]

class CategorySegmentLCD(GenericCategory):
	config_resolution = 0
	config_multiple_categories = True

	@classmethod
	def get_type(cls):
		return [cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE | cls.TYPE_EXT_BINARY]

	def get_category_regexpr(self):
		return [other_features_regexpr, r".*\b(lcd)\b(?!.*pump).*"]

	def get_category_regexpr_exclude(self):
		return [r".*\b(timers?|graphics?)\b.*"]

	def parse(self, string):
		value = ""
		if self.get_global_config("category_regex_index") == 0:
			value = self.parse_feature(string, ["segment\s*display", "lcd"])
		else:
			values = self.parse_format(string, ["@n0[x\\*]@n1"])
			if len(values):
				value = str(int(values[0][0]) * int(values[0][1]))
			else:
				value = self.parse_number(string)
				if value == "":
					value = self.parse_binary(string)
		self.set_value(self.format_value(value))

class CategoryGraphicsController(GenericFeatureCategory):

	def get_category_regexpr(self):
		return [other_features_regexpr, r".*\b(graphics?)\b.*"]

	def get_feature_regexpr(self):
		return [["graphics?"], [""]]

	def get_category_regexpr_exclude(self):
		return [r".*\b(segment).*"]

class CategoryCamera(GenericBinaryFeatureCategory):

	def get_feature_regexpr(self):
		return [["camera"], ["camera", ""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(camera)\b.*"]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 2:
			return GenericCategory.ERROR
		if nb and nb > 1:
			return GenericCategory.WARNING
		return GenericCategory.PASS

class CategoryEBI(GenericFeatureExtendedCategory):
	config_binary = True

	translation_table = [[
		# value | features | [regular expression] | [class name]
		["sram", ["sram"], r".*\b(sram).*"],
		["sdram", ["sdram"], r".*\b(sdram).*"],
		["nand", ["nand"], r".*\b(nand).*"],
		["nor", ["nor"], r".*\b(nor).*"],
		["ddr1", ["ddr1"], r".*\b(ddr1).*"],
		["ddr2", ["ddr2"], r".*\b(ddr2).*"],
		["ddr3", ["ddr3"], r".*\b(ddr3).*"],
		["lpddr", ["lpddr"], r".*\b(lpddr).*"]
	]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(ebi|epi|emi|external\s*bus|parallel\s*port)\b.*"]

	def get_category_regexpr_exclude(self):
		return [r".*\b(timers?)\b.*"]

	def get_feature_regexpr(self):
		return [["ebi", "epi", "emi"], ["ebi", "epi", "emi", ""]]

	def sanity_check(self, value):
		nb = to_number(value[0])
		if nb and nb > 2:
			return GenericCategory.ERROR
		if nb and nb > 1:
			return GenericCategory.WARNING
		return GenericCategory.PASS

class CategoryEBIType(GenericFeatureExtendedSubCategory):
	config_parent_category = CategoryEBI

class CategoryMCI(GenericBinaryFeatureCategory):

	def get_feature_regexpr(self):
		return [["sdio", "hsmci", "mci", "mmc", "sdhc"], ["sdio", "hsmci", "mci", "mmc", "sdhc", ""]]

	def get_category_regexpr(self):
		return [serial_peripheral_regexpr, r".*\b(sdio|mmc|sd\s*card|mci|sdhc)\b.*"]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 2:
			return GenericCategory.ERROR
		if nb and nb > 1:
			return GenericCategory.WARNING
		return GenericCategory.PASS

class CategoryEthernet(GenericMultiCategory):
	config_resolution = 0
	config_multiple_categories = True
	config_nb_values = 2
	config_merge_strategy = MERGE_STRATEGY_REPLACE | MERGE_CONCATENATE
	config_merge_with_original_strategy = MERGE_STRATEGY_REPLACE | MERGE_CONCATENATE

	config_merge_options = {
		'list_rules': [
			# If the item has 0 ethernet, fill the rest with a dash
			{'pattern': ['0', r'^[0\-]?$'], 'fill': ['0', '-']},
			# If there is at least one non null attribute and the nb peripherals is empty, set it to yes
			{'pattern': [r'^0?$', r'[^-0]+'], 'fill': ['yes']}
		]
	}

	@classmethod
	def get_type(cls):
		return [
			cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE | cls.TYPE_EXT_BINARY, # Nb peripherals
			cls.TYPE_STRING,                                                # 10/100/1000/10G
		]

	def get_category_regexpr(self):
		return [ r".*\b(ethernet)\b.*" ]

	def parse(self, string):
		nb_peripherals = ""
		type = ""

		# Update the type
		if re.match(r".*\b/?(10)/?\b.*", string.lower()):
			type = merge_strings(type, "10", strategy = MERGE_STRATEGY_REPLACE | MERGE_CONCATENATE)
		if re.match(r".*\b/?(100)/?\b.*", string.lower()):
			type = merge_strings(type, "100", strategy = MERGE_STRATEGY_REPLACE | MERGE_CONCATENATE)
		if re.match(r".*\b/?(1000|1\s*g)/?\b.*", string.lower()):
			type = merge_strings(type, "1000", strategy = MERGE_STRATEGY_REPLACE | MERGE_CONCATENATE)
		if re.match(r".*\b/?(10000|10\s*g)/?\b.*", string.lower()):
			type = merge_strings(type, "10G", strategy = MERGE_STRATEGY_REPLACE | MERGE_CONCATENATE)

		# If the type is defined, then there is at least 1 peripheral
		if type != "":
			nb_peripherals = "yes"
		# Look if this is a binary value
		else:
			nb_peripherals = self.parse_binary(string)

		self.set_value(self.format_value([nb_peripherals, type]))

class CategoryEthernetPeripheral(GenericSubFeatureCategory):
	config_value_index = 0
	config_parent_category = CategoryEthernet

	def get_feature_regexpr(self):
		return [["ethernet"], ["ethernet"], ["ethernet", ""]]

	def get_category_regexpr(self):
		return [other_features_regexpr, serial_peripheral_regexpr, r".*\b(ethernet)\b.*"]

	def get_category_regexpr_exclude(self):
		return [r".*\b(timers?)\b.*"]
