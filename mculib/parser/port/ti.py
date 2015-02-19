#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from mculib.parser.generic import *
from mculib.parser.deep import *

class TICommon(GenericParserPort):

	@staticmethod
	def get_manufacturer():
		return "ti"

	def setup_specific_parser_rules(self, parser):
		pass

	def setup_parser_rules(self, parser):
		"""
		Rules that applies specificly to TI
		"""

		def category_pre_processing_hook(category, options):
			# Empty values means 0 or none in TI's paramteric tables
			#category.consider_empty_values() Seems not true anymore
			if category.to_param() == "CategoryDeviceName":
				category.add_category_regexpr(r"^qgpn$")
			if category.to_param() == "CategoryCPUCore":
				category.add_translation_table([
					[ r".*\b(msp430x)\b.*", "msp430x" ],
					[ r".*\b(msp430)\b.*", "msp430" ],
					[ r".*\b(c24).*", "c24x" ],
					[ r".*\b(c28).*", "c28x" ]
				])
			if category.to_param() == "CategoryDatasheet":
				def get_category_regexpr_void(self):
					return None
				category.get_category_regexpr = get_category_regexpr_void

		def post_device_discovery_hook(device, options):
			family_translation_table = [
				[ r"^msp430f1.*", "msp430f1" ],
				[ r"^msp430c1.*", "msp430c1" ],
				[ r"^msp430f2.*", "msp430f2" ],
				[ r"^msp430g2.*", "msp430g2" ],
				[ r"^msp430c3.*", "msp430c3" ],
				[ r"^msp430c4.*", "msp430c4" ],
				[ r"^msp430cg4.*", "msp430cg4" ],
				[ r"^msp430f4.*", "msp430f4" ],
				[ r"^msp430fe4.*", "msp430fe4" ],
				[ r"^msp430fg4.*", "msp430fg4" ],
				[ r"^msp430fw4.*", "msp430fw4" ],
				[ r"^msp430f5.*", "msp430f5" ],
				[ r"^msp430f6.*", "msp430f6" ],
				[ r"^msp430fr57.*", "msp430fr57" ],
				[ r"^msp430fr58.*", "msp430fr58" ],
				[ r"^msp430fr59.*", "msp430fr59" ],
				[ r"^msp430c09.*", "msp430c09" ],
				[ r"^msp430l09.*", "msp430l09" ],
				[ r"^cc430.*", "cc430" ],
				[ r"^tm4c.*", "tivac" ],
			]
			top_family_translation_table = [
				[ r"^msp430.*", "msp430" ],
				[ r"^lm4.*", "stellaris" ],
				[ r"^lm3.*", "stellaris" ],
				[ r"^tm4.*", "tiva" ],
			]
			name = device.get_device_name(strict = False, fullname = False)
			if name == None:
				return

			for family_translation in family_translation_table:
				if re.match(family_translation[0], name):
					device.add_category("CategoryDeviceFamily", family_translation[1])
			for top_family_translation in top_family_translation_table:
				if re.match(top_family_translation[0], name):
					device.add_category("CategoryDeviceTopFamily", top_family_translation[1])
			# Add datasheet path
			device.add_category("CategoryWebPage", "http://www.ti.com/product/" + name)
			device.add_category("CategoryDatasheet", "http://www.ti.com/lit/gpn/" + name)

		parser.hook("pre_category_discovery", category_pre_processing_hook)
		parser.hook("post_device_discovery", post_device_discovery_hook)
		self.setup_specific_parser_rules(parser)

class TIParser(GenericParser):
	"""
	{
		"ParametricResults": [
			{
				"o1": "MSP430C1101",
				"o2": "MSP430C1101",
				"o3": "16-Bit Ultra-Low-Power Microcontroller, 1kB of ROM, 128B RAM, Comparator",
				"o4": "ACTIVE",
				"o5": "",
				"o7": "1 Series",
				"o10": "fbd_slas241i.gif",
				"o11": "SLAS241I",
				"p62": "8",
				"p1227": "",
				"p67": "128",
				"p886": "14",
				"p2090": "Yes",
				"p730": "Yes",
				"p1025": "",
				"p242": ""
	"""
	pass

class TI(TICommon):

	# Common parser options
	def get_options(self, options):
		return {
			'data': [{
					'parser': JSONParser,
					'device_tag': ["ParametricResults", None],
					'category_tag': [None],
					'category_param': {
						'id_tag': [],
						'id_attr': True,
						'value_tag': [],
						'value_attr': False,
						'value_optional_tag': ["multipair1", "l"],
					},
					'encoding': 'utf-8',
					'timeout': 30
				}, {
					'parser': JSONParser,
					'category_map_tag': ["ParametricControl", "controls", None],
					'category_map_param': {
						'id_tag': ["cid"],
						'id_attr': False,
						'value_tag': [ ["name"], ["units"] ],
						'value_attr': [ False, False ],
					},
					'encoding': 'utf-8',
					'timeout': 30
				}
			],
			'ignore_categories': [r"uart.*modem.*signalling", ".*family.*"]
		}

	specific_options_list = [
		# All
		{'display': 'All MCUs', 'id': 'all', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/4/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/4/criteria?lang=en&output=json'}
			]
		},
		# Low-power MCUs
		{'display': 'Low-power MCUs', 'id': 'lp', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/342/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/342/criteria?lang=en&output=json'}
			]
		},
			# Ultra-low Power
		{'display': 'Ultra-low Power', 'id': 'ulp', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/3274/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/3274/criteria?lang=en&output=json'}
			]
		},
		{'display': 'MSP430F1x', 'id': 'msp430f1x', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/911/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/911/criteria?lang=en&output=json'}
			]
		},
		{'display': 'MSP430F2x/4x', 'id': 'msp430f2x_4x', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/912/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/912/criteria?lang=en&output=json'}
			]
		},
		{'display': 'MSP430FRxx FRAM', 'id': 'msp430frxx', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1751/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1751/criteria?lang=en&output=json'}
			]
		},
		{'display': 'MSP430G2x', 'id': 'msp430g2x', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1937/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1937/criteria?lang=en&output=json'}
			]
		},
		{'display': 'MSP430L09x Low Voltage', 'id': 'msp430l09x', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1997/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1997/criteria?lang=en&output=json'}
			]
		},
			# Low Power + Performance
		{'display': 'Low Power + Performance', 'id': 'ulp_perf', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/3275/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/3275/criteria?lang=en&output=json'}
			]
		},
		{'display': 'MSP430F5x/6x', 'id': 'msp430f5x_6x', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1615/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1615/criteria?lang=en&output=json'}
			]
		},
			# Security + Communications
		{'display': 'Security + Communications', 'id': 'crypto_com', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/3276/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/3276/criteria?lang=en&output=json'}
			]
		},
		{'display': 'RF430', 'id': 'rf430', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1663/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1663/criteria?lang=en&output=json'}
			]
		},

		# Performance MCUs
		{'display': 'Performance MCUs', 'id': 'perf', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/3277/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/3277/criteria?lang=en&output=json'}
			],
			'ignore_categories': [r"^ram.*kb"]
		},

		# Real-time Control MCUs
		{'display': 'Real-time Control MCUs', 'id': 'realtime_ctrl', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/916/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/916/criteria?lang=en&output=json'}
			],
			'custom': {
				'CategoryDeviceTopFamily': 'c2000'
			}
		},

		{'display': 'Piccolo F2802x/3x/5x/6x MCUs', 'id': 'c28x_piccolo', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/919/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/919/criteria?lang=en&output=json'}
			],
			'custom': {
				'CategoryDeviceTopFamily': 'c2000',
				'CategoryDeviceFamily': 'c28x_piccolo'
			}
		},
		{'display': 'Delfino F2833x/F2837x MCUs', 'id': 'c28x_delfino', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1414/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1414/criteria?lang=en&output=json'}
			],
			'custom': {
				'CategoryDeviceTopFamily': 'c2000',
				'CategoryDeviceFamily': 'c28x_delfino'
			}
		},
		{'display': 'Fixed-point F280x/1x MCUs', 'id': 'c28x_fixedpoint', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1523/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1523/criteria?lang=en&output=json'}
			],
			'custom': {
				'CategoryDeviceTopFamily': 'c2000',
				'CategoryDeviceFamily': 'c28x_fixedpoint'
			}
		},

		# Control + Automation
		{'display': 'Control + Automation', 'id': 'control', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/3102/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/3102/criteria?lang=en&output=json'}
			],
			'ignore_categories': [r"^ram.*kb"]
		},
		{'display': 'TM4C12x', 'id': 'tm4c12x', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/3137/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/3137/criteria?lang=en&output=json'}
			],
			'custom': {
				'CategoryDeviceTopFamily': 'tm4c12x'
			}
		},
		{'display': 'F28M3x', 'id': 'f28m3x', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/2049/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/2049/criteria?lang=en&output=json'}
			],
			'custom': {
				'CategoryDeviceTopFamily': 'f28m3x'
			}
		},

		# Safety
		{'display': 'Safety MCUs', 'id': 'safety', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1931/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1931/criteria?lang=en&output=json'}
			]
		},
		{'display': 'Hercules RM MCUs', 'id': 'hercules_rm', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/2056/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/2056/criteria?lang=en&output=json'}
			],
			'custom': {
				'CategoryDeviceTopFamily': 'hercules',
				'CategoryDeviceFamily': 'rm'
			}
		},
		{'display': 'Hercules TMS570 MCUs', 'id': 'hercules_tms570', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1870/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1870/criteria?lang=en&output=json'}
			],
			'custom': {
				'CategoryDeviceTopFamily': 'hercules',
				'CategoryDeviceFamily': 'tms570'
			}
		},
		{'display': 'Hercules TMS470M MCUs', 'id': 'hercules_tms470m', 'data': [
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1999/results?lang=en&output=json'},
				{'url': 'http://www.ti.com/wsapi/paramdata/family/1999/criteria?lang=en&output=json'}
			],
			'custom': {
				'CategoryDeviceTopFamily': 'hercules',
				'CategoryDeviceFamily': 'tms470m'
			}
		},
	]
