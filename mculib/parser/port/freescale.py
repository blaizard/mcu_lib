#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from mculib.parser.generic import *
from mculib.parser.deep import *
from bs4 import BeautifulSoup
import re
import HTMLParser
import xml.sax.saxutils

class REMatcher(object):
    def __init__(self, matchstring):
        self.matchstring = matchstring

    def match(self, regexp):
        self.rematch = re.match(regexp, self.matchstring)
        return bool(self.rematch)

    def group(self,i):
        return self.rematch.group(i)

class FreescaleCommon(GenericParserPort):

	@staticmethod
	def get_manufacturer():
		return "freescale"

	@staticmethod
	def check_device(mcu, db):
		"""
		This function is called to check devices and clean up info about a certain device.
		It is also used to set specific info on a device with its name and other paramters.
		"""
		# Ignore hidden devices
		if db.get_item_param_value(mcu, "CategoryHidden") == "yes":
			return

		mcu_name = db.get_name(mcu)
		# Default attributes
		attr = {}
		# Known package list identifier
		package_list = {
			"fg": ["16", "qfn"],
			"tg": ["16", "tssop"],
			"wj": ["20", "soic"],
			"af": ["20", "wlcsp"],
			"fk": ["24", "qfn"],
			"lc": ["32", "qfp"],
			"fm": ["32", "qfn"],
			"ad": ["35", "wlcsp"],
			"ld": ["44", "qfp"],
			"hh": ["44", "bga"],
			"ft": ["48", "qfn"],
			"lf": ["48", "qfp"],
			"qh": ["64", "qfp"],
			"lh": ["64", "qfp"],
			"mp": ["64", "bga"],
			"lk": ["80", "qfp"],
			"mb": ["81", "bga"],
			"ll": ["100", "qfp"],
			"ml": ["104", "bga"],
			"ab": ["120", "wlcsp"],
			"mc": ["121", "bga"],
			"dc": ["121", "bga"],
			"aa": ["143", "wlcsp"],
			"lq": ["144", "qfp"],
			"md": ["144", "bga"],
			"mj": ["256", "bga"]
		}
		package_list_regexpr = "|".join(package_list.keys())
		temperature = "[vcm]?"
		revision = "[zab]?"
		cpu = "[zdfc]?"
		nvm = "[0-9]+m?0?"
		# Parse the name and look for parameters
		# Check if the name matches this specific Kinetis device name scheme
		m = REMatcher(mcu_name)
		# Kinetis K
		if m.match(r"^([mp])(k[0-9]+)(" + cpu + ")([nx])(" + nvm + ")(" + revision + ")(" + temperature + ")(" + package_list_regexpr + ")([0-9]+)(r?)$"):
			attr["top_family"] = "kinetis k"
			attr["qualification"] = m.group(1)
			attr["family"] = m.group(2)
			attr["cpu"] = m.group(3)
			attr["nvm"] = m.group(5)
			attr["revision"] = m.group(6)
			attr["temperature"] = m.group(7)
			attr["package"] = m.group(8)
			attr["speed"] = m.group(9)
			pcn = "m" + m.group(2) + attr["cpu"] + m.group(4) + attr["nvm"] + attr["package"] + attr["speed"]
		# Kinetis EA
		elif m.match(r"^([sp])9(kea)(" + cpu + ")(n?)(" + nvm + ")(" + revision + ")(" + temperature + ")(" + package_list_regexpr + ")(r?)$"):
			attr["top_family"] = "kinetis ea"
			attr["qualification"] = m.group(1)
			attr["family"] = m.group(2)
			attr["cpu"] = m.group(3)
			attr["can"] = m.group(4)
			attr["nvm"] = m.group(5)
			attr["revision"] = m.group(6)
			attr["temperature"] = m.group(7)
			attr["package"] = m.group(8)
		# Kinetis E
		elif m.match(r"^([mp])(ke[0-9]+)(" + cpu + ")(" + nvm + ")(" + revision + ")(" + temperature + ")(" + package_list_regexpr + ")([0-9]+)(r?)$"):
			attr["top_family"] = "kinetis e"
			attr["qualification"] = m.group(1)
			attr["family"] = m.group(2)
			attr["cpu"] = m.group(3)
			attr["nvm"] = m.group(4)
			attr["revision"] = m.group(5)
			attr["temperature"] = m.group(6)
			attr["package"] = m.group(7)
			attr["speed"] = m.group(8)
		# Kinetis L
		elif m.match(r"^([mp])(kl[0-9]+)(" + cpu + ")(" + nvm + ")(" + revision + ")(" + temperature + ")(" + package_list_regexpr + ")([0-9]+)(r?)$"):
			attr["top_family"] = "kinetis l"
			attr["qualification"] = m.group(1)
			attr["family"] = m.group(2)
			attr["cpu"] = m.group(3)
			attr["nvm"] = m.group(4)
			attr["revision"] = m.group(5)
			attr["temperature"] = m.group(6)
			attr["package"] = m.group(7)
			attr["speed"] = m.group(8)
		# Kinetis M
		elif m.match(r"^([mp])(km[0-9])([0-9])(" + cpu + ")(" + nvm + ")(" + temperature + ")(" + package_list_regexpr + ")([0-9]+)(r?)$"):
			attr["top_family"] = "kinetis m"
			attr["qualification"] = m.group(1)
			attr["family"] = m.group(2)
			if attr["family"] == "km3":
				attr["lcd"] = "yes"
			attr["sdadc"] = m.group(3)
			attr["revision"] = m.group(4)
			attr["nvm"] = m.group(5)
			attr["temperature"] = m.group(6)
			attr["package"] = m.group(7)
			attr["speed"] = m.group(8)
		# Kinetis V
		elif m.match(r"^([mp])(kv[0-9])[0-9](" + cpu + ")(" + nvm + ")(" + revision + ")(" + temperature + ")(" + package_list_regexpr + ")([0-9]+)(r?)$"):
			attr["top_family"] = "kinetis v"
			attr["qualification"] = m.group(1)
			attr["family"] = m.group(2) + "x"
			attr["cpu"] = m.group(3)
			attr["nvm"] = m.group(4)
			attr["revision"] = m.group(5)
			attr["temperature"] = m.group(6)
			attr["package"] = m.group(7)
			attr["speed"] = m.group(8)
		else:
			db.warning("The device name `%s' did not match any of the known part identification." % (mcu_name))

		# This array will contain the new values to be set
		value_list = {}

		# Set the device top family
		if attr.has_key("top_family"):
			value_list["CategoryDeviceTopFamily"] = attr["top_family"]
		# Set the device family
		if attr.has_key("family"):
			value_list["CategoryDeviceFamily"] = attr["family"]
		# Set the CPU core
		if attr.has_key("cpu") and attr["cpu"] != "":
			if attr["cpu"] == "z":
				value_list["CategoryCPUCore"] = "cortexm0+"
			elif attr["cpu"] == "d":
				value_list["CategoryCPUCore"] = "cortexm4"
			elif attr["cpu"] == "c":
				value_list["CategoryCPUCore"] = "cortexm4"
			elif attr["cpu"] == "f":
				value_list["CategoryCPUCore"] = "cortexm4f"
			else:
				db.warning("Unknown CPU core identifier `%s' for `%s'." % (attr["cpu"], mcu_name))
		# Set the device CAN
		if attr.has_key("can") and attr["can"] == "n":
			value_list["CategoryCAN"] = "yes"
		# Set the device LCD
		if attr.has_key("lcd") and attr["lcd"] == "yes":
			value_list["CategorySegmentLCD"] = "yes"
		# Set the device number of SD ADCs
	#	if attr.has_key("sdadc"):
	#		if attr["sdadc"] == "1":
	#			value_list["CategoryADC"] = []
	#		value_list["CategorySegmentLCD"] = "yes"
		# NVM size
		if attr.has_key("nvm"):
			if is_number(attr["nvm"]):
				value_list["CategoryMemoryFlash"] = to_number(attr["nvm"]) * 1024
			elif attr["nvm"] == "1m0":
				value_list["CategoryMemoryFlash"] = 1024 * 1024
			elif attr["nvm"] == "2m0":
				value_list["CategoryMemoryFlash"] = 2 * 1024 * 1024
			else:
				db.warning("Cannot identify the flash size from `%s' for `%s'." % (attr["nvm"], mcu_name))
		# Check the temperature
		if attr.has_key("temperature") and attr["temperature"] != "":
			if attr["temperature"] == "v":
				value_list["CategoryMinTemperature"] = "-40"
				value_list["CategoryMaxTemperature"] = "105"
			elif attr["temperature"] == "c":
				value_list["CategoryMinTemperature"] = "-40"
				value_list["CategoryMaxTemperature"] = "85"
			elif attr["temperature"] == "m":
				value_list["CategoryMinTemperature"] = "-40"
				value_list["CategoryMaxTemperature"] = "125"
			else:
				db.warning("Unknown temperature range `%s' for `%s'." % (attr["temperature"], mcu_name))
		# Package code
		if attr.has_key("package"):
			if package_list.has_key(attr["package"]):
				value_list["CategoryPackage"] = [package_list[attr["package"]]]
			else:
				db.warning("Unknown package identifier `%s' for `%s'." % (attr["package"], mcu_name))
		# CPU speed
		if attr.has_key("speed"):
			if attr["speed"] == "2":
				value_list["CategoryCPUSpeed"] = 20 * 1000 * 1000
			elif attr["speed"] == "4":
				if attr.has_key("family") and attr["family"] in ["ke02"]:
					value_list["CategoryCPUSpeed"] = 40 * 1000 * 1000
				else:
					value_list["CategoryCPUSpeed"] = 48 * 1000 * 1000
			elif attr["speed"] == "5":
				value_list["CategoryCPUSpeed"] = 50 * 1000 * 1000
			elif attr["speed"] == "7":
				if attr.has_key("top_family") and attr["top_family"] in ["kinetis v"]:
					value_list["CategoryCPUSpeed"] = 75 * 1000 * 1000
				else:
					value_list["CategoryCPUSpeed"] = 72 * 1000 * 1000
			elif attr["speed"] == "10" or attr["speed"] == "100":
				value_list["CategoryCPUSpeed"] = 100 * 1000 * 1000
			elif attr["speed"] == "12":
				value_list["CategoryCPUSpeed"] = 120 * 1000 * 1000
			elif attr["speed"] == "15":
				value_list["CategoryCPUSpeed"] = 150 * 1000 * 1000
			else:
				db.warning("Cannot identify the CPU speed from `%s' for `%s'." % (attr["speed"], mcu_name))

		# Save the value list
		for param_type in value_list.keys():
			value = value_list[param_type]
			# Handle devices with flex memory
			if param_type == "CategoryMemoryFlash":
				original_value = db.get_item_param_value(mcu, "CategoryMemoryFlash")
				# If the orignal number is higher than the new one, it measn that there is flexmemory
				if original_value and to_number(original_value) > to_number(value):
				        continue
				# If the registered size is lower than the one calculated +/-5%
				elif original_value and to_number(original_value) < to_number(value) * 0.95:
					db.warning("The flash memory size (%s) is bigger than the one registered (%s), please double check (%s)." % (value, original_value, mcu_name))
					continue
			db.set_item_parameter(mcu, param_type, value)

	def setup_specific_parser_rules(self, parser):
		pass

	def setup_parser_rules(self, parser):
		"""
		Rules that applies specificly to Freescale
		"""

		def category_post_processing_hook(category, options):
			"""
			1. In the SRAM memory, do not use the ratio * 1024
			"""
			#if category.to_param() in ["CategoryMemoryEEPROM", "CategoryMemorySRAM"]:
			#	self.workaround("Fix the (EB) issue in the unit, it should be (kB)")
			#	category.set_global_config('config_convert_ratio', 1024)
			pass

		def category_pre_processing_hook(category, options):
			"""
			1. Ignore '-' character, on Freescale it is not used to indicate that there is no features
			2. Analog channels (SE + DP as features)
			3. Flexbus means EBI
			"""
			category.ignore_minus_char()
			if category.to_param() in ["CategoryADCChannel", "CategoryDACChannel"]:
				category.add_feature_regexpr(["se", "dp"])
			if category.to_param() == "CategoryEBI":
				category.add_feature_regexpr(["flexbus"])
			if category.to_param() in ["CategoryMemoryEEPROM", "CategoryMemorySRAM"]:
				self.workaround("By default the ratio is set to kilo (1024).")
				category.config_convert_ratio = 1024

		def post_device_discovery(device, options):
			pass

		parser.hook("post_device_discovery", post_device_discovery)

		parser.hook("post_category_discovery", category_post_processing_hook)
		parser.hook("pre_category_discovery", category_pre_processing_hook)
		self.setup_specific_parser_rules(parser)

class FreescaleParametricSearchParser(GenericParser):
	"""
	<RESULT_HEADER>
		<RESULT_SECTION>
			<count>3</count>
			<Result>
				<HeaderUID id="id" compareVal="OP::MKL05Z32VFM4">
					<a	href ="http://www.freescale.com/webapp/sps/site/prod_summary.jsp?code=KL0&amp;fsrch=1&amp;sr=1">
						<text>MKL05Z32VFM4</text>
					</a>
					<displayOrder>a</displayOrder>
				</HeaderUID>
				<HeaderUID id="0000001679">
					48
				</HeaderUID>
				...
				<HeaderUID id="packages_desc">
					<a href="javascript:{ var leftpos=(screen.width	- 900)/2;var toppos	=(screen.height	- 500)/2-100;top.newWin	= window.open('http://www.freescale.com/webapp/search.partparamdetail.framework?PART_NUMBER=MKL05Z32VFM4&amp;buyNow=true&amp;fromSearch=true#Package_Information','Freescale','left='+leftpos+',top='+toppos+',width=900,height=500,titlebar=yes,'+'toolbar=yes,resizable=yes,scrollbars=yes,menubar=no,status=yes');top.newWin.focus();}">
						QFN 32 5*5*1 P0.5
					</a>
				</HeaderUID>
				...
			</Result>
			<Result>
				...
			</Result>
		</RESULT_SECTION>
		<HEADERSECTION>
			<header>
				<headerName>id</headerName>
				<isSortable>true</isSortable>
				<isSorted>false</isSorted>
				<isAscending>false</isAscending>
				<isHideable>false</isHideable>
				<isDefault>true</isDefault>
				<defTableOrder>0</defTableOrder>
				<isDefVisibleHeader>true</isDefVisibleHeader>
				<isAssociated>false</isAssociated>
				<groupName> </groupName>
				<displayName>Part Number</displayName>
				<adminOption> </adminOption>
				<UOM></UOM>
			</header>
			<header>
				...
			</header>
		</HEADERSECTION>
	</RESULT_HEADER>
	"""

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

	def load(self, data, options = {}):

		data = BeautifulSoup(data)
		# List all devices
		for index, d in enumerate(data.find_all("result")):
			self.element_create()
			# List all categories
			for index, c in enumerate(d.find_all("headeruid")):
				category_id = c['id']
				category_string = ""
				# Handle datasheet case
				if category_id in ["Info"]:
					match = re.findall(r"openCollateral\([\'\"]([^\'\"]*)[\'\"]", str(c))
					if len(match):
						category_string = HTMLParser.HTMLParser().unescape(match[0])
				else:
					text_tag = c.find_all("text")
					if len(text_tag):
						for t in text_tag:
							category_string += " " + self.format_value(t.get_text())
					else:
						category_string = c.get_text()
				self.element_add_value(category_string, str(category_id))
		# Category mapping
		for index, c in enumerate(data.find_all("header")):
			if c.headername and c.displayname:
				category_id = c.headername.string
				category_name = ""
				if c.groupname and c.groupname.string:
					category_name += " " + self.format_value(c.groupname.string)
				if c.displayname and c.displayname.string:
					category_name += " " + self.format_value(c.displayname.string)
				if c.uom and c.uom.string:
					category_name += " " + self.format_value(c.uom.string)
				self.category_mapping_add(category_id, category_name)

class FreescaleNewParser(GenericParser):
	"""
	{
		"deviceTree": [
			{
				"count":"4",
				"shortName":"c201",
				"displayName":"Microcontrollers"
			}
			,{
				"count":"4",
				"shortName":"c201_c173",
				"displayName":"Kinetis MCUs based on Cortex-M Cores"
			}
			,{
				"count":"4",
				"shortName":"c201_c173_c161",
				"displayName":"K Series"
			},
			{
				"count":"4",
				"shortName":"c201_c173_c161_c162",
				"displayName":"K0x Entry-level MCUs"
			}
		],
		"OPNs": [
			{
				"ProdName":"K02_100",
				"ProdCode":"MK02FN64VFM10",
				"opnRow":"yes",
				"p277":"16",
				"p31":"UART
				...
			}
			,
				...
		],
		"totalCount":"4",
		"paraheader": [
			{
				"shortName":"Order",
				"name":"Order",
				"filterId":"LOV - Value",
				"show":"true",
				"type":"Y",
				"filterVal":[{"Distributor":"1"}]
			},
			{
				"shortName":"status",
				"name":"Status",
				"filterId":"LOV - Value",
				"show":"true",
				"filterVal":[{"Active":"4"}],
				"type":"Y"
			},
			{
				"shortName":"p314",
				"dw":"",
				"name":"Package Type and Termination Count",
				"filterId":"LOV - Value",
				"filterVal":[{"QFN 32":"2"},{"QFP 64":"2"}],
				"type":"Y",
				"show":"true"
			},
			...
		]
	}
	"""
	def load(self, data, options = {}):
	#	FINISH TO UPDATE THIS CRAWLER
		# Read the JSON data
		json_data = json.loads(data)
		# Loop through the different part numbers
		for i, device in enumerate(json_data["OPNs"]):
			self.element_create()
			# Add the device name category
			self.element_add_value(device["ProdCode"], "device name")
			# Fill the values
			for j, keys in enumerate(device):
				self.element_add_value(device[keys], str(keys))
				self.info("Adding %s -> %s" % (str(keys), str(device[keys])), 3)
		# Set the category mapping
		for category in json_data["paraheader"]:
			self.category_mapping_add(category["shortName"], category["name"])

class FreescaleNewParametricSearch(FreescaleCommon):

	def get_options(self, options):
		return {
			'ignore_categories': [r"datasheet", r".*package.*your.*way.*", r"order"],
			'data': {
				'parser': FreescaleNewParser,
				'encoding': 'utf-8',
				'timeout': 600,
			}
		}

	specific_options_list = [
		# Kinetis K
		# K0x
		{'display': 'Kinetis K02_100', 'id': 'k02_100', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K02_100&co=Order,status,p314,p77,p136,p53,p277,p31,p78,p119,p80,p728,p240,p303,p66,p6,p67,p91,p259,p115,p187,p253,p725,p133,p254,p189,p112,p727'}]},
		# K1x
		{'display': 'Kinetis K10_100', 'id': 'k10_100', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K10_100&co=Order,status,p314,p77,p91,p254,p253,p94,p133,p187,p107,p257,p259,p277,p112,p31,p6,p256,p104,p189,p136,p303,p78,p119,p728,p66,p67,p87,p191,p48,p80,p53,p240,p724,p98,p25,p725,p726,p727,p276'}]},
		{'display': 'Kinetis K10_120', 'id': 'k10_120', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K10_120&co=Order,status,p314,p77,p91,p254,p253,p94,p133,p187,p107,p257,p259,p277,p112,p31,p6,p256,p104,p189,p136,p303,p78,p119,p728,p66,p67,p87,p28,p48,p80,p53,p240,p724,p98,p25,p725,p726,p727,p276'}]},
		{'display': 'Kinetis K10_50', 'id': 'k10_50', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K10_50&co=Order,status,p314,p77,p91,p254,p253,p94,p133,p187,p107,p257,p259,p277,p112,p31,p6,p256,p189,p136,p303,p78,p119,p728,p66,p67,p191,p48,p80,p240,p724,p98,p25,p725,p727,p87,p53'}]},
		{'display': 'Kinetis K10_72', 'id': 'k10_72', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K10_72&co=Order,status,p314,p77,p91,p254,p253,p94,p133,p187,p107,p257,p259,p277,p112,p31,p6,p256,p104,p189,p136,p303,p78,p119,p728,p66,p67,p87,p48,p80,p53,p240,p724,p98,p25,p725,p726,p727,p276'}]},
		{'display': 'Kinetis K11_50', 'id': 'k11_50', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K11_50&co=Order,status,p314,p77,p91,p254,p253,p94,p133,p187,p107,p257,p259,p277,p112,p31,p6,p256,p189,p136,p303,p78,p119,p80,p53,p240,p66,p67,p87,p98,p728,p48,p724,p25,p725,p727'}]},
		{'display': 'Kinetis K12_50', 'id': 'k12_50', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K12_50&co=Order,status,p314,p77,p91,p254,p253,p94,p133,p187,p107,p257,p259,p277,p112,p31,p6,p256,p104,p189,p136,p303,p78,p119,p728,p66,p67,p191,p48,p80,p240,p724,p98,p25,p725,p727,p87,p53'}]},
		# K2x
		{'display': 'Kinetis K20_100', 'id': 'k20_100', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K20_100&co=Order,status,p314,p77,p276,p91,p133,p254,p107,p253,p187,p94,p257,p259,p256,p277,p112,p6,p31,p104,p48,p189,p136,p78,p119,p728,p66,p67,p191,p80,p240,p303,p724,p98,p25,p725,p726,p727,p53,p87'}]},
		{'display': 'Kinetis K20_120', 'id': 'k20_120', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K20_120&co=Order,status,p314,p77,p91,p133,p254,p107,p253,p187,p94,p257,p259,p256,p277,p112,p6,p31,p104,p48,p189,p136,p78,p119,p728,p66,p67,p87,p28,p191,p80,p53,p240,p303,p724,p98,p25,p725,p726,p727'}]},
		{'display': 'Kinetis K20_50', 'id': 'k20_50', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K20_50&co=Order,status,p314,p77,p91,p133,p254,p107,p253,p187,p94,p257,p259,p256,p277,p112,p6,p31,p48,p189,p136,p78,p119,p728,p66,p67,p191,p80,p240,p303,p724,p25,p725,p727,p87,p53'}]},
		{'display': 'Kinetis K20_72', 'id': 'k20_72', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K20_72&co=Order,status,p314,p77,p91,p133,p254,p107,p253,p187,p94,p257,p259,p256,p277,p112,p6,p31,p104,p48,p189,p136,p78,p119,p728,p66,p67,p191,p80,p240,p303,p724,p98,p25,p725,p726,p727,p87,p53'}]},
		{'display': 'Kinetis K21_120', 'id': 'k21_120', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K21_120&co=Order,status,p314,p77,p91,p133,p254,p107,p253,p187,p94,p257,p259,p256,p277,p112,p6,p31,p104,p48,p189,p136,p78,p119,p728,p66,p67,p87,p191,p80,p53,p240,p303,p724,p98,p25,p725,p726,p727'}]},
		{'display': 'Kinetis K21_50', 'id': 'k21_50', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K21_50&co=Order,status,p314,p77,p276,p91,p133,p254,p107,p253,p187,p94,p257,p259,p256,p277,p112,p6,p31,p104,p48,p189,p136,p78,p119,p728,p66,p67,p87,p191,p80,p53,p240,p303,p724,p98,p25,p725,p727'}]},
		{'display': 'Kinetis K22_100', 'id': 'k22_100', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K22_100&co=Order,status,p314,p77,p91,p133,p254,p187,p259,p277,p112,p6,p31,p189,p136,p78,p119,p80,p53,p66,p67,p191,p240,p303,p115,p724,p725,p727'}]},
		{'display': 'Kinetis K22_120', 'id': 'k22_120', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K22_120&co=Order,status,p314,p77,p91,p133,p254,p107,p253,p187,p94,p257,p259,p256,p277,p112,p6,p31,p104,p48,p189,p136,p78,p119,p80,p240,p303,p66,p684,p724,p67,p115,p725,p727,p53,p728,p87,p191,p98,p25,p726'}]},
		{'display': 'Kinetis K22_50', 'id': 'k22_50', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K22_50&co=Order,status,p314,p77,p276,p91,p133,p254,p107,p253,p187,p94,p257,p259,p256,p277,p112,p6,p31,p104,p48,p189,p136,p78,p119,p728,p66,p67,p28,p191,p80,p240,p303,p724,p98,p25,p725,p727,p87,p53'}]},
		{'display': 'Kinetis K24_120', 'id': 'k24_120', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K24_120&co=Order,status,p314,p77,p91,p133,p254,p107,p253,p187,p94,p257,p259,p256,p277,p112,p6,p31,p104,p48,p189,p136,p78,p119,p728,p66,p67,p87,p191,p80,p53,p240,p303,p724,p98,p25,p725,p726,p727'}]},
		# K3x
		{'display': 'Kinetis K30_100', 'id': 'k30_100', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K30_100&co=Order,status,p314,p77,p276,p94,p107,p91,p133,p254,p187,p253,p257,p259,p277,p112,p6,p31,p104,p48,p189,p136,p303,p89,p78,p119,p728,p66,p67,p28,p256,p80,p240,p724,p98,p25,p725,p726,p727,p87,p53'}]},
		{'display': 'Kinetis K30_72', 'id': 'k30_72', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K30_72&co=Order,status,p314,p77,p94,p107,p91,p133,p254,p187,p253,p257,p259,p277,p112,p6,p31,p104,p48,p189,p136,p303,p89,p78,p119,p728,p66,p67,p87,p256,p80,p53,p240,p724,p98,p25,p725,p726,p727,p191'}]},
		# K4x
		{'display': 'Kinetis K40_100', 'id': 'k40_100', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K40_100&co=Order,status,p314,p77,p276,p91,p133,p254,p277,p112,p259,p94,p187,p253,p107,p6,p31,p89,p78,p104,p136,p119,p728,p66,p67,p257,p191,p189,p256,p48,p80,p240,p303,p724,p98,p25,p725,p726,p727,p87,p53'}]},
		{'display': 'Kinetis K40_72', 'id': 'k40_72', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K40_72&co=Order,status,p314,p77,p91,p133,p254,p277,p112,p259,p94,p187,p253,p107,p6,p31,p89,p78,p104,p136,p119,p728,p66,p67,p257,p191,p189,p256,p48,p80,p240,p303,p724,p98,p25,p725,p726,p727,p87,p53'}]},
		# K5x
		{'display': 'Kinetis K50_100', 'id': 'k50_100', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K50_100&co=Order,status,p314,p77,p91,p133,p254,p277,p259,p107,p94,p187,p253,p31,p25,p78,p104,p136,p119,p728,p66,p67,p87,p257,p28,p191,p189,p256,p48,p80,p53,p240,p303,p6,p724,p98,p725,p112,p727'}]},
		{'display': 'Kinetis K50_72', 'id': 'k50_72', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K50_72&co=Order,status,p314,p77,p91,p133,p254,p277,p259,p107,p94,p187,p253,p31,p78,p104,p136,p119,p728,p66,p67,p87,p257,p191,p189,p256,p48,p80,p53,p240,p303,p6,p724,p98,p25,p725,p112,p727'}]},
		{'display': 'Kinetis K51_100', 'id': 'k51_100', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K51_100&co=Order,status,p314,p77,p276,p91,p133,p254,p277,p259,p107,p94,p187,p89,p253,p31,p78,p104,p136,p119,p728,p66,p67,p87,p257,p28,p191,p189,p256,p48,p80,p53,p240,p303,p6,p724,p98,p25,p725,p112,p727'}]},
		{'display': 'Kinetis K51_72', 'id': 'k51_72', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K51_72&co=Order,status,p314,p77,p91,p133,p254,p277,p259,p107,p94,p187,p89,p253,p31,p78,p104,p136,p119,p728,p66,p67,p87,p257,p191,p189,p256,p48,p80,p53,p240,p303,p6,p724,p98,p25,p725,p112,p727'}]},
		{'display': 'Kinetis K53_100', 'id': 'k53_100', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K53_100&co=Order,status,p314,p77,p276,p91,p133,p254,p277,p259,p107,p94,p187,p89,p253,p78,p136,p119,p80,p53,p240,p303,p66,p67,p87,p98,p257,p189,p112,p31,p104,p728,p191,p256,p48,p6,p724,p25,p725,p727'}]},
		# K6x
		{'display': 'Kinetis K60_100', 'id': 'k60_100', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K60_100&co=Order,status,p314,p77,p276,p91,p133,p254,p277,p112,p28,p259,p94,p107,p256,p187,p253,p31,p78,p104,p136,p119,p728,p66,p67,p257,p191,p189,p48,p80,p240,p303,p6,p724,p98,p25,p725,p726,p727,p87,p53'}]},
		{'display': 'Kinetis K60_120', 'id': 'k60_120', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K60_120&co=Order,status,p314,p77,p276,p91,p133,p254,p277,p112,p28,p259,p94,p107,p256,p187,p253,p31,p78,p104,p136,p119,p728,p66,p67,p87,p257,p191,p189,p48,p80,p53,p240,p303,p6,p724,p98,p25,p725,p726,p727'}]},
		{'display': 'Kinetis K63_120', 'id': 'k63_120', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K63_120&co=Order,status,p314,p77,p91,p133,p254,p277,p112,p259,p94,p107,p256,p187,p253,p31,p78,p136,p119,p728,p66,p67,p87,p257,p191,p189,p48,p80,p53,p240,p303,p6,p724,p98,p25,p725,p726,p727'}]},
		{'display': 'Kinetis K64_120', 'id': 'k64_120', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K64_120&co=Order,status,p314,p77,p91,p133,p254,p277,p112,p259,p94,p107,p256,p187,p253,p31,p78,p136,p119,p728,p66,p67,p87,p257,p191,p189,p48,p80,p53,p240,p303,p6,p724,p98,p25,p725,p726,p727'}]},
		# K7x
		{'display': 'Kinetis K70_120', 'id': 'k70_120', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=K70_120&co=Order,status,p314,p77,p276,p91,p133,p254,p112,p107,p256,p253,p187,p89,p94,p31,p78,p104,p136,p119,p728,p66,p67,p87,p257,p259,p28,p191,p189,p277,p48,p80,p53,p240,p303,p6,p724,p98,p25,p725,p726,p727'}]},

		# Kinetis V
		{'display': 'Kinetis KV1x', 'id': 'kv1x', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KV1x&co=Order,status,p314,p77,p257,p259,p91,p133,p277,p6,p31,p187,p303,p78,p104,p136,p119,p728,p66,p67,p253,p94,p191,p107,p189,p254,p256,p48,p80,p53,p240,p25,p725,p727,p47,p40,p46'}]},
		{'display': 'Kinetis KV3x', 'id': 'kv3x', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KV3x&co=Order,status,p314,p77,p257,p259,p91,p133,p277,p6,p31,p187,p303,p48,p104,p78,p119,p80,p53,p240,p66,p67,p253,p191,p725,p254,p189,p112,p727,p256'}]},
		{'display': 'Kinetis KV4x', 'id': 'kv4x', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KV4x&co=Order,status,p314,p77,p257,p259,p133,p277,p6,p31,p187,p303,p48,p78,p119,p80,p728,p53,p240,p66,p67,p253,p191,p725,p189,p112,p727,p254,p104'}]},

		# Kinetis M
		{'display': 'Kinetis KM1x', 'id': 'km1x', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KM1x&co=Order,status,p314,p77,p259,p133,p277,p6,p31,p189,p187,p136,p48,p240,p303,p78,p119,p80,p728,p53,p66,p67,p87,p28,p94,p725,p727'}]},
		{'display': 'Kinetis KM3x', 'id': 'km3x', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KM3x&co=Order,status,p314,p77,p259,p133,p277,p6,p31,p189,p187,p136,p48,p240,p303,p78,p119,p80,p728,p53,p66,p67,p87,p28,p94,p725,p727'}]},

		# Kinetis W
		{'display': 'Kinetis KW0x', 'id': 'kw0x', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KW0x&co=Order,status,p314,p77,p133,p277,p257,p259,p35,p225,p310,p73,p240,p303,p87,p6,p31,p189,p187,p94,p78,p119,p80,p53,p66,p67,p725,p727'}]},
		{'display': 'Kinetis KW2x', 'id': 'kw2x', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KW2x&co=Order,status,p314,p77,p133,p277,p257,p259,p35,p225,p310,p73,p60,p240,p303,p87,p6,p31,p189,p187,p94,p78,p119,p80,p728,p53,p66,p67,p191,p725,p727'}]},

		# Kinetis EA
		{'display': 'Kinetis KEA', 'id': 'kea', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KEA&co=Order,status,p77,p314,p133,p277,p112,p257,p259,p31,p6,p87,p136,p187,p189,p253,p240,p78,p119,p80,p728,p303,p66,p67,p94,p725,p726,p727,p53'}]},

		# Kinetis E
		{'display': 'Kinetis KE02', 'id': 'ke02', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KE02&co=Order,status,p314,p77,p133,p277,p112,p257,p259,p31,p87,p253,p94,p136,p187,p189,p240,p78,p119,p80,p728,p53,p303,p66,p6,p67,p725,p727'}]},
		{'display': 'Kinetis KE02_40', 'id': 'ke02_40', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KE02_40&co=Order,status,p314,p77,p133,p277,p112,p257,p259,p31,p253,p94,p136,p187,p189,p240,p78,p119,p80,p728,p53,p303,p66,p6,p67,p725'}]},
		{'display': 'Kinetis KE04', 'id': 'ke04', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KE04&co=Order,status,p314,p77,p133,p277,p112,p257,p259,p31,p87,p253,p136,p187,p189,p240,p78,p119,p80,p728,p53,p303,p66,p6,p67,p725,p727'}]},
		{'display': 'Kinetis KE06', 'id': 'ke06', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KE06&co=Order,status,p314,p77,p133,p259,p31,p253,p136,p187,p240,p78,p119,p80,p728,p53,p303,p66,p6,p67,p725,p726,p727'}]},

		# Kinetis L
		{'display': 'Kinetis KL0', 'id': 'kl0', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KL0&co=Order,status,p314,p77,p133,p277,p28,p259,p31,p6,p191,p104,p25,p48,p136,p187,p240,p189,p253,p303,p94,p78,p119,p728,p66,p67,p87,p257,p80,p53,p725,p727,p91,p115,p107,p254,p112,p724'}]},
		{'display': 'Kinetis KL02', 'id': 'kl02', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KL02&co=Order,status,p314,p77,p133,p277,p28,p259,p31,p6,p191,p104,p25,p48,p136,p187,p240,p189,p253,p303,p94,p78,p119,p80,p728,p53,p66,p67,p87,p257,p725'}]},
		{'display': 'Kinetis KL03', 'id': 'kl03', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KL03&co=Order,status,p314,p77,p133,p277,p259,p31,p6,p191,p104,p25,p136,p240,p189,p253,p303,p94,p78,p119,p728,p66,p67,p87,p88,p257,p91,p115,p107,p254,p80,p53,p725,p112,p727'}]},
		{'display': 'Kinetis KL1x', 'id': 'kl1x', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KL1x&co=Order,status,p314,p77,p133,p277,p28,p259,p31,p6,p191,p104,p25,p48,p136,p187,p240,p189,p253,p303,p94,p78,p119,p42,p40,p80,p53,p66,p46,p67,p257,p91,p112,p256,p724,p728,p87,p725,p727'}]},
		{'display': 'Kinetis KL2x', 'id': 'kl2x', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KL2x&co=Order,status,p314,p77,p133,p277,p28,p259,p31,p6,p191,p104,p25,p48,p136,p187,p240,p189,p253,p303,p94,p78,p119,p42,p40,p80,p53,p66,p46,p67,p98,p257,p91,p112,p256,p728,p87,p725,p727,p724'}]},
		{'display': 'Kinetis KL3x', 'id': 'kl3x', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KL3x&co=Order,status,p314,p77,p133,p277,p28,p259,p31,p6,p191,p104,p25,p48,p136,p240,p189,p253,p303,p94,p78,p119,p66,p67,p257,p91,p256,p42,p80,p40,p53,p46,p112,p728,p87,p725,p727,p724'}]},
		{'display': 'Kinetis KL4x', 'id': 'kl4x', 'data': [{'url': 'http://www.freescale.com/webapp/search/loadJSON.sp?load=buyPara&aType=OP&p=KL4x&co=Order,status,p314,p77,p133,p277,p28,p259,p31,p6,p191,p104,p25,p48,p136,p240,p189,p253,p303,p94,p78,p119,p66,p67,p257,p91,p256,p42,p80,p40,p53,p46,p112,p728,p87,p725,p727,p724'}]},
	]

class FreescaleParametricSearch(FreescaleCommon):

	def get_options(self, options):
		return {
			'data': {
				'parser': FreescaleParametricSearchParser,
				'encoding': 'utf-8',
				'timeout': 600,
				'device_tag': ['RESULT_HEADER', 'RESULT_SECTION', 'Result'],
				'category_tag': ['HeaderUID'],
				'category_param': {
						'id_tag': [],
						'id_attr': "id",
						'value_tag': [],
						'value_optional_tag': ["a", "text"],
						'value_attr': None
					},
				'category_map_tag': ['HEADERSECTION', 'header'],
				'category_map_param': {
						'id_tag': ['headerName'],
						'id_attr': None,
						'value_multi': True,
						'value_tag': [ ['groupName'], ['displayName'], ['UOM'] ],
						'value_attr': [ None, None, None ]
					},
				'url': 'http://www.freescale.com/webapp/search/ResultAreaGenerator.jsp?',
			},
			'merge_categories': [{
				'merge_options': {'separator': ':', 'newline': ';'},
				'category_selector': ["serial interface type", "serial interface number of interfaces"],
				'category_name': "serial interface"
			}],
		}

	specific_options_list = [

		# All Kinetis
		{'display': 'Kinetis', 'id': 'k', 'data': [{'post': {'searchState': "fsrch=1`!showAllCategories=false`!fromMobile=false`!columnOrder=Info!`Order!`sector_param_status!`package_type!`budgetary_price!`0000001678!`0000001679!`0000002199!`0000001360!`0000002204!`0000001347!`0000001285!`0000001483!`0000001413!`0000002201!`0000002205!`0000001267!`0000002200!`0000001521!`0000001777!`0000002203!`0000001368!`0000001956!`0000001771!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs`!getTree=false`!fromPSP=false`!SelectedAsset=Orderable Parts`!fromCust=false`!fromDAP=false`!fromWebPages=false`!getResult=false`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!isResult=true`!isFromFlex=true`!isTree=false`!fromASP=false`!pageSize=1000`!isAdvanceSearch=false`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!getFilter=false`!isComparison=false`!"}}]},

		# Kinetis L
		{'display': 'KL0: Kinetis KL0 Entry-Level MCUs', 'id': 'kl0x', 'data': [{'post': {'searchState': "sessionChecker=nvXgQvcR11GxjC0PtVhfhzV72Lh5yKmpYJjTwmQFGfrBt2l28Y3S!-1210531214!1348656209351`!fsrch=1`!showAllCategories=false`!fromMobile=false`!columnOrder=Info%21%60Order%21%600000001679%21%600000001360%21%600000001347%21%600000001483%21%600000001413%21%600000001774%21%600000002200%21%600000001467%21%600000001267%21%600000002203%21%600000001672%21%600000001521%21%600000001777%21%600000001368%21%600000001771%21%600000001957%21%600000001956%21%60packages_desc%21%60budgetary_price%21%60sector_param_status%21%60app_qual_tier_desc%21%60plc_desc%21%60plc_cd%21%60lead_cnt%21%60MOUNTING%21%60MOISTURE_SENSE_LVL%21%60JEDEC_DESC%21%60ECCN%21%600000001884%21%600000001678%21%6011_CFLG%21%60`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/020M0S9FY70C``Kinetis L Series MCUs`!getTree=false`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=KL0`!fromCust=false`!searchType=3`!fromDAP=false`!fromWebPages=false`!getResult=false`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!isResult=true`!isFromFlex=true`!isTree=false`!pageSize=1000`!fromASP=false`!isAdvanceSearch=false`!svi=194.19.124.36.1347891890956732`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!getFilter=false`!isComparison=false`!customized=%21%60app_qual_tier_desc%21%60plc_desc%21%60plc_cd%21%60lead_cnt%21%60MOUNTING%21%60MOISTURE_SENSE_LVL%21%60JEDEC_DESC%21%60ECCN%21%600000001884%21%600000001678%21%6011_CFLG`!hidden=null`!"}}]},
		{'display': 'KL02: Kinetis KL02 Chip-Scale Package (CSP)', 'id': 'kl02', 'data': [{'post': {'searchState': "sessionChecker=qshnR6yhNC0J1WGR1hWTTx8bGJhN8J2C4g7kT7DJGqBJ2KVn2QgG!525461193!1375351450323`!prodTax=016246FH1YY70C`!searchType=3`!svi=194.19.124.36.1348829336578835`!SelectedAsset=Orderable Parts`!SelectedAsset=Orderable Parts`!pageSize=1000`!metaId=KL02`!lang_cd=en`!"}}]},
		{'display': 'KL03: Kinetis KL03 Chip-Scale Package (CSP)', 'id': 'kl03', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/030M0S9FY70C``Kinetis L Series MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=KL03`!fromDAP=false`!columnOrder=Info%21%60Order%21%60sector_param_status%21%60package_type%21%60budgetary_price%21%600000001679%21%60tape_and_reel%21%600000001360%21%600000001483%21%600000001413%21%600000001467%21%600000002203%21%600000001777%21%600000001957%21%600000001956%21%600000001216%21%600000001217%21%60ECCN%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%600000002199%21%60`!customized=0000001216%21%600000001217%21%60ECCN%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%600000002199%21%60`!pageNum=1`!"}}]},
		{'display': 'KL1x: Kinetis KL1x General Purpose MCUs', 'id': 'kl1x', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/030M0S9FY70C``Kinetis L Series MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=KL1x`!fromDAP=false`!columnOrder=Info%21%60Order%21%60sector_param_status%21%60package_type%21%60budgetary_price%21%600000001679%21%60tape_and_reel%21%600000001360%21%600000001347%21%600000001483%21%600000001413%21%600000001774%21%600000002200%21%600000001467%21%600000001267%21%600000002203%21%600000001672%21%600000001521%21%600000001777%21%600000001368%21%600000001771%21%600000001957%21%600000001956%21%6011_CFLG%21%600000001678%21%600000001884%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%60`!customized=11_CFLG%21%600000001678%21%600000001884%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%60`!pageNum=1`!"}}]},
		{'display': 'KL2x: Kinetis KL2x USB MCUs', 'id': 'kl2x', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/030M0S9FY70C``Kinetis L Series MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=KL2x`!fromDAP=false`!columnOrder=Info%21%60Order%21%60sector_param_status%21%60package_type%21%60budgetary_price%21%600000001679%21%60tape_and_reel%21%600000001360%21%600000001347%21%600000001483%21%600000001413%21%600000001774%21%600000002200%21%600000001467%21%600000001267%21%600000002203%21%600000001672%21%600000001521%21%600000001777%21%600000001368%21%600000001771%21%600000001957%21%600000001956%21%6011_CFLG%21%600000001678%21%600000001884%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%60`!customized=11_CFLG%21%600000001678%21%600000001884%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%60`!pageNum=1`!"}}]},
		{'display': 'KL3x: Kinetis KL3x Segment LCD MCUs', 'id': 'kl3x', 'data': [{'post': {'searchState': "sessionChecker=qshnR6yhNC0J1WGR1hWTTx8bGJhN8J2C4g7kT7DJGqBJ2KVn2QgG!525461193!1375351450323`!prodTax=016246FH1YY70C`!searchType=3`!svi=194.19.124.36.1348829336578835`!SelectedAsset=Orderable Parts`!SelectedAsset=Orderable Parts`!pageSize=1000`!metaId=KL3x`!lang_cd=en`!"}}]},
		{'display': 'KL4x: Kinetis KL4x USB and Segment LCD MCUs', 'id': 'kl4x', 'data': [{'post': {'searchState': "sessionChecker=qshnR6yhNC0J1WGR1hWTTx8bGJhN8J2C4g7kT7DJGqBJ2KVn2QgG!525461193!1375351450323`!prodTax=016246FH1YY70C`!searchType=3`!svi=194.19.124.36.1348829336578835`!SelectedAsset=Orderable Parts`!SelectedAsset=Orderable Parts`!pageSize=1000`!metaId=KL4x`!lang_cd=en`!"}}]},

		# Kinetis E
		{'display': 'KE02: Kinetis KE02 Entry-Level MCUs', 'id': 'ke02', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010MQ4YU75WC``Kinetis E Series MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=KE02`!fromDAP=false`!columnOrder=Info%21%60Order%21%60budgetary_price%21%600000001678%21%600000001679%21%600000001360%21%600000001347%21%600000001285%21%600000002203%21%600000001777%21%600000001368%21%600000002200%21%600000001957%21%600000001771%21%600000001216%21%600000001956%21%6011_CFLG%21%600000001884%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60package_type%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%600000001413%21%600000001483%21%60`!customized=0000001216%21%600000001956%21%6011_CFLG%21%600000001884%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60package_type%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%600000001413%21%600000001483%21%60`!pageNum=1`!"}}]},

		# Kinetis M
		{'display': 'KM1x: Kinetis KM1x MCU Family', 'id': 'km1', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/040MAR5BO5ZH``Kinetis M Series MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=KM1x`!fromDAP=false`!columnOrder=Info%21%60Order%21%60sector_param_status%21%60package_type%21%60budgetary_price%21%60tape_and_reel%21%600000001679%21%600000001360%21%600000001347%21%600000001413%21%600000001483%21%600000001777%21%600000001771%21%600000001368%21%600000001521%21%600000001957%21%600000001956%21%600000001672%21%6011_CFLG%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%600000002200%21%60`!customized=0000001672%21%6011_CFLG%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%600000002200%21%60`!pageNum=1`!"}}]},
		{'display': 'KM3x: Kinetis KM3x MCU Family', 'id': 'km3', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/040MAR5BO5ZH``Kinetis M Series MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=KM3x`!fromDAP=false`!columnOrder=Info%21%60Order%21%60sector_param_status%21%60package_type%21%60budgetary_price%21%60tape_and_reel%21%600000001679%21%600000001360%21%600000001347%21%600000001413%21%600000001483%21%600000001777%21%600000001771%21%600000001368%21%600000001521%21%600000001957%21%600000001956%21%600000001672%21%6011_CFLG%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%600000002200%21%60`!customized=0000001672%21%6011_CFLG%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%600000002200%21%60`!pageNum=1`!"}}]},

		# Kinetis W
		{'display': 'KW0x: Kinetis sub-1 GHz radio and ARM Cortex-M0+ MCU with 128 KB flash, 64 byte flash cache, 16 KB RAM', 'id': 'kw0x', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/050M7TMQR7YF``Kinetis W Series MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=KW0x`!fromDAP=false`!columnOrder=Info%21%60Order%21%60sector_param_status%21%60package_type%21%60tape_and_reel%21%600000001678%21%600000001679%21%600000001360%21%600000001347%21%600000001572%21%600000001310%21%600000002139%21%600000001668%21%600000001567%21%600000001957%21%600000001956%21%600000001216%21%600000001413%21%600000001483%21%600000001777%21%600000001771%21%600000002200%21%6011_CFLG%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001774%21%60`!customized=11_CFLG%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001774%21%60`!pageNum=1`!"}}]},
		{'display': 'KW2x: Kinetis KW2x Family of 2.4 GHz RF MCUs', 'id': 'kw2x', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/050M7TMQR7YF``Kinetis W Series MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=KW2x`!fromDAP=false`!columnOrder=Info%21%60Order%21%60sector_param_status%21%60package_type%21%60budgetary_price%21%60tape_and_reel%21%600000001678%21%600000001679%21%600000001360%21%600000001347%21%600000001572%21%600000001310%21%600000002139%21%600000001668%21%600000001567%21%600000001957%21%600000001956%21%600000001413%21%600000001483%21%600000001777%21%600000001771%21%600000002200%21%6011_CFLG%21%600000001884%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%600000001774%21%60`!customized=11_CFLG%21%600000001884%21%60ECCN%21%60MOISTURE_SENSE_LVL%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%60app_qual_tier_desc%21%600000001774%21%60`!pageNum=1`!"}}]},

		# Kinetis K
		#    Kinetis K02

		#    Kinetis K10
		{'display': 'K10_50: Kinetis K10 Baseline 50 MHz MCUs', 'id': 'k10_50', 'data': [{'post': {'searchState': "sessionChecker=nDR3QGCZj5b2trcZQcQ2Ww6RGS0ynyVKXcnZMFWZP0yCsB4y8pJW!-1288384361!1346683513318`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002199!`0000002204!`0000002203!`0000002200!`0000001360!`0000001771!`0000002201!`0000001678!`0000001679!`0000001347!`0000001285!`0000001483!`0000001413!`0000002205!`0000001267!`0000001777!`0000001368!`0000001956!`11_CFLG!`0000001884!`ECCN!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001957!`0000001521!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/010LXE7DK5Q3``K10 Baseline MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K10_50`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K10_72: Kinetis K10 Baseline 72 MHz MCUs', 'id': 'k10_72', 'data': [{'post': {'searchState': "sessionChecker=WW9JQGfHVT6Qjt5LXtknc2N2PWGpFlGTDWyP4J21HL124KV9TLC1!-889924706!1346772743076`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002199!`0000002204!`0000002203!`0000002200!`0000001360!`0000001771!`0000002201!`0000001678!`0000001679!`0000001347!`0000001285!`0000001483!`0000001413!`0000002205!`0000001267!`0000001777!`0000001368!`0000001956!`11_CFLG!`0000001884!`ECCN!`0000001235!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001957!`0000001521!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/010LXE7DK5Q3``K10 Baseline MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K10_72`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K10_100: Kinetis K10 Baseline 100 MHz MCUs', 'id': 'k10_100', 'data': [{'post': {'searchState': "sessionChecker=WW9JQGfHVT6Qjt5LXtknc2N2PWGpFlGTDWyP4J21HL124KV9TLC1!-889924706!1346772743076`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002199!`0000002204!`0000002203!`0000002200!`0000001360!`0000001771!`0000002201!`0000001678!`0000001679!`0000001347!`0000001285!`0000001483!`0000001413!`0000002205!`0000001267!`0000001777!`0000001368!`0000001956!`11_CFLG!`0000001884!`ECCN!`0000001235!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001957!`0000001521!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/010LXE7DK5Q3``K10 Baseline MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K10_100`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K10_120: Kinetis K10 Baseline 120 MHz MCUs', 'id': 'k10_120', 'data': [{'post': {'searchState': "sessionChecker=qVcYQG1Q1Dg94GFJqV21Q4xW1LjQcQQ3Hq0x2Rm54Tm82nRywx5V!1088951353!1346830144629`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002199!`0000002204!`0000002203!`0000002200!`0000001360!`0000001771!`0000002201!`0000001678!`0000001679!`0000001347!`0000001285!`0000001483!`0000001413!`0000002205!`0000001267!`0000001777!`0000001368!`0000001956!`0000001672!`11_CFLG!`0000001884!`ECCN!`0000001235!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001957!`0000001521!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/010LXE7DK5Q3``K10 Baseline MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K10_120`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		#    Kinetis K11
		{'display': 'K11_50: Kinetis K11 Baseline 50 MHz MCUs', 'id': 'k11_50', 'data': [{'post': {'searchState': "sessionChecker=1GvfQ1fG1wVjDvxQ9dNR75Q2P1HTnQDz969QRd0pvWrdKyktNCSH!488215765!1349852966923`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002199!`0000002204!`0000002203!`0000002200!`0000001360!`0000001771!`0000002201!`0000001678!`0000001679!`0000001347!`0000001285!`0000001483!`0000001413!`0000002205!`0000001267!`0000001777!`0000001368!`0000001956!`11_CFLG!`0000001884!`ECCN!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`MOUNTING!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001957!`0000001521!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/010LXE7DK5Q3``K10 Baseline MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1348829336578835`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K11_50`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		#    Kinetis K12
		{'display': 'K12_50: Kinetis K12 Baseline 50 MHz MCUs', 'id': 'k12_50', 'data': [{'post': {'searchState': "sessionChecker=WW9JQGfHVT6Qjt5LXtknc2N2PWGpFlGTDWyP4J21HL124KV9TLC1!-889924706!1346772743076`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002199!`0000002204!`0000002203!`0000002200!`0000001360!`0000001771!`0000002201!`0000001678!`0000001679!`0000001347!`0000001285!`0000001483!`0000001413!`0000002205!`0000001267!`0000001777!`0000001368!`0000001956!`11_CFLG!`0000001884!`ECCN!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`MOUNTING!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`0000001957!`0000001521!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/010LXE7DK5Q3``K10 Baseline MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K12_50`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		#    Kinetis K20
		{'display': 'K20_50: Kinetis K20 USB 50 MHz MCUs', 'id': 'k20_50', 'data': [{'post': {'searchState': "sessionChecker=qVcYQG1Q1Dg94GFJqV21Q4xW1LjQcQQ3Hq0x2Rm54Tm82nRywx5V!1088951353!1346830144629`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002199!`0000001360!`0000002204!`0000002201!`0000002203!`0000001771!`0000002200!`0000001678!`0000001679!`0000002205!`0000001347!`0000001285!`0000001413!`0000001483!`0000001267!`0000001521!`0000001777!`0000001368!`0000001956!`11_CFLG!`0000001884!`ECCN!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001957!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/020LXE7DZCIC``K20 USB MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K20_50`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K20_72: Kinetis K20 USB 72 MHz MCUs', 'id': 'k20_72', 'data': [{'post': {'searchState': "sessionChecker=qVcYQG1Q1Dg94GFJqV21Q4xW1LjQcQQ3Hq0x2Rm54Tm82nRywx5V!1088951353!1346830144629`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002199!`0000001360!`0000002204!`0000002201!`0000002203!`0000001771!`0000002200!`0000001678!`0000001679!`0000002205!`0000001347!`0000001285!`0000001413!`0000001483!`0000001267!`0000001521!`0000001777!`0000001368!`0000001956!`11_CFLG!`0000001884!`ECCN!`0000001235!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001957!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/020LXE7DZCIC``K20 USB MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K20_72`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K20_100: Kinetis K20 USB 100 MHz MCUs', 'id': 'k20_100', 'data': [{'post': {'searchState': "sessionChecker=qVcYQG1Q1Dg94GFJqV21Q4xW1LjQcQQ3Hq0x2Rm54Tm82nRywx5V!1088951353!1346830144629`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002199!`0000001360!`0000002204!`0000002201!`0000002203!`0000001771!`0000002200!`0000001678!`0000001679!`0000002205!`0000001347!`0000001285!`0000001413!`0000001483!`0000001267!`0000001521!`0000001777!`0000001368!`0000001956!`11_CFLG!`0000001884!`ECCN!`0000001235!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001957!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/020LXE7DZCIC``K20 USB MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K20_100`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K20_120: Kinetis K20 USB 120 MHz MCUs', 'id': 'k20_120', 'data': [{'post': {'searchState': "sessionChecker=Jlp5S6qQsqb0HKypZQn4tLVqZ1ncBW5W9nQbH8fNdY74DL612C12!-118055848!1379576544424`!prodTax=016246FH1YNHR6ZCIC`!searchType=3`!svi=194.19.124.36.1348829336578835`!SelectedAsset=Orderable Parts`!SelectedAsset=Orderable Parts`!pageSize=1000`!metaId=K20_120`!lang_cd=en`!"}}]},
		#    Kinetis K21
		{'display': 'K21_50: Kinetis K21 USB 50 MHz MCUs', 'id': 'k21_50', 'data': [{'post': {'searchState': "sessionChecker=qVcYQG1Q1Dg94GFJqV21Q4xW1LjQcQQ3Hq0x2Rm54Tm82nRywx5V!1088951353!1346830144629`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002199!`0000001360!`0000002204!`0000002201!`0000002203!`0000001771!`0000002200!`0000001678!`0000001679!`0000002205!`0000001347!`0000001285!`0000001413!`0000001483!`0000001267!`0000001521!`0000001777!`0000001368!`0000001956!`11_CFLG!`0000001884!`ECCN!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`MOUNTING!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`0000001957!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/020LXE7DZCIC``K20 USB MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K21_50`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K21_120: Kinetis K21 USB 120 MHz MCUs', 'id': 'k21_120', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/020LXE78NHR6``Kinetis K Series MCUs/020LXE7DZCIC``K2x USB MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=K21_120`!fromDAP=false`!columnOrder=Info%21%60Order%21%60sector_param_status%21%60package_type%21%60budgetary_price%21%60tape_and_reel%21%600000002199%21%600000001360%21%600000002204%21%600000002201%21%600000002203%21%600000001771%21%600000002200%21%600000001678%21%600000001679%21%600000002205%21%600000001347%21%600000001285%21%600000001413%21%600000001483%21%600000001267%21%600000001521%21%600000001777%21%600000001368%21%600000001956%21%6011_CFLG%21%600000001884%21%60ECCN%21%600000001235%21%60MOISTURE_SENSE_LVL%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001957%21%600000001774%21%60`!customized=0000001956%21%6011_CFLG%21%600000001884%21%60ECCN%21%600000001235%21%60MOISTURE_SENSE_LVL%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001957%21%600000001774%21%60`!pageNum=1`!"}}]},
		#    Kinetis K22
		{'display': 'K22_50: Kinetis K22 USB 50 MHz MCUs', 'id': 'k22_50', 'data': [{'post': {'searchState': "sessionChecker=qVcYQG1Q1Dg94GFJqV21Q4xW1LjQcQQ3Hq0x2Rm54Tm82nRywx5V!1088951353!1346830144629`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002199!`0000001360!`0000002204!`0000002201!`0000002203!`0000001771!`0000002200!`0000001678!`0000001679!`0000002205!`0000001347!`0000001285!`0000001413!`0000001483!`0000001267!`0000001521!`0000001777!`0000001368!`0000001956!`11_CFLG!`0000001884!`ECCN!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`MOUNTING!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`0000001957!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/020LXE7DZCIC``K20 USB MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K22_50`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K22_120: Kinetis K22 USB 120 MHz MCUs', 'id': 'k22_120', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/020LXE78NHR6``Kinetis K Series MCUs/020LXE7DZCIC``K2x USB MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=K22_120`!fromDAP=false`!columnOrder=Info%21%60Order%21%60sector_param_status%21%60package_type%21%60budgetary_price%21%60tape_and_reel%21%600000002199%21%600000001360%21%600000002204%21%600000002201%21%600000002203%21%600000001771%21%600000002200%21%600000001678%21%600000001679%21%600000002205%21%600000001347%21%600000001285%21%600000001413%21%600000001483%21%600000001267%21%600000001521%21%600000001777%21%600000001368%21%600000001956%21%6011_CFLG%21%600000001884%21%60ECCN%21%600000001235%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001957%21%600000001774%21%60`!customized=0000001956%21%6011_CFLG%21%600000001884%21%60ECCN%21%600000001235%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001957%21%600000001774%21%60`!pageNum=1`!"}}]},
		#    Kinetis K24
		{'display': 'K24_120: Kinetis K24 USB 120 MHz MCUs', 'id': 'k24_120', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/020LXE78NHR6``Kinetis K Series MCUs/020LXE7DZCIC``K2x USB MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=K24_120`!fromDAP=false`!columnOrder=Info%21%60Order%21%60sector_param_status%21%60package_type%21%60budgetary_price%21%60tape_and_reel%21%600000002199%21%600000001360%21%600000002204%21%600000002201%21%600000002203%21%600000001771%21%600000002200%21%600000001678%21%600000001679%21%600000002205%21%600000001347%21%600000001285%21%600000001413%21%600000001483%21%600000001521%21%600000001777%21%600000001368%21%600000001956%21%6011_CFLG%21%600000001884%21%60ECCN%21%600000001235%21%60MOISTURE_SENSE_LVL%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001957%21%600000001774%21%60`!customized=0000001956%21%6011_CFLG%21%600000001884%21%60ECCN%21%600000001235%21%60MOISTURE_SENSE_LVL%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001957%21%600000001774%21%60`!pageNum=1`!"}}]},
		#    Kinetis K30
		{'display': 'K30_72: Kinetis K30 Segment LCD 72 MHz MCUs', 'id': 'k30_72', 'data': [{'post': {'searchState': "sessionChecker=qVcYQG1Q1Dg94GFJqV21Q4xW1LjQcQQ3Hq0x2Rm54Tm82nRywx5V!1088951353!1346830144629`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002200!`0000002201!`0000002199!`0000001360!`0000002204!`0000001771!`0000002203!`0000001678!`0000001679!`0000001347!`0000001285!`0000001413!`0000001483!`0000001267!`0000001521!`0000001777!`0000001368!`0000001956!`11_CFLG!`0000001884!`ECCN!`0000001235!`JEDEC_DESC!`0000002205!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001957!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/030LXE7EM35I``K30 Segment LCD MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K30_72`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K30_100: Kinetis K30 Segment LCD 100 MHz MCUs', 'id': 'k30_100', 'data': [{'post': {'searchState': "sessionChecker=qVcYQG1Q1Dg94GFJqV21Q4xW1LjQcQQ3Hq0x2Rm54Tm82nRywx5V!1088951353!1346830144629`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002200!`0000002201!`0000002199!`0000001360!`0000002204!`0000001771!`0000002203!`0000001678!`0000001679!`0000001347!`0000001285!`0000001413!`0000001483!`0000001267!`0000001521!`0000001777!`0000001368!`0000001956!`11_CFLG!`0000001884!`ECCN!`0000001235!`JEDEC_DESC!`0000002205!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001957!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/030LXE7EM35I``K30 Segment LCD MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K30_100`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		#    Kinetis K40
		{'display': 'K40_72: Kinetis K40 USB and Segment LCD 72 MHz MCUs', 'id': 'k40_72', 'data': [{'post': {'searchState': "searchState:sessionChecker=DDv6QHLY4TR5Lph1P1pdvpmnTxrQQR4QWxTJ7DjLpvXpSr7rgL8y!1088951353!1346849624955`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002203!`0000002199!`0000001360!`0000002200!`0000001771!`0000002204!`0000002201!`0000001678!`0000001679!`0000001347!`0000001285!`0000001413!`0000001483!`0000001956!`11_CFLG!`0000001267!`0000001777!`0000001884!`ECCN!`0000001368!`JEDEC_DESC!`0000002205!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001957!`0000001521!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/040LXE7F624D``K40 USB & Segment LCD MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K40_72`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K40_100: Kinetis K40 USB and Segment LCD 100 MHz MCUs', 'id': 'k40_100', 'data': [{'post': {'searchState': "sessionChecker=DDv6QHLY4TR5Lph1P1pdvpmnTxrQQR4QWxTJ7DjLpvXpSr7rgL8y!1088951353!1346849624955`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002203!`0000002199!`0000001360!`0000002200!`0000001771!`0000002204!`0000002201!`0000001678!`0000001679!`0000001347!`0000001285!`0000001413!`0000001483!`0000001956!`11_CFLG!`0000001267!`0000001777!`0000001884!`ECCN!`0000001235!`0000001368!`JEDEC_DESC!`0000002205!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001957!`0000001521!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/040LXE7F624D``K40 USB & Segment LCD MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K40_100`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		#    Kinetis K50
		{'display': 'K50_72: Kinetis K50 Measurement 72 MHz MCUs', 'id': 'k50_72', 'data': [{'post': {'searchState': "sessionChecker=ZGNcQJWQKw4tzXTQvMcGKlPrJ2nls8xnMvlmk3JLQF17SdDydjhV!406752240!1346999888083`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002201!`0000002200!`0000002199!`0000001360!`0000001771!`0000002203!`0000002204!`REFLOW_TEMP_NUM!`0000001956!`11_CFLG!`0000001679!`0000001678!`0000001267!`0000001777!`0000001884!`0000001285!`ECCN!`0000001235!`0000001368!`0000001347!`JEDEC_DESC!`0000002205!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001413!`0000001483!`0000001957!`0000001521!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/050LXE7FN9UN``K50 Measurement MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K50_72`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K50_100: Kinetis K50 Measurement 100 MHz MCUs', 'id': 'k50_100', 'data': [{'post': {'searchState': "sessionChecker=ZGNcQJWQKw4tzXTQvMcGKlPrJ2nls8xnMvlmk3JLQF17SdDydjhV!406752240!1346999888083`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002201!`0000002200!`0000002199!`0000001360!`0000001771!`0000002203!`0000002204!`REFLOW_TEMP_NUM!`0000001956!`11_CFLG!`0000001679!`0000001678!`0000001267!`0000001777!`0000001884!`0000001285!`ECCN!`0000001235!`0000001368!`0000001347!`JEDEC_DESC!`0000002205!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001413!`0000001483!`0000001957!`0000001521!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/050LXE7FN9UN``K50 Measurement MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K50_100`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		#    Kinetis K51
		{'display': 'K51_72: Kinetis K51 Measurement 72 MHz MCUs', 'id': 'k51_72', 'data': [{'post': {'searchState': "sessionChecker=ZGNcQJWQKw4tzXTQvMcGKlPrJ2nls8xnMvlmk3JLQF17SdDydjhV!406752240!1346999888083`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`sector_param_status!`packages_desc!`budgetary_price!`0000002201!`0000002200!`0000002199!`0000001360!`0000001771!`0000002203!`0000002204!`REFLOW_TEMP_NUM!`0000001956!`11_CFLG!`0000001679!`0000001678!`0000001267!`0000001777!`0000001884!`0000001285!`ECCN!`0000001235!`0000001368!`0000001347!`JEDEC_DESC!`0000002205!`MOISTURE_SENSE_LVL!`MOUNTING!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001413!`0000001483!`0000001957!`0000001521!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/050LXE7FN9UN``K50 Measurement MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K51_72`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K51_100: Kinetis K51 Measurement 100 MHz MCUs', 'id': 'k51_100', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/020LXE78NHR6``Kinetis K Series MCUs/050LXE7FN9UN``K5x Measurement MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=K51_100`!fromDAP=false`!columnOrder=Info%21%60Order%21%60sector_param_status%21%60package_type%21%60budgetary_price%21%60tape_and_reel%21%600000002201%21%600000002200%21%600000002199%21%600000001360%21%600000001771%21%600000002203%21%600000002204%21%60REFLOW_TEMP_NUM%21%600000001956%21%600000001672%21%6011_CFLG%21%600000001679%21%600000001678%21%600000001267%21%600000001777%21%600000001884%21%600000001285%21%60ECCN%21%600000001235%21%600000001368%21%600000001347%21%600000002205%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001413%21%600000001483%21%600000001957%21%600000001521%21%600000001774%21%60`!customized=0000001956%21%600000001672%21%6011_CFLG%21%600000001679%21%600000001678%21%600000001267%21%600000001777%21%600000001884%21%600000001285%21%60ECCN%21%600000001235%21%600000001368%21%600000001347%21%600000002205%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001413%21%600000001483%21%600000001957%21%600000001521%21%600000001774%21%60`!pageNum=1`!"}}]},
		#    Kinetis K53
		{'display': 'K53_100: Kinetis K53 Measurement 100 MHz MCUs', 'id': 'k53_100', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/020LXE78NHR6``Kinetis K Series MCUs/050LXE7FN9UN``K5x Measurement MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=K53_100`!fromDAP=false`!columnOrder=Info%21%60Order%21%60sector_param_status%21%60package_type%21%60budgetary_price%21%60tape_and_reel%21%600000002201%21%600000002200%21%600000002199%21%600000001360%21%600000001771%21%600000002203%21%600000002204%21%60REFLOW_TEMP_NUM%21%600000001956%21%6011_CFLG%21%600000001679%21%600000001678%21%600000001267%21%600000001777%21%600000001884%21%600000001285%21%60ECCN%21%600000001235%21%600000001368%21%600000001347%21%600000002205%21%60MOISTURE_SENSE_LVL%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001413%21%600000001483%21%600000001957%21%600000001521%21%600000001774%21%60`!customized=0000001956%21%6011_CFLG%21%600000001679%21%600000001678%21%600000001267%21%600000001777%21%600000001884%21%600000001285%21%60ECCN%21%600000001235%21%600000001368%21%600000001347%21%600000002205%21%60MOISTURE_SENSE_LVL%21%60PCN_NUM%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001413%21%600000001483%21%600000001957%21%600000001521%21%600000001774%21%60`!pageNum=1`!"}}]},
		#    Kinetis K60
		{'display': 'K60_100: Kinetis K60 Ethernet Crypto 100 MHz MCUs', 'id': 'k60_100', 'data': [{'post': {'searchState': "sessionChecker=ZGNcQJWQKw4tzXTQvMcGKlPrJ2nls8xnMvlmk3JLQF17SdDydjhV!406752240!1346999888083`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`status!`packages_desc!`budgetary_price!`0000002204!`0000002199!`0000001360!`0000002200!`0000002201!`0000002205!`0000001771!`0000002203!`0000001956!`11_CFLG!`0000001679!`0000001678!`0000001267!`0000001777!`0000001884!`0000001285!`ECCN!`0000001235!`0000001368!`0000001347!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`PCN_NUM!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001413!`0000001483!`0000001957!`0000001521!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/060LXE7G970C``K60 Ethernet Crypto MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K60_100`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		{'display': 'K60_120: Kinetis K60 Ethernet Crypto 120/150 MHz MCUs', 'id': 'k60_120', 'data': [{'post': {'searchState': "sessionChecker=ZGNcQJWQKw4tzXTQvMcGKlPrJ2nls8xnMvlmk3JLQF17SdDydjhV!406752240!1346999888083`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`status!`packages_desc!`budgetary_price!`0000002204!`0000002199!`0000001360!`0000002200!`0000002201!`0000002205!`0000001771!`0000002203!`0000001956!`0000001672!`11_CFLG!`0000001679!`0000001678!`0000001267!`0000001777!`0000001884!`0000001285!`ECCN!`0000001235!`0000001368!`0000001347!`JEDEC_DESC!`MOISTURE_SENSE_LVL!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001413!`0000001483!`0000001957!`0000001521!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/060LXE7G970C``K60 Ethernet Crypto MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K60_120`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},
		#    Kinetis K63
		{'display': 'K63_120: Kinetis K63 Ethernet Crypto 120/150 MHz MCUs', 'id': 'k63_120', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/020LXE78NHR6``Kinetis K Series MCUs/060LXE7G970C``K6x Ethernet Crypto MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=K63_120`!fromDAP=false`!columnOrder=Info%21%60Order%21%60status%21%60package_type%21%60budgetary_price%21%60tape_and_reel%21%600000002204%21%600000002199%21%600000001360%21%600000002200%21%600000002201%21%600000002205%21%600000001771%21%600000002203%21%600000001956%21%6011_CFLG%21%600000001679%21%600000001678%21%600000001777%21%600000001884%21%600000001285%21%60ECCN%21%600000001235%21%600000001368%21%600000001347%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001413%21%600000001483%21%600000001957%21%600000001521%21%600000001774%21%60`!customized=0000001956%21%6011_CFLG%21%600000001679%21%600000001678%21%600000001777%21%600000001884%21%600000001285%21%60ECCN%21%600000001235%21%600000001368%21%600000001347%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001413%21%600000001483%21%600000001957%21%600000001521%21%600000001774%21%60`!pageNum=1`!"}}]},
		#    Kinetis K64
		{'display': 'K64_120: Kinetis K64 Ethernet Crypto 120/150 MHz MCUs', 'id': 'k64_120', 'data': [{'post': {'searchState': "searchType=3`!getResult=false`!iteration=1`!fsrch=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/020LXE78NHR6``Kinetis K Series MCUs/060LXE7G970C``K6x Ethernet Crypto MCUs`!isComparison=false`!showAllCategories=false`!getTree=false`!fromTrng=false`!getFilter=false`!fromPSP=false`!fromCust=false`!showCustomCollateral=false`!pageSize=1000`!RELEVANCE=true`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!isResult=true`!attempt=0`!isFromFlex=true`!assetLockedForNavigation=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!assetLocked=false`!svi=194.19.124.36.1392908052391800`!fromMobile=false`!metaId=K64_120`!fromDAP=false`!columnOrder=Info%21%60Order%21%60status%21%60package_type%21%60budgetary_price%21%60tape_and_reel%21%600000002204%21%600000002199%21%600000001360%21%600000002200%21%600000002201%21%600000002205%21%600000001771%21%600000002203%21%600000001956%21%6011_CFLG%21%600000001679%21%600000001678%21%600000001777%21%600000001884%21%600000001285%21%60ECCN%21%600000001235%21%600000001368%21%600000001347%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001413%21%600000001483%21%600000001957%21%600000001521%21%600000001774%21%60`!customized=0000001956%21%6011_CFLG%21%600000001679%21%600000001678%21%600000001777%21%600000001884%21%600000001285%21%60ECCN%21%600000001235%21%600000001368%21%600000001347%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001413%21%600000001483%21%600000001957%21%600000001521%21%600000001774%21%60`!pageNum=1`!"}}]},
		#    Kinetis K70
		{'display': 'K70_120: Kinetis K70 Graphic LCD 120/150 MHz MCUs', 'id': 'k70_120', 'data': [{'post': {'searchState': "sessionChecker=ZGNcQJWQKw4tzXTQvMcGKlPrJ2nls8xnMvlmk3JLQF17SdDydjhV!406752240!1346999888083`!fsrch=1`!attempt=0`!showCustomCollateral=false`!RELEVANCE=true`!fromTrng=false`!showAllCategories=false`!fromMobile=false`!isResult=false`!columnOrder=Info!`Order!`status!`packages_desc!`budgetary_price!`0000002199!`0000001360!`0000002204!`0000002201!`0000002205!`0000002203!`0000001771!`0000002200!`0000001956!`0000001672!`11_CFLG!`0000001679!`0000001678!`0000001267!`0000001777!`0000001884!`0000001285!`ECCN!`0000001235!`0000001368!`0000001347!`MOISTURE_SENSE_LVL!`lead_cnt!`plc_cd!`plc_desc!`0000001467!`app_qual_tier_desc!`0000001413!`0000001483!`0000001957!`0000001521!`0000001774!``!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/010LXE78NHR6``Kinetis K Series MCUs/070LXE7HA9B0``K70 Graphic LCD MCUs`!isTree=false`!isFromFlex=false`!pageSize=1000`!fromASP=false`!getTree=false`!svi=194.19.124.36.1334903193526574`!fromPSP=false`!SelectedAsset=Orderable Parts`!metaId=K70_120`!iteration=1`!assetLocked=false`!assetLockedForNavigation=false`!fromCust=false`!searchType=3`!getFilter=false`!fromDAP=false`!getResult=false`!isComparison=false`!pageNum=1`!"}}]},

		# Kinetis V
		{'display': 'Kinetis V', 'id': 'kinetis_v', 'data': [{'post': {'searchState': "attempt=0`!isFromFlex=true`!searchType=3`!getResult=false`!assetLockedForNavigation=false`!iteration=1`!Product Type=Products/040M934302706246``Microcontrollers/030L3CG5FH1Y``Kinetis MCUs/080N10ARNEPN``Kinetis V Series MCUs`!fsrch=1`!isComparison=false`!showAllCategories=false`!sessionChecker=Vff8G-LNGbnYsrjW4cIcb76V.ebiz_ms2`!getTree=false`!fromTrng=false`!fromPSP=false`!getFilter=false`!assetLocked=false`!fromCust=false`!svi=194.19.124.36.1392908052391800`!showCustomCollateral=false`!RELEVANCE=true`!pageSize=1000`!SelectedAsset=Orderable Parts`!fromWebPages=false`!fromASP=false`!fromMobile=false`!isAdvanceSearch=false`!lang_cd=en`!isTree=false`!metaId=KV1x`!fromDAP=false`!isResult=true`!columnOrder=Info%21%60Order%21%600000001771%21%600000001956%21%600000002203%21%6011_CFLG%21%600000001679%21%600000001678%21%600000001267%21%600000001777%21%600000001884%21%60ECCN%21%600000002204%21%600000001368%21%600000002201%21%600000001360%21%600000001347%21%600000002205%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60package_type%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001413%21%600000001483%21%600000001957%21%600000002200%21%600000001514%21%600000001697%21%600000001520%21%600000001521%21%600000002199%21%600000001774%21%60`!customized=0000001771%21%600000001956%21%600000002203%21%6011_CFLG%21%600000001679%21%600000001678%21%600000001267%21%600000001777%21%600000001884%21%60ECCN%21%600000002204%21%600000001368%21%600000002201%21%600000001360%21%600000001347%21%600000002205%21%60MOISTURE_SENSE_LVL%21%60MOUNTING%21%60package_type%21%60lead_cnt%21%60plc_cd%21%60plc_desc%21%600000001467%21%60app_qual_tier_desc%21%600000001413%21%600000001483%21%600000001957%21%600000002200%21%600000001514%21%600000001697%21%600000001520%21%600000001521%21%600000002199%21%600000001774%21%60`!pageNum=1`!"}}]},
	]
