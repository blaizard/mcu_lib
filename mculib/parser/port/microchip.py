#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from mculib.parser.generic import *
from mculib.parser.html_table import *
from mculib.parser.deep import *

class MicrochipCommon(GenericParserPort):
	allow_retry = True

	@staticmethod
	def get_manufacturer():
		return "microchip"

	def setup_specific_parser_rules(self, parser):
		pass

	def setup_parser_rules(self, parser):
		"""
		Rules that applies specificly to Microchip
		"""

		def category_pre_processing_hook(category, options):
			"""
			MSSP/SSP is a I2C and SPI peripheral
			ECCP/CCP is a PWM
			"""
			if category.to_param() in ["CategoryI2C", "CategorySPI"]:
				category.add_feature_regexpr(["mssp", "ssp"])
			if category.to_param() == "CategoryPWM":
				category.add_feature_regexpr(["eccp", "ccp"])
			if category.to_param() == "CategoryEBI":
				category.add_feature_regexpr(["pmp", "psp", "epmp"])
			if category.to_param() == "CategoryCPUCore":
				category.add_translation_table([
					[ r".*(baseline)\b.*", "pic_baseline" ],
					[ r".*(enhanced)\b.*", "pic_enhanced" ],
					[ r".*(midrange)\b.*", "pic_midrange" ],
					[ r".*\b(pic18)\b.*", "pic18" ],
					[ r".*\b(pic24)\b.*", "pic24" ],
					[ r".*\b(dspic30)\b.*", "dspic30" ],
					[ r".*\b(dspic33)\b.*", "dspic33" ],
				])

		def post_device_discovery_hook(device, options):
			# Read the device name
			name = device.get_device_name(strict = True, fullname = False)
			# Add web page path
			device.add_category("CategoryWebPage", "http://www.microchip.com/" + name)

		parser.hook("pre_category_discovery", category_pre_processing_hook)
		parser.hook("post_device_discovery", post_device_discovery_hook)

		self.setup_specific_parser_rules(parser)

class MicrochipHTML(MicrochipCommon):

	def get_options(self, options):
		return {
			# Ignore empty devices
			'ignore_devices':[[0, "^\s*$"]],
			'ignore_categories': [r"program memory.*kwords.*", "auxiliary flash", "dma ram", "adc mode 2 ksps", "adc mode 2 bits"],
			'map_categories': [ [0, "products"] ],
			'data': {
				'category_row': 0,
				'css_selector': "table#ctl00_ctl00_MainContent_PageContent_uc_ComparisonChart1_tblDetail",
				'timeout': 60,
				'parser': HTMLTableParser,
				# Used to get the page with the expanded view
				'post': {
					"ctl00$ctl00$MainContent$PageContent$uc_ComparisonChart1$view": "more",
					"__EVENTTARGET": "ctl00$ctl00$MainContent$PageContent$uc_ComparisonChart1$more"
				},
				'encoding': 'iso-8859-1',
			}
		}

	specific_options_list = [
		# 8-bit Products
		{'display': 'All 8-bit Microcontrollers Products', 'id': '8bit', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=1012' } ]},
		{'display': 'PIC10', 'id': 'pic10', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/chart.aspx?branchID=1009' } ], 'custom': {'CategoryDeviceTopFamily': 'pic10', 'CategoryDeviceFamily': 'pic10'}},
		{'display': 'PIC12', 'id': 'pic12', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/chart.aspx?branchID=1001' } ], 'custom': {'CategoryDeviceTopFamily': 'pic12', 'CategoryDeviceFamily': 'pic12'}},
		{'display': 'PIC16', 'id': 'pic16', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=1002' } ], 'custom': {'CategoryDeviceTopFamily': 'pic16', 'CategoryDeviceFamily': 'pic16'}},
		{'display': 'PIC18', 'id': 'pic18', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=1004' } ], 'custom': {'CategoryDeviceTopFamily': 'pic18', 'CategoryCPUCore': 'pic18'}},
		{'display': 'PIC18J', 'id': 'pic18j', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=1019' } ], 'custom': {'CategoryDeviceTopFamily': 'pic18', 'CategoryDeviceFamily': 'pic18j', 'CategoryCPUCore': 'pic18'}},
		{'display': 'PIC18K', 'id': 'pic18k', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=1026' } ], 'custom': {'CategoryDeviceTopFamily': 'pic18', 'CategoryDeviceFamily': 'pic18k', 'CategoryCPUCore': 'pic18'}},
		{'display': '8-bit Baseline', 'id': 'baseline', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=1023' } ], 'custom': {'CategoryCPUCore': 'pic_baseline'}},
		{'display': '8-bit Mid-Range', 'id': 'midrange', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=1024' } ], 'custom': {'CategoryCPUCore': 'pic_midrange'}},
		{'display': '8-bit Enhanced Mid-Range', 'id': 'enhanced_midrange', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=1025' } ], 'custom': {'CategoryCPUCore': 'pic_enhanced'}},
		# 16-bit Products
		{'display': 'All 16-bit Microcontrollers Products', 'id': '16bit', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=20' } ]},
		{'display': 'PIC24F', 'id': 'pic24f', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8181' } ], 'custom': {'CategoryDeviceTopFamily': 'pic24', 'CategoryDeviceFamily': 'pic24f', 'CategoryCPUCore': 'pic24'}},
		{'display': 'PIC24H', 'id': 'pic24h', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8186' } ], 'custom': {'CategoryDeviceTopFamily': 'pic24', 'CategoryDeviceFamily': 'pic24h', 'CategoryCPUCore': 'pic24'}},
		{'display': 'PIC24E', 'id': 'pic24e', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8187' } ], 'custom': {'CategoryDeviceTopFamily': 'pic24', 'CategoryDeviceFamily': 'pic24e', 'CategoryCPUCore': 'pic24'}},
		{'display': 'DSPIC30F DSC', 'id': 'dspic30f', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8182' } ], 'custom': {'CategoryDeviceTopFamily': 'dspic', 'CategoryDeviceFamily': 'dspic30f', 'CategoryCPUCore': 'dspic30'}},
		{'display': 'DSPIC33E DSC', 'id': 'dspic33e', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8188' } ], 'custom': {'CategoryDeviceTopFamily': 'dspic', 'CategoryDeviceFamily': 'dspic33e', 'CategoryCPUCore': 'dspic33'}},
		{'display': 'DSPIC33F DSC', 'id': 'dspic33f', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8192' } ], 'custom': {'CategoryDeviceTopFamily': 'dspic', 'CategoryDeviceFamily': 'dspic33f', 'CategoryCPUCore': 'dspic33'}},
		# 32-bit Products
		{'display': 'PIC32', 'id': 'pic32', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=211' } ], 'custom': {'CategoryDeviceTopFamily': 'pic32', 'CategoryDeviceFamily': 'pic32', 'CategoryCPUCore': 'mips32m4k'}},
		# Microcontrollers By Application Features
		{'display': 'Sensor', 'id': 'sensor', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8096' } ]},
		{'display': 'DSP', 'id': 'dsp', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8097' } ]},
		{'display': 'SMPS & Digital Power Conversion', 'id': 'smps', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8010' } ]},
		{'display': 'General Purpose', 'id': 'gp', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8098' } ]},
		{'display': 'CAN', 'id': 'can', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=50' } ]},
		{'display': 'mTouch', 'id': 'mtouch', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=144' } ]},
		{'display': 'XLP', 'id': 'xlp', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=143' } ], 'custom': {'CategorySpecialFeature': 'xlp'}},
		{'display': 'USB', 'id': 'usb', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=111' } ]},
		{'display': 'Ethernet', 'id': 'ethernet', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=121' } ]},
		{'display': 'LCD', 'id': 'lcd', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=107' } ]},
	#	{'display': 'Motor Control', 'id': 'mc', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=55' } ]},
	#	{'display': 'CAN (bis)', 'id': 'can2', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8094' } ]},
	#	{'display': 'USB (bis)', 'id': 'usb2', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8011' } ]},
	#	{'display': 'Motor Control & Power Conversion', 'id': 'mc_pc', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8093' } ]},
	#	{'display': 'Codec Interface', 'id': 'codec', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8095' } ]},
	#	{'display': 'nanoWatt', 'id': 'nanowatt', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8099' } ],
			# Hack, ignore the analog column in this category it gives wrong results because badly formated
	#		'ignore_categories': ["analog"],
	#	},
	#	{'display': 'Graphics', 'id': 'graphics', 'data': [ { 'url': 'http://www.microchip.com/ParamChartSearch/Chart.aspx?branchID=8101' } ]},
	]

class MicrochipProductSelectionTool(MicrochipCommon):

	specific_options_list = [
		{'display': 'Master Parametric Table', 'id': 'master_param_table',
			'data': [{
				'url': 'http://www.microchip.com/mchpweblib/products.asmx/ProductsByGroup',
				'post': {
					'prefix': '*',
					'columns': 'ADCBit,ADChannels,AEUSART,architecture,bytes,CAN,CapTouchCH,CCP,Comparators,CPUSpeedMHz,CPUSpeedMIPS,ECCP,EEPROM,Ethernet,PSP,I2C,inputCapture,LIN,link,LowPwTimer1Osc,MSSP,nWFastWake,nWLowSleep,nWPwrMode,pricing,PSP,PWMChannels,outputPWM,pincount,PWMresolutions,RAM,RAM,RTCC,segmentLCD,SPI,SSP,supplyVoltageMax,supplyVoltageMin,Timer16Bit,Timer32Bit,Timer8Bit,title,UART,USB,XLP',
					'group': 'PICMCU',
					'filter': '*',
					'lang': 'en'},
				'timeout': 120,
				'parser': XMLParser,
				'device_tag': ['ProductLib', 'Products', 'Product'],
				'category_tag': ['param'],
				'category_param': {
					'id_tag': [],
					'id_attr': "name",
					'value_tag': [],
					'value_attr': "value"
				},
				'category_map_tag': ['ProductLib', 'ProductParamHeader', 'Label'],
				'category_map_param': {
					'id_tag': [],
					'id_attr': 'name',
					'value_tag': [],
					'value_attr': 'text'
				}
			}]
		}
	]

	def setup_specific_parser_rules(self, parser):
		def category_post_processing_hook(category, options):
			"""
			1. In the SRAM memory, do not use the ratio * 1024
			"""
			if category.to_param() == "CategoryMemorySRAM":
				self.workaround("Disable CategoryMemorySRAM ratio")
				category.set_global_config('config_convert_ratio', 1)

		def category_pre_processing_hook(category, options):
			"""
			Make sure it matches these category names:
				- "Pincount"
				- "ADCBit"
				- "LowPwTimer1Osc"
				- "PWMresolutions"
			"""
			if category.to_param() in ["CategoryADCResolution"]:
				category.add_category_regexpr("adcbit")

		parser.hook("pre_category_discovery", category_pre_processing_hook)
		parser.hook("post_category_discovery", category_post_processing_hook)
