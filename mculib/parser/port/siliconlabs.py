#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import re
import json

from mculib.parser.generic import *
from mculib.parser.deep import *

class SiliconLabsCommon(GenericParserPort):

	@staticmethod
	def get_manufacturer():
		return "siliconlabs"

	def setup_specific_parser_rules(self, parser):
		pass

	def setup_parser_rules(self, parser):
		"""
		Rules that applies specificly to Silicon Labs
		"""

		def category_pre_processing_hook(category, options):
			if category.to_param() in ["CategoryDatasheet"]:
				category.set_base_url("http://www.silabs.com")

		def post_device_discovery_hook(device, options):
			"""
			There is one part name per packaging
			"""
			# Rename the devices
			name = device.get_device_name(strict = True, fullname = False)
			name = re.sub(r"-[^-]*", "", name)
			device.force_device_category("CategoryDeviceName", name)

		parser.hook("pre_category_discovery", category_pre_processing_hook)
		parser.hook("post_device_discovery", post_device_discovery_hook)
		self.setup_specific_parser_rules(parser)

class SiliconLabsParser(GenericParser):
	"""
	Data have the following format:
		[
			{
				"MHz":"20",
				"McuCore":"8051",
				"FlashBytes":"32 kB",
				"RamBytes":"0.25",
				"DigitalPort":"32",
				"Communications":"I2C; SPI; UART",
				"PcaChannels":"5",
				"Timers16Bit":"4",
				"InternalOsc":"&#177;20%",
				"Adc1":"12-bit, 8-ch., 100 ksps",
				"Adc2":"—",
				"Dac":"12-bit, 2-ch.",
				"TempSensor":true,
				"DebugInterface":"JTAG",
				"Other":"—",
				"McuPackage":"QFP64",
				"DevKitLink":"&lt;a href=&quot;\/products\/mcu\/Pages\/C8051F005DK.aspx&quot;&gt;C8051F005DK.aspx&lt;\/a&gt;",
				"DevKit":"C8051F005DK",
				"DataSheetLink":"&lt;a href=&quot;\/Support%20Documents\/TechnicalDocs\/C8051F0xx.pdf&quot;&gt;C8051F0xx.pdf&lt;\/a&gt;",
				"DataShortLink":"&lt;a href=&quot;\/Support%20Documents\/TechnicalDocs\/C8051F000-Short.pdf&quot;&gt;C8051F000_short.pdf&lt;\/a&gt;",
				"ErrataLink":"",
				"Vref":true,
				"Comparators":"2",
				"Alternative":"",
				"AECQ100":false,
				"CapSense":false,
				"PartNumber":"C8051F000",
				"PartNumberLink":"&lt;a href=&quot;\/products\/mcu\/8-bit\/c8051f00x-f01x\/pages\/c8051f00x-f01x.aspx&quot;&gt;c8051f00x-f01x.aspx&lt;\/a&gt;",
				"OrderPartNumber":"C8051F000-GQ",
				"SampleAvailable":true,
				"BuyAvailable":true,
				"ReleaseDate":"\/Date(-62135575200000-0600)\/",
				"PackageType":"QFP64",
				"PackageSize":"10x10 mm",
				"Automotive":false,
				"Footnotes":"",
				"DevicePageURL":"\/products\/mcu\/8-bit\/c8051f00x-f01x\/pages\/\/C8051F000.aspx"
		},
		...
	]
	"""

	def parse_deep(self, data):
		data = data.encode('ascii', 'replace')
		data = json.loads(data)
		# Loop through each devices
		for d in data:
			self.element_create()
			# Loop through each categories
			for i, cat in enumerate(d):
				self.element_add_value(str(d[cat]), str(cat))

		# Add custom category mapping
		self.category_mapping_add("FlashBytes", "flash")
		self.category_mapping_add("RamBytes", "ram (kb)")
		self.category_mapping_add("Communications", "serial")
		self.category_mapping_add("Timers16Bit", "16-bit timer")
		self.category_mapping_add("Adc1", "adc 1")
		self.category_mapping_add("Adc2", "adc 2")
		self.category_mapping_add("TempSensor", "temperature sensor")
		self.remove_categories("DataSheetLink")
		self.remove_categories("DevicePageURL")
		self.remove_categories("PartNumberLink")
		self.remove_categories("DataShortLink")
		#self.category_mapping_add("communications", "digital")
		#self.category_mapping_add("timers16bit", "16-bit timers")
		#self.category_mapping_add("internalosc", "oscillator accuracy")
		#self.category_mapping_add("tempsensor", "temperature sensor")
		#self.category_mapping_add("datasheetlink", "datasheet link")
		#self.category_mapping_add("orderpartnumber", "")
		#self.category_mapping_add("partnumber", "part number")

	def load(self, data, options = {}):
		if options.has_key('data'):
			self.options = options['data']
		self.parse_deep(data)

class SiliconLabs(SiliconLabsCommon):

	def get_options(self, options):
		return {
			'ignore_categories': [r".*order.*"],
			'data': {
				'parser': SiliconLabsParser,
				'encoding': 'utf-8',
				'url': 'http://www.silabs.com/_vti_bin/ParametricSearchData.svc/getversion/GetMCUItems?UserId=flashLists&UserPassword=P@ssw0rd',
			},
		}

	specific_options_list = [
		{'display': 'Parametric', 'id': 'parametric', 'data': [{}]},
	]


