#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from generic import *
from mculib.log import *
import re
import time
from urlparse import urljoin

generic_categories = r".*(system.*feature|peripheral|other|additional.*feature).*"

class CategoryDiscovered(GenericCategory):
	"""
	This function tells how the device has been discovered.
	"""
	config_always_update = True
	config_silent = True
	config_translation_table = [
		[ r".*(auto).*", "automatic" ],
		[ r".*(manual).*", "manual" ],
	]

class CategoryDeviceName(GenericCategory):

	@classmethod
	def get_type(cls):
		return [cls.TYPE_STRING]

	def get_category_regexpr(self):
		return [r".*(product|part.*number|part.*name|device.*name).*", r"^(devices?)$"]

	def get_category_regexpr_exclude(self):
		return [r".*(status|description|link|order|newly|intro|rapid|growth|photo|training|module|page|specification).*"]

	def parse(self, string):
		# Remove ()
		string = re.sub(r"\([^\)]*\)", "", string.lower())
		# Remove / or \\
		string = re.sub(r"[\\/,;\.]+", "-", string.lower())
		# Remove spaces at the begining and end
		string = string.strip()
		# Keep only a certain type of characters, if
		result = re.split('[^a-z0-9\s_-]', string, flags=re.IGNORECASE)
		string = result[0]
		self.set_value(string)

class CategoryAlias(GenericCategory):
	"""
	This is a special value that will not be saved as it is.
	This category tells if a device is an alias of another, when merged this device
	will hen be merged with its parent.
	"""
	pass

class CategoryGenericURL(GenericCategory):
	base_url = ""
	config_case_sensitive = True

	@classmethod
	def get_type(cls):
		return [cls.TYPE_URL]

	@classmethod
	def set_base_url(cls, base_url):
		cls.base_url = base_url

	def parse(self, string):
		# Get the URL out of a string
		url_list = re.findall('(?:http[s]?|ftp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
		# look if this is a tag
		if len(url_list) == 0:
		        url_list = re.findall(r"href\s*=\s*[\"\']([^\"\']*)", string)
		# Look if this is a partial URL
		if len(url_list) == 0:
			url_list = re.findall('(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
		if len(url_list) > 0:
			# URl
			url = url_list[0]
			# Make sure this is not one of the banned value
			if not re.match(r"\s*(-)\s*$", url):
				# Check if the base URL should be append
				if not re.match('^(?:http[s]?|ftp)://', url):
					url = urljoin(self.base_url, url)
				self.set_value(url)

class CategoryDatasheet(CategoryGenericURL):
	def get_category_regexpr(self):
		return [r"(datasheet)"]

class CategoryWebPage(CategoryGenericURL):
	def get_category_regexpr(self):
		return [r"(url)"]

class CategoryOrderPage(CategoryGenericURL):
	# This value is kept for the alias
	config_alias_delete_if_duplicate = False
	# Don't merge this value to the alias
	config_alias_merge_with_mcu = False
	def get_category_regexpr(self):
		return [r"(order)"]

class CategoryLaunchDate(GenericCategory):
	"""
	This category keeps the date of the product launch
	"""
	# This value is kept for the alias
	config_alias_delete_if_duplicate = False
	# Don't merge this value to the alias
	config_alias_merge_with_mcu = False

	@classmethod
	def get_type(cls):
		return [cls.TYPE_DATE]

	@classmethod
	def parse_date(self, string):
		string = string.strip()
		if not string:
			return None
		string = string.replace('/',' ').replace('-',' ').replace(',',' ')

		# With year, month, day
		for format in [ '%d %m %Y', '%Y %m %d', '%d %B %Y', '%B %d %Y',
				'%d %b %Y', '%b %d %Y', '%d %m %y', '%y %m %d',
				'%d %B %y', '%B %d %y', '%d %b %y', '%b %d %y']:
			try:
				return time.strptime(string, format)
			except ValueError:
				pass
		# With month and year
		for format in [ '%m %Y', '%Y %m', '%m %y',
				'%Y %B', '%B %Y', '%Y %b', '%b %Y',
				'%y %B', '%B %y', '%b %y', '%b %y']:
			try:
				return time.strptime(string, format)
			except ValueError:
				pass
		# With day and month
		for format in ['%d %B', '%B %d', '%d %b', '%b %d']:
			try:
				return time.strptime(string, format)
			except ValueError:
				pass
		raise error("Unable to parse the date `%s'." % (str(string)), self)


	def parse(self, string):
		time_tuple = self.parse_date(string)
		date_str = time.strftime("%Y-%m", time_tuple)
		self.set_value(date_str)

class CategoryDeviceManufacturer(GenericCategory):

	@classmethod
	def get_type(cls):
		return [cls.TYPE_STRING]

	def get_category_regexpr(self):
		return [r".*(product|device|part).*(manufacturer).*", r"^(manufacturer?)$"]

class CategoryDeviceFamily(GenericCategory):

	@classmethod
	def get_type(cls):
		return [cls.TYPE_STRING]

	def get_category_regexpr(self):
		return r"^(sub[-\s]?family)$"

	def parse(self, string):
		# Remove some words
		string = re.sub(r"\b(series?|family|families)\b", "", string.lower())
		self.set_value(string)

class CategoryDeviceTopFamily(GenericCategory):

	@classmethod
	def get_type(cls):
		return [cls.TYPE_STRING]

	def get_category_regexpr(self):
		return r"^(family)$"

	def get_category_regexpr_exclude(self):
		return [r".*(sub).*"]

	def parse(self, string):
		# Remove some words
		string = re.sub(r"\b(series?|family|families)\b", "", string.lower())
		self.set_value(string)

class CategoryUniqueID(GenericBinaryFeatureCategory):
	def get_feature_regexpr(self):
		return [["id", ""]]

	def get_category_regexpr(self):
		return [r".*\b(unique\s+id)\b.*"]

class CategoryRegulator(GenericBinaryFeatureCategory):
	def get_feature_regexpr(self):
		return [["regulator", "reg", ""]]

	def get_category_regexpr(self):
		return [r".*\b(regulator)\b.*"]

class CategoryRegulatorVoltageScaling(GenericBinaryFeatureCategory):
	def get_feature_regexpr(self):
		return [["volatge\s+scaling", ""]]

	def get_category_regexpr(self):
		return [r".*\b(volatge\s+scaling)\b.*"]

class CategoryMPU(GenericBinaryFeatureCategory):
	def get_feature_regexpr(self):
		return [["mpu", ""]]

	def get_category_regexpr(self):
		return [r".*\b(mpu|memory\s*protection\s*unit)\b.*"]

class CategoryLegacy(GenericBinaryFeatureCategory):
	def get_feature_regexpr(self):
		return [[""]]

class CategoryHidden(GenericBinaryFeatureCategory):
	def get_feature_regexpr(self):
		return [[""]]

class CategoryDeviceStatus(GenericCategory):

	config_translation_table = [
		[ r".*(production|active|available|new).*", "production" ],
		[ r".*(future|announced|preview|proposal|target|development|qualification).*", "announced" ],
		[ r".*(sampl|evaluation).*", "sampling" ],
		[ r".*(mature|eof|end.*life|nrnd|not.*recomm[ae]nded|no.*longer.*manufactured|obsolete).*", "mature" ],
		[ r"\s*", "" ],
	]

	def get_category_regexpr(self):
		return r"(.*status.*)"

class CategoryPricing(GenericMultiListCategory):

	# Defines which values are important when we merging
	config_merge_options = {
		'conflict': [0, 0, 1]
	}

	# Do not merge the pricing with the parent
	config_alias_merge_with_mcu = False

	config_always_update = True
	config_resolution = 0
	config_nb_values = 3
	price_regexpr = r"(?i)(\$|€|usd|euro)"
	volume_regexpr = r"(?i)(u|units?|(?<=k|m))\b"
	# Allow multiple categories
	config_multiple_categories = True

	config_translation_table = [
		None,
		[["usd", "$"], ["euro", "€"]],
		None
	]

	@classmethod
	def get_type(cls):
		return [
			cls.TYPE_DECIMAL | cls.TYPE_EXT_POSITIVE | cls.TYPE_EXT_NOT_NULL, # Price
			cls.TYPE_ANY,                                                     # Currency
			cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE | cls.TYPE_EXT_NOT_NULL, # Volume
		]

	def get_category_regexpr(self):
		return ".*(price|pricing).*"

	def get_fixed_value_regexpr(self):
		price_regexpr = r"@e1" + self.price_regexpr
		volume_regexpr = r"@n2{px}" + self.volume_regexpr
		return [price_regexpr + ".*" + volume_regexpr, volume_regexpr + ".*" + price_regexpr, price_regexpr, volume_regexpr]

	def parse(self, string):
		# Parse known formats
		(values, string) = self.parse_list_format(string, [
				"@n2{ipx}@,\@@,US@e1" + self.price_regexpr + "@n0{pd2}" # 10000 @ US$6.02
			])
		# If it outputs nothing try something else
		if len(values) == 0:
			(values, string) = self.parse_list(string, [r"@n0{pd2}", r"@e0" + self.price_regexpr, r"@n0{px}" + self.volume_regexpr])
		# Set the result
		self.set_value(values)

class CategoryPricingDigiKey(CategoryPricing):
	def get_category_regexpr(self):
		return None

class CategoryDMA(GenericFeatureCategory):

	# There will not be different appelation for DMAs inside the same prodcut (most likely), this has caused issues with Freescale.
	config_merge_strategy = MERGE_STRATEGY_MAX

	def get_feature_regexpr(self):
		return [["dma", "ch", ""]]

	def get_category_regexpr(self):
		return [r".*\b(dma|direct.*memory.*access)\b.*(?!ram)"]

class CategoryInternalOscillator(GenericMultiListCategory):

	config_resolution = 0
	config_nb_values = 2

	@classmethod
	def get_type(cls):
		return [
			CategoryInternalOscillatorFrequency.get_type()[0],	# Frequency
			CategoryInternalOscillatorAccuracy.get_type()[0]	# Accuracy
		]

	def get_category_regexpr(self):
		return r"(.*internal.*oscillator.*)"

	def parse(self, string):
		(values, string) = self.parse_list(string, [r"@n0{px}hz", r"@n0{p}%"])
		if string:
			sub_values = self.parse_format(string, ["@n0{xp}hz@,@n1{p}%", "@n1{p}%@,@n0{xp}hz", "@n0{xp}hz", "@n0{xp}"])
			values.extend(sub_values)
		self.set_value(values)

class CategoryInternalOscillatorFrequency(GenericBinarySubFeatureCategory):
	config_value_index = 0
	config_parent_category = CategoryInternalOscillator

	@classmethod
	def get_type(cls):
		return [cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE | cls.TYPE_EXT_NOT_NULL]

	def get_feature_regexpr(self):
		return [[""], [""]]

	def get_category_regexpr(self):
		return [r".*hz.*oscillator.*", r"oscillator.*hz.*"]

	def get_fixed_value_regexpr(self):
		return ["@n0{p}[mk]hz"]

class CategoryInternalOscillatorAccuracy(GenericSubCategory):
	config_value_index = 1
	config_parent_category = CategoryInternalOscillator
	config_resolution = 2

	@classmethod
	def get_type(cls):
		return [cls.TYPE_DECIMAL | cls.TYPE_EXT_POSITIVE | cls.TYPE_EXT_NOT_NULL]

	def parse(self, string):
		values = self.parse_format(string, ["@n0{p}%"])
		if values:
			self.set_value(values[0][0])

	def get_category_regexpr(self):
		return r".*oscillator.*accuracy.*"

class CategoryBrownOutDetector(GenericBinaryFeatureCategory):

	def get_feature_regexpr(self):
		return [["bod", "bor", "pbor", "pvd", "brown[\s\-]*out[\s\-]*detect"], ["bod", "bor", "pbor", "pvd", "brown[\s\-]*out[\s\-]*detect", ""]]

	def get_category_regexpr(self):
		return [generic_categories, r".*\b(brown.*out.*detector|brown.*out.*reset|bod|bor|voltage.*detector)\b.*"]

class CategoryPowerOnReset(GenericBinaryFeatureCategory):

	def get_feature_regexpr(self):
		return [["por"], ["por", ""]]

	def get_category_regexpr(self):
		return [generic_categories, r".*\b(power.*on.*reset|por)\b.*"]

class CategoryWatchdog(GenericBinaryFeatureCategory):

	def get_feature_regexpr(self):
		return [["wdt", "wwdt", "wdg", "wwdg"], ["wdt", "wwdt","wdg", "wwdg", ""]]

	def get_category_regexpr(self):
		return [generic_categories, r".*\b(watch\s*dog|wdt|wwdt|wdg|wwdg)\b.*"]

class CategoryCRC(GenericBinaryFeatureCategory):
	def get_feature_regexpr(self):
		return [["crc"], ["crc", ""]]

	def get_category_regexpr(self):
		return [generic_categories, r".*\b(crc)\b.*"]

class CategoryRealTimeClock(GenericBinaryFeatureCategory):
	def get_feature_regexpr(self):
		return [["rtc", "rtcc"], ["rtc", "rtcc", ""]]

	def get_category_regexpr(self):
		return [generic_categories, r"(real.*time.*clock|real.*time.*calendar|rtc|rtcc)\b.*"]

class CategoryHDMICEC(GenericFeatureCategory):
	def get_feature_regexpr(self):
		return [["hdmi-cec", "cec"], ["hdmi-cec", "cec", ""]]

	def get_category_regexpr(self):
		return [r"(serial.*interface)", r".*\b(cec)\b.*"]

class CategoryPWM(GenericFeatureCategory):
	config_merge_strategy = MERGE_STRATEGY_MAX
	config_merge_with_original_strategy = MERGE_STRATEGY_MAX

	def get_feature_regexpr(self):
		return [["pwm", "std\\. pwm", ""]]
	def get_category_regexpr_exclude(self):
		return [r".*(resolution|motion|speed|time).*"]
	def get_category_regexpr(self):
		return [r".*\b(pulse.*width.*modul|pwm).*"]

class CategoryTimer8bit(GenericFeatureCategory):
	# By default the category to choose is the first one
	category_regex_index = 0

	def get_feature_regexpr(self):
		return [["8[- \t]*bit", ""], ["8[- \t]*bit"]]
	def get_category_regexpr_exclude(self):
		return [r".*16[- \t]*bit.*", r".*32[- \t]*bit.*"]
	def get_category_regexpr(self):
		return [r".*\b(8[- \t]*bit.*timers?)\b.*", r".*\b(timers?)\b.*"]

class CategoryTimer16bit(GenericFeatureCategory):
	# By default the category to choose is the first one
	category_regex_index = 0

	def get_feature_regexpr(self):
		return [["16[- \t]*bit", ""], ["16[- \t]*bit"]]
	def get_category_regexpr_exclude(self):
		return [r".*8[- \t]*bit.*", r".*32[- \t]*bit.*"]
	def get_category_regexpr(self):
		return [r".*\b(16[- \t]*bit.*timers?)\b.*", r".*\b(timers?)\b.*"]

class CategoryTimer32bit(GenericFeatureCategory):
	# By default the category to choose is the first one
	category_regex_index = 0

	def get_feature_regexpr(self):
		return [["32[- \t]*bit", ""], ["32[- \t]*bit"]]
	def get_category_regexpr_exclude(self):
		return [r".*8[- \t]*bit.*", r".*16[- \t]*bit.*"]
	def get_category_regexpr(self):
		return [r".*\b(32[- \t]*bit.*timers?)\b.*", r".*\b(timers?)\b.*"]

class CategoryTouchChannel(GenericFeatureCategory):
	def get_feature_regexpr(self):
		return [["channels", "ch", "chs"], ["channels", "ch", "chs", ""]]
	def get_category_regexpr(self):
		return [r"^\S*(touch)\S*$", r".*(touch).*(channel).*"]
	def get_category_regexpr_exclude(self):
		return [r".*resistive.*"]

class CategoryPackaging(GenericCategory):
	"""
	This function the packaging type of the device
	"""
	# This value is kept for the alias
	config_alias_delete_if_duplicate = False
	# Don't merge this value to the alias
	config_alias_merge_with_mcu = False

	def get_category_regexpr(self):
		return [r".*(packaging).*"]

	config_translation_table = [
		[ r".*(tape.*reel).*", "tape&reel" ],
		[ r".*(cut.*tape).*", "tape" ],
		[ r".*(tray).*", "tray" ],
		[ r".*(tube).*", "tube" ],
		[ r".*", "" ]
	]

class CategoryPin(GenericFeatureCategory):
	# This value is kept for the alias
	config_alias_delete_if_duplicate = False

	def get_feature_regexpr(self):
		return [["pins?", ""], ["pins?"]]
	def get_category_regexpr(self):
		return [r".*\b(number.*pins?|pin.*count)\b.*", r".*\b(pins?)\b.*"]
	def get_category_regexpr_exclude(self):
		return [r".*5v.*", r".*volt.*", r".*i[/|]?o.*"]

class CategoryPackage(GenericMultiListCategory):
	config_resolution = 0
	config_nb_values = 5
	# Following package types should be banned
	banned_list = [ "mil", "ball" ]
	# These packages will be replaced by others
	package_translation_table = []
	# This value is kept for the alias
	config_alias_delete_if_duplicate = False
	# Add the value if if no trust for the packages
	config_merge_trust_strategy = MERGE_STRATEGY_FILL
	# Allow multiple categories
	config_multiple_categories = True

	# Translation table on the package name
	config_translation_table = [
		None,
		[
			[ r".*(qfn|mlf).*", "qfn" ],
			[ r".*(dfn).*", "dfn" ],
			[ r".*(dip).*", "pdip" ],
			[ r".*(map|lga|bga).*", "bga" ],
			[ r".*(qfp).*", "qfp" ],
			[ r".*(tssop).*", "tssop" ],
			[ r".*(ssop).*", "ssop" ],
			[ r".*(soic).*", "soic" ],
			[ r".*(sot).*", "sot23" ],
			[ r".*(?<![a-z])(so)(?![a-z]).*", "soic" ],
			[ r".*(csp).*", "wlcsp" ],
			[ r".*(lcc|plcc).*", "lcc" ],
		]
	]

	@classmethod
	def get_type(cls):
		return [
			cls.TYPE_INTEGER | cls.TYPE_EXT_NOT_NULL | cls.TYPE_EXT_POSITIVE, # Number of pins
			cls.TYPE_STRING,                                                  # Package type
			cls.TYPE_DECIMAL | cls.TYPE_EXT_NOT_NULL | cls.TYPE_EXT_POSITIVE, # Width
			cls.TYPE_DECIMAL | cls.TYPE_EXT_NOT_NULL | cls.TYPE_EXT_POSITIVE, # Height
			cls.TYPE_DECIMAL | cls.TYPE_EXT_NOT_NULL | cls.TYPE_EXT_POSITIVE  # Depth
		]

	@classmethod
	def set_package_translation_table(cls, package_translation_table):
		cls.package_translation_table = package_translation_table

	def get_category_regexpr(self):
		return r".*\b(package|packages)\b.*"

	def get_category_regexpr_exclude(self):
		return [r".*(temperature|version).*"]

	def parse(self, string):

		# Make a string of the custom package to add
		custom_package = ""
		for package in self.package_translation_table:
			custom_package = custom_package + package[0] + "|"

		string = string.lower()
		package_match_regexpr = "\w*(?:" + custom_package + "bga|lga|pga|qfp|cfp|qfn-s|qfn|dip|sop|soic-[0-9]+|soic|dfn|csp|sot-?[0-9]+|sot|vlap|vftla|vtla|so-[0-9]+|so|plcc|lcc|wafer|map|mlf)\w*"
		regexpr_pins = "(?<![\*x])@n0{ip}(?![\*a-zA-Z])(?:-?pins?)?"
		regexpr_package = "@e1(" + package_match_regexpr + ")"
		regexpr_size = "\(?@n2\s*[\*x]\s*@n3\s*[\*x]?\s*@n4?\)?"
		(values, string) = self.parse_list_format(string, [
				regexpr_pins + "[-/]" + regexpr_package + "[:]?@," + regexpr_size, # 64/TQFP 3x3x1.2
				regexpr_package + "[-/]" + regexpr_pins + "[:]?@," + regexpr_size, # TQFP/64 3x3x1.2
				regexpr_pins + "@," + regexpr_package + "[:]?@," + regexpr_size, # 64 TQFP 3x3x1.2
				regexpr_package + "@," + regexpr_pins + "[:]?@," + regexpr_size, # TQFP 64 3x3x1.2
				regexpr_pins + "[-/]" + regexpr_package, # 64/TQFP
				regexpr_package + "[-/]" + regexpr_pins, # TQFP/64
				regexpr_pins + "@," + regexpr_package, # 64 TQFP
				regexpr_package + "@," + regexpr_pins, # TQFP 64
				regexpr_pins + regexpr_package + "[:]?@," + regexpr_size, # 64TQFP 3x3x1.2
				regexpr_package + regexpr_pins + "[:]?@," + regexpr_size, # TQFP64 3x3x1.2
				"(?<![\*a-zA-Z])@n0{ip}" + regexpr_package + "[:]?@," + regexpr_size, # 64TQFP  3x3x1.2
				"(?<![\*a-zA-Z])@n0{ip}" + regexpr_package, # 64TQFP
				"@e1((?:sot|soic)-?[0-9]+)",    # SOT-23
				regexpr_package + "@n0{ip}(?![\*a-zA-Z])", # TQFP64
			])

		# Special case remove some specific pattern
		string = re.sub(r"die\s+[0-9]+", "", string)

		# If there is a left over
		if string:
			regexpr_package = "@e0(" + package_match_regexpr + ")"
			(new_values, string) = self.parse_list(string, [regexpr_pins, regexpr_package])
			values = merge_lists(values, new_values)

		# Ban list
		for banned_regexpr in self.banned_list:
			for value in values:
				if re.match(banned_regexpr, value[1].lower()):
					values.remove(value)

		for package in values:
			# Translation table
			new_package_type = self.parse_translation_table(package[1], self.package_translation_table)
			if new_package_type:
				package[1] = new_package_type
			# Update the pin count on some specific packages
			pin_count = self.parse_format(package[1], ["(?:qfn|so)-?@n0{i}"])
			if pin_count:
				package[0] = pin_count[0][0]
			# Remove any numbers from the package name of some packages
			if re.match(r".*(wafer).*", package[1]):
				package[1] = re.sub(r"[0-9]", "", package[1])
			# Remove the 0 pin count for some packages
			if re.match(r".*(wafer).*", package[1]) and package[0] == "0":
				package[0] = ""
			# Remove the pin count of the package name if it is located at the begining or at the end
			if is_number(package[0]):
				package[1] = re.sub("^" + package[0], "", package[1])
				package[1] = re.sub(package[0] + "$", "", package[1])
				package[1] = package[1].strip('-')

		# Set the value
		self.set_value(values)

	def sanity_check(self, value, complete_list):

		# Make sure all packages have at least 2 pins
		if value[0] and to_number(value[0]) < 2:
			return GenericCategory.ERROR

		# Make sure all packages type are not empty and are at least 2 character long
		if len(value[1]) < 2:
			return GenericCategory.ERROR

		# Make sure all package length are approximately the same
		package_size_min = 9999999
		package_size_max = 0
		for v in complete_list:
			size = to_number(v[0])
			if size != None and size < package_size_min:
				package_size_min = size
			if size != None and size > package_size_max:
				package_size_max = size
		if package_size_max >= 150 and package_size_max > (package_size_min * 4):
			self.info(complete_list, 0)
			return GenericCategory.ERROR

		return GenericCategory.PASS

class CategorySpecialFeature(GenericListCategory):
	config_multiple_categories = True

	@classmethod
	def get_type(cls):
		return [cls.TYPE_STRING]

	def parse(self, string):
		values = self.parse_format(string, ["@e0([^,;\n/\.]+)", "@s0"])
		feature_list = []
		for v in values:
			feature_list.append(self.format_value(v[0]))
		self.set_value(feature_list)
