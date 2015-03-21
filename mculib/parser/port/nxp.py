#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import re

from mculib.parser.generic import *
from mculib.parser.deep import *

class NXPCommon(GenericParserPort):

	@staticmethod
	def get_manufacturer():
		return "nxp"

	def setup_specific_parser_rules(self, parser):
		pass

	def setup_parser_rules(self, parser):
		"""
		Rules that applies specificly to NXP
		"""
		def category_pre_processing_hook(category, options):
			"""
			"""
			if category.to_param() in ["CategoryCPUCore", "CategoryCPUCoreSecondary"]:
				category.add_translation_table([
					[ r".*(i/?o\s*handler)\b.*", "iohandler" ]
				])
		parser.hook("pre_category_discovery", category_pre_processing_hook)

		self.setup_specific_parser_rules(parser)

class NXPParser(GenericParser):
	"""
	Data have the following format:
	{
	"filters":[
		{"o":[],"se":[],"a":[],"t":"multi","i":"c0","d":"NXP product identifcation","f":"Type number","u":"","s":1,"cw":"large"},
		{
			"o":[{"c":1,"i":"9874d","l":"SOT163-1"},{"c":1,"i":"3f251","l":"SOT360-1"},{"c":2,"i":"714f0","l":"SOT403-1"},{"c":1,"i":"8e982","l":"SOT97-2"}],
			"se":["714f0","3f251","9874d","8e982"],
			"a":[],
			"t":"multi",
			"i":"c8313d","d":"code identifying the package outline version","f":"Package version","u":"","s":1,"cw":"medium"},
		{"o":[{"c":5,"i":"e6dfe","l":"Development"}],"se":["e6dfe"],"a":[],"t":"multi","i":"cdd728","d":"code indicating the life cycle phase of a product","f":"Product status","u":"","s":1,"cw":"medium"},
		{"min":30.0,"max":30.0,"vs":[30.0],"se":{"min":30.0,"max":30.0},"t":"range","i":"c65563","d":"maximum value of the internal clock frequency of a digital signal function IC","f":"f\u003csub\u003emax\u003c/sub\u003e [max]","u":"MHz","s":1,"cw":"small"},
		...
	],
	"results":[
		{"i":"c0","rs":[
			{"l":"LPC810M021FN8","h":"/pip/LPC810M021FN8","td":{"ds":"/documents/data_sheet/LPC81XM.pdf","pi":"/pip/LPC810M021FN8","tt":"LPC810M021FN8","d":"32-bit ARM Cortex-M0+ microcontroller; 4 kB flash and 1 kB SRAM","pc":"/packages/SOT97-2.html","sm":"/pip/LPC810M021FN8/ordering","od":"/pip/LPC810M021FN8/ordering","dc":"/pip/LPC810M021FN8/documentation","qa":"/pip/LPC810M021FN8/quality"},"i":"LPC810M021FN8"},
			{"l":"LPC811M001FDH16","h":"/pip/LPC811M001FDH16","td":{"ds":"/documents/data_sheet/LPC81XM.pdf","pi":"/pip/LPC811M001FDH16","tt":"LPC811M001FDH16","d":"32-bit ARM Cortex-M0+ microcontroller; 8 kB flash and 2 kB SRAM","pc":"/packages/SOT403-1.html","sm":"/pip/LPC811M001FDH16/ordering","od":"/pip/LPC811M001FDH16/ordering","dc":"/pip/LPC811M001FDH16/documentation","qa":"/pip/LPC811M001FDH16/quality"},"i":"LPC811M001FDH16"},
			{"l":"LPC812M101FD20","h":"/pip/LPC812M101FD20","td":{"ds":"/documents/data_sheet/LPC81XM.pdf","pi":"/pip/LPC812M101FD20","tt":"LPC812M101FD20","d":"32-bit ARM Cortex-M0+ microcontroller; 16 kB flash and 4 kB SRAM","pc":"/packages/SOT163-1.html","sm":"/pip/LPC812M101FD20/ordering","od":"/pip/LPC812M101FD20/ordering","dc":"/pip/LPC812M101FD20/documentation","qa":"/pip/LPC812M101FD20/quality"},"i":"LPC812M101FD20"},
			{"l":"LPC812M101FDH16","h":"/pip/LPC812M101FDH16","td":{"ds":"/documents/data_sheet/LPC81XM.pdf","pi":"/pip/LPC812M101FDH16","tt":"LPC812M101FDH16","d":"32-bit ARM Cortex-M0+ microcontroller; 16 kB flash and 4 kB SRAM","pc":"/packages/SOT403-1.html","sm":"/pip/LPC812M101FDH16/ordering","od":"/pip/LPC812M101FDH16/ordering","dc":"/pip/LPC812M101FDH16/documentation","qa":"/pip/LPC812M101FDH16/quality"},"i":"LPC812M101FDH16"},
			{"l":"LPC812M101FDH20","h":"/pip/LPC812M101FDH20","td":{"ds":"/documents/data_sheet/LPC81XM.pdf","pi":"/pip/LPC812M101FDH20","tt":"LPC812M101FDH20","d":"32-bit ARM Cortex-M0+ microcontroller; 16 kB flash and 4 kB SRAM","pc":"/packages/SOT360-1.html","sm":"/pip/LPC812M101FDH20/ordering","od":"/pip/LPC812M101FDH20/ordering","dc":"/pip/LPC812M101FDH20/documentation","qa":"/pip/LPC812M101FDH20/quality"},"i":"LPC812M101FDH20"}
		]},
		{"i":"c8313d","rs":[
			{"l":"SOT97-2","h":"/packages/SOT97-2.html"},
			{"l":"SOT403-1","h":"/packages/SOT403-1.html"},
			{"l":"SOT163-1","h":"/packages/SOT163-1.html"},
			{"l":"SOT403-1","h":"/packages/SOT403-1.html"},
			{"l":"SOT360-1","h":"/packages/SOT360-1.html"}
		]},
		...
	"""

	def parse_deep(self, json_data):

		def select_and_feed_element(i, element_index, value, category):
			if i == 0:
				self.element_create()
			else:
				self.element_select(element_index)
			self.element_add_value(value, str(category))
			return element_index + 1

		# Fill in the parameter values
		for i, category in enumerate(json_data["results"]):
			element_index = 0
			for value in category["rs"]:
				# If this is a MCU group
				if value.has_key("rs"):
					for value_sub in value["rs"]:
						element_index = select_and_feed_element(i, element_index, value_sub["l"], category["i"])
				else:
					element_index = select_and_feed_element(i, element_index, value["l"], category["i"])
		# Fill in the category names
		for category in json_data["filters"]:
			self.category_mapping_add(category["i"], category["f"] + " (" + category["u"] + ")")

	def load(self, data, options = {}):
		if options.has_key('data'):
			self.options = options['data']
		json_data = json.loads(data)
		self.parse_deep(json_data)

class NXP(NXPCommon):

	def get_options(self, options):
		return {
			'data': {
				'parser': NXPParser,
				'encoding': 'utf-8',
			},
			'map_categories': [[r".*type.*number.*", "device name"]],
		}

	specific_options_list = [
		# All
		{'display': 'All', 'id': 'all', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=50809'}]},
		# Cortex-M0
		{'display': 'LPC800', 'id': 'lpc800', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=71785'}], 'custom': {'CategoryDeviceTopFamily': 'lpc800', 'CategoryCPUCore': 'cm0+'}},
		{'display': 'LPC1100', 'id': 'lpc1100', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=1392389687150'}], 'custom': {'CategoryDeviceTopFamily': 'lpc1100'}},
		{'display': 'LPC1200', 'id': 'lpc1200', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=71514'}], 'custom': {'CategoryDeviceTopFamily': 'lpc1200'}},
		# Cortex-M3
		{'display': 'LPC1300', 'id': 'lpc1300', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=1403790687302'}], 'custom': {'CategoryDeviceTopFamily': 'lpc1300', 'CategoryCPUCore': 'cm3'}},
		{'display': 'LPC1500', 'id': 'lpc1500', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=1403790713448'}], 'custom': {'CategoryDeviceTopFamily': 'lpc1500', 'CategoryCPUCore': 'cm3'}},
		{'display': 'LPC1700', 'id': 'lpc1700', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=1403790745385'}], 'custom': {'CategoryDeviceTopFamily': 'lpc1700', 'CategoryCPUCore': 'cm3'}},
		{'display': 'LPC1800', 'id': 'lpc1800', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=1403790776032'}], 'custom': {'CategoryDeviceTopFamily': 'lpc1800', 'CategoryCPUCore': 'cm3'}},
		{'display': 'LPC2100/200/300/400', 'id': 'lpc210_200_300_400', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=71580'}]},
		{'display': 'LPC2900', 'id': 'lpc2900', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=71571'}]},
		{'display': 'LPC3100/200', 'id': 'lpc3100_200', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=71572'}]},
		# Cortex-M4
		{'display': 'LPC4000', 'id': 'lpc4000', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=1403790399405'}], 'custom': {'CategoryDeviceTopFamily': 'lpc4000', 'CategoryCPUCore': 'cm4'}},
		{'display': 'LPC4300', 'id': 'lpc4300', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=1403790133078'}], 'custom': {'CategoryDeviceTopFamily': 'lpc4300', 'CategoryCPUCore': 'cm4'}},
		{'display': 'LPC54100', 'id': 'lpc54100', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=100&fs=0&sc=&so=&es=&type=initial&i=1414576688124'}], 'custom': {'CategoryDeviceTopFamily': 'lpc54100', 'CategoryCPUCore': 'cm4f'}},
		{'display': 'LH7', 'id': 'lpc3100_200', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=99999&fs=0&sc=&so=&es=&type=initial&i=71572'}]},

		# 8-/16-bit Legacy
		{'display': 'LPC900', 'id': 'lpc900', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=100&fs=0&sc=&so=&es=&type=initial&i=71590'}], 'custom': {'CategoryDeviceTopFamily': 'lpc900', 'CategoryLegacy': 'yes'}},
		{'display': 'LPC700', 'id': 'lpc700', 'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=100&fs=0&sc=&so=&es=&type=initial&i=71592'}], 'custom': {'CategoryDeviceTopFamily': 'lpc700', 'CategoryLegacy': 'yes'}},
		{'display': 'OTP/ROM', 'id': 'otp_rom', 'ignore_categories': [r".*temperature.*range.*", r".*system.*frequency.*", r".*operating.*frequency.*"],
				'merge_categories': [
					{'category_selector': [r".*ram.*"],
					'category_name': "ram \(byte\)"
				}],'data': [{'url': 'http://www.nxp.com/parametrics/psdata/?p=1&s=0&c=&rpp=100&fs=0&sc=&so=&es=&type=initial&i=71591'}], 'custom': {'CategoryDeviceTopFamily': 'otp_rom', 'CategoryLegacy': 'yes'}},
	]


