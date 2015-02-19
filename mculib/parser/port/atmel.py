#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from mculib.parser.generic import *
from mculib.parser.deep import *

class AtmelCommon(GenericParserPort):
	@staticmethod
	def get_manufacturer():
		return "atmel"

	def setup_specific_parser_rules(self, parser):
		pass

	def setup_parser_rules(self, parser):
		"""
		Rules that applies specificly to Atmel
		"""
		def category_pre_processing_hook(category, options):
			"""
			CPU Cores
			"""
			# Empty values means 0
			category.consider_empty_values()
			if category.to_param() == "CategoryCPUCore":
				category.add_translation_table([
					[ r".*\b(avr32a.*rev.*1)\b.*", "avr32a_rev1" ],
					[ r".*\b(avr32a.*rev.*2)\b.*", "avr32a_rev2" ],
					[ r".*\b(avr32a.*rev.*3)\b.*", "avr32a_rev3" ],
					[ r".*\b(avr32b.*rev.*1)\b.*", "avr32b_rev1" ],
					[ r".*\b(avr32b.*rev.*2)\b.*", "avr32b_rev2" ],
					[ r".*\b(avr32b.*rev.*3)\b.*", "avr32b_rev3" ],
					[ r".*(xmega).*", "xmega_avr" ],
					[ r".*(mega).*", "mega_avr" ],
					[ r".*(tiny).*", "tiny_avr" ],
				])

		parser.hook("pre_category_discovery", category_pre_processing_hook)

		self.setup_specific_parser_rules(parser)

class AtmelParser(GenericParser):
	"""
	Data have the following format:
	{"payload":
		{"items":
			{"item":[
					{
						"buyurl": "http:\/\/www.stkcheck.com\/evs\/atmel\/atmelheader2.asp?mfg=atmel&part=AT32UC3A0128",
						"datasheeturl": "Images\/32058S.pdf",
						"description": "&#160;",
						"familyid": "33180",
						"familyname": "Atmel AVR 8- and 32-bit Microcontrollers",
						"id": 32131,
						"matureproduct": "0",
						"name": "AT32UC3A0128",
						"pm": [
							{"i": {"id": 92, "value": "LQFP RU 144,TFBGA 7U 144"} , "id": 9999} ,
							{"i": {"id": 12, "value": "128"} , "id": 8238} ,
							{"i": {"id": 12, "value": "144"} , "id": 8394} ,
							{"i": {"id": 18, "value": "66"} , "id": 8362} ,
							{"i": {"id": 0, "value": "32-bit AVR"} , "id": 8282} ,
							{"i": {"id": 20, "value": "32"} , "id": 8236} ,
							{"i": {"id": 0, "value": "No"} , "id": 8327} ,
							{"i": {"id": 52, "value": "109"} , "id": 8358} ,
							{"i": {"id": 46, "value": "109"} , "id": 8304} ,
							{"i": {"id": 1, "value": "1"} , "id": 8470} ,
							{"i": {"id": 1, "value": "Full Speed"} , "id": 8468} ,
							{"i": {"id": 2, "value": "Device + OTG"} , "id": 8466} ,
							{"i": {"id": 6, "value": "6"} , "id": 8429} ,
							{"i": {"id": 1, "value": "1"} , "id": 8458} ,
							{"i": {"id": 4, "value": "4"} , "id": 8462} ,
							{"i": {"id": 1, "value": "1"} , "id": 8433} ,
							{"i": {"id": 1, "value": "1"} , "id": 8302} ,
							{"i": {"id": 0, "value": "No"} , "id": 8325} ,
							{"i": {"id": 0, "value": "No"} , "id": 8472} ,
							{"i": {"id": 0, "value": "No"} , "id": 8276} ,
							{"i": {"id": 6, "value": "8"} , "id": 8254} ,
							{"i": {"id": 1, "value": "10"} , "id": 8256} ,
							{"i": {"id": 14, "value": "384"} , "id": 8258} ,
							{"i": {"id": 0, "value": "No"} , "id": 8413} ,
							{"i": {"id": 2, "value": "2"} , "id": 8286} ,
							...
						]
					},
					....
				],
			"items": "462",
			"page": "0",
			"pages": "10"
		} ,
		"keyparameters": {
			"pmc": [
				{"id": 8238} ,
				{"id": 8394} ,
				{"id": 8362} ,
				{"id": 8282}
			]
		} ,
		"parameterconfig": {
			"pmc": [
				{"display": "Slider", "id": 8238, "name": "Flash (Kbytes)", "order": "1", "unit": "Kbytes", "value": [{"id": 0, "name": "0"} , {"id": 1, "name": "0.5"} , {"id": 2, "name": "1"} , {"id": 3, "name": "2"} , {"id": 4, "name": "4"} , {"id": 5, "name": "8"} , {"id": 6, "name": "12"} , {"id": 7, "name": "16"} , {"id": 8, "name": "20"} , {"id": 9, "name": "32"} , {"id": 10, "name": "40"} , {"id": 11, "name": "64"} , {"id": 12, "name": "128"} , {"id": 13, "name": "192"} , {"id": 14, "name": "256"} , {"id": 15, "name": "384"} , {"id": 16, "name": "512"} , {"id": 17, "name": "1024"} , {"id": 18, "name": "2048"} ]} ,
				{"display": "Slider", "id": 8394, "name": "Pin Count", "order": "4", "unit": "", "value": [{"id": 0, "name": "6"} , {"id": 1, "name": "8"} , {"id": 2, "name": "14"} , {"id": 3, "name": "20"} , {"id": 4, "name": "24"} , {"id": 5, "name": "28"} , {"id": 6, "name": "32"} , {"id": 7, "name": "44"} , {"id": 8, "name": "48"} , {"id": 9, "name": "64"} , {"id": 10, "name": "100"} , {"id": 12, "name": "144"} , {"id": 13, "name": "176"} , {"id": 15, "name": "217"} , {"id": 17, "name": "256"} , {"id": 18, "name": "324"} ]} ,
				{"display": "Slider", "id": 8362, "name": "Max. Operating Frequency", "order": "5", "unit": "MHz", "value": [{"id": 1, "name": "1"} , {"id": 2, "name": "4"} , {"id": 3, "name": "8"} , {"id": 4, "name": "12"} , {"id": 5, "name": "16"} , {"id": 6, "name": "20"} , {"id": 7, "name": "24"} , {"id": 8, "name": "25"} , {"id": 9, "name": "32"} , {"id": 10, "name": "33"} , {"id": 11, "name": "36"} , {"id": 12, "name": "40"} , {"id": 13, "name": "48"} , {"id": 14, "name": "50"} , {"id": 15, "name": "55"} , {"id": 16, "name": "60"} , {"id": 17, "name": "64"} , {"id": 18, "name": "66"} , {"id": 19, "name": "75"} , {"id": 20, "name": "84"} , {"id": 21, "name": "96"} , {"id": 24, "name": "180"} , {"id": 25, "name": "210"} , {"id": 26, "name": "240"} , {"id": 27, "name": "266"} , {"id": 28, "name": "400"} ]} , {"display": "Checkbox", "id": 8282, "name": "CPU", "order": "8", "unit": "", "value": [{"id": 0, "name": "32-bit AVR"} , {"id": 1, "name": "8-bit AVR"} , {"id": 2, "name": "8051-12C"} , {"id": 3, "name": "8051-1C"} , {"id": 4, "name": "ARM7TDMI"} , {"id": 5, "name": "ARM920"} , {"id": 6, "name": "ARM926"} , {"id": 7, "name": "Cortex-M3"} , {"id": 8, "name": "Cortex-M4"} ]} , {"display": "Slider", "id": 8236, "name": "# of Touch Channels", "order": "12", "unit": "", "value": [{"id": 1, "name": "1"} , {"id": 2, "name": "3"} , {"id": 3, "name": "4"} , {"id": 4, "name": "5"} , {"id": 5, "name": "6"} , {"id": 7, "name": "8"} , {"id": 8, "name": "11"} , {"id": 9, "name": "12"} , {"id": 10, "name": "13"} , {"id": 11, "name": "14"} , {"id": 12, "name": "16"} , {"id": 13, "name": "17"} , {"id": 14, "name": "21"} , {"id": 15, "name": "23"} , {"id": 17, "name": "25"} , {"id": 18, "name": "28"} , {"id": 19, "name": "31"} , {"id": 20, "name": "32"} ]} , {"display": "Dropdown", "id": 8327, "name": "Hardware QTouch Acquisition", "order": "14", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Slider", "id": 8358, "name": "Max I\/O Pins", "order": "19", "unit": "", "value": [{"id": 1, "name": "4"} , {"id": 2, "name": "6"} , {"id": 3, "name": "11"} , {"id": 4, "name": "12"} , {"id": 5, "name": "14"} , {"id": 6, "name": "15"} , {"id": 7, "name": "16"} , {"id": 8, "name": "17"} , {"id": 9, "name": "18"} , {"id": 10, "name": "19"} , {"id": 11, "name": "20"} , {"id": 12, "name": "21"} , {"id": 13, "name": "22"} , {"id": 14, "name": "23"} , {"id": 15, "name": "26"} , {"id": 16, "name": "27"} , {"id": 17, "name": "28"} , {"id": 18, "name": "30"} , {"id": 19, "name": "32"} , {"id": 20, "name": "34"} , {"id": 21, "name": "35"} , {"id": 22, "name": "36"} , {"id": 23, "name": "37"} , {"id": 24, "name": "38"} , {"id": 25, "name": "42"} , {"id": 26, "name": "43"} , {"id": 27, "name": "44"} , {"id": 28, "name": "45"} , {"id": 29, "name": "47"} , {"id": 30, "name": "48"} , {"id": 31, "name": "49"} , {"id": 32, "name": "50"} , {"id": 33, "name": "51"} , {"id": 34, "name": "53"} , {"id": 35, "name": "54"} , {"id": 36, "name": "57"} , {"id": 37, "name": "58"} , {"id": 38, "name": "62"} , {"id": 39, "name": "63"} , {"id": 40, "name": "69"} , {"id": 41, "name": "75"} , {"id": 42, "name": "78"} , {"id": 43, "name": "79"} , {"id": 44, "name": "80"} , {"id": 45, "name": "81"} , {"id": 46, "name": "86"} , {"id": 47, "name": "88"} , {"id": 48, "name": "96"} , {"id": 49, "name": "103"} , {"id": 50, "name": "105"} , {"id": 52, "name": "109"} , {"id": 53, "name": "110"} , {"id": 54, "name": "118"} , {"id": 56, "name": "122"} , {"id": 57, "name": "123"} , {"id": 60, "name": "160"} ]} , {"display": "Slider", "id": 8304, "name": "Ext Interrupts", "order": "22", "unit": "", "value": [{"id": 0, "name": "2"} , {"id": 1, "name": "3"} , {"id": 2, "name": "4"} , {"id": 3, "name": "6"} , {"id": 4, "name": "8"} , {"id": 5, "name": "10"} , {"id": 6, "name": "11"} , {"id": 7, "name": "12"} , {"id": 8, "name": "13"} , {"id": 9, "name": "15"} , {"id": 10, "name": "16"} , {"id": 11, "name": "17"} , {"id": 12, "name": "18"} , {"id": 13, "name": "20"} , {"id": 14, "name": "21"} , {"id": 15, "name": "24"} , {"id": 16, "name": "25"} , {"id": 17, "name": "27"} , {"id": 18, "name": "28"} , {"id": 19, "name": "32"} , {"id": 20, "name": "34"} , {"id": 21, "name": "36"} , {"id": 22, "name": "43"} , {"id": 23, "name": "44"} , {"id": 24, "name": "47"} , {"id": 25, "name": "48"} , {"id": 26, "name": "49"} , {"id": 27, "name": "50"} , {"id": 28, "name": "51"} , {"id": 29, "name": "53"} , {"id": 30, "name": "54"} , {"id": 31, "name": "57"} , {"id": 32, "name": "58"} , {"id": 33, "name": "62"} , {"id": 34, "name": "63"} , {"id": 35, "name": "64"} , {"id": 36, "name": "69"} , {"id": 37, "name": "75"} , {"id": 38, "name": "78"} , {"id": 39, "name": "79"} , {"id": 40, "name": "80"} , {"id": 41, "name": "88"} , {"id": 42, "name": "96"} , {"id": 43, "name": "100"} , {"id": 44, "name": "103"} , {"id": 45, "name": "105"} , {"id": 46, "name": "109"} , {"id": 47, "name": "110"} , {"id": 48, "name": "118"} , {"id": 49, "name": "122"} , {"id": 50, "name": "144"} , {"id": 51, "name": "160"} ]} , {"display": "Checkbox", "id": 8470, "name": "USB Transceiver", "order": "29", "unit": "", "value": [{"id": 1, "name": "1"} , {"id": 2, "name": "2"} , {"id": 3, "name": "3"} ]} , {"display": "Checkbox", "id": 8404, "name": "Quadrature Decoder Channels", "order": "31", "unit": "", "value": [{"id": 0, "name": "0"} , {"id": 1, "name": "1"} , {"id": 2, "name": "2"} ]} , {"display": "Checkbox", "id": 8468, "name": "USB Speed", "order": "36", "unit": "", "value": [{"id": 1, "name": "Full Speed"} , {"id": 2, "name": "Hi-Speed"} , {"id": 3, "name": "No"} ]} , {"display": "Checkbox", "id": 8466, "name": "USB Interface", "order": "37", "unit": "", "value": [{"id": 1, "name": "Device"} , {"id": 2, "name": "Device + OTG"} , {"id": 3, "name": "Host, Device"} , {"id": 4, "name": "No"} ]} , {"display": "Slider", "id": 8429, "name": "SPI", "order": "38", "unit": "", "value": [{"id": 1, "name": "1"} , {"id": 2, "name": "2"} , {"id": 3, "name": "3"} , {"id": 4, "name": "4"} , {"id": 5, "name": "5"} , {"id": 6, "name": "6"} , {"id": 7, "name": "7"} , {"id": 8, "name": "8"} , {"id": 9, "name": "10"} , {"id": 10, "name": "12"} ]} , {"display": "Slider", "id": 8458, "name": "TWI (I2C)", "order": "39", "unit": "", "value": [{"id": 0, "name": "0"} , {"id": 1, "name": "1"} , {"id": 2, "name": "2"} , {"id": 3, "name": "3"} , {"id": 4, "name": "4"} ]} , {"display": "Slider", "id": 8462, "name": "UART", "order": "40", "unit": "", "value": [{"id": 0, "name": "0"} , {"id": 1, "name": "1"} , {"id": 2, "name": "2"} , {"id": 3, "name": "3"} , {"id": 4, "name": "4"} , {"id": 5, "name": "5"} , {"id": 6, "name": "6"} , {"id": 7, "name": "7"} , {"id": 8, "name": "8"} ]} , {"display": "Checkbox", "id": 8278, "name": "CAN", "order": "41", "unit": "", "value": [{"id": 1, "name": "1"} , {"id": 2, "name": "2"} ]} , {"display": "Slider", "id": 8347, "name": "LIN", "order": "42", "unit": "", "value": [{"id": 1, "name": "1"} , {"id": 2, "name": "3"} , {"id": 3, "name": "4"} , {"id": 4, "name": "5"} ]} , {"display": "Slider", "id": 8433, "name": "SSC", "order": "43", "unit": "", "value": [{"id": 1, "name": "1"} , {"id": 2, "name": "2"} , {"id": 3, "name": "3"} ]} , {"display": "Checkbox", "id": 8302, "name": "Ethernet", "order": "44", "unit": "", "value": [{"id": 1, "name": "1"} , {"id": 2, "name": "2"} ]} , {"display": "Slider", "id": 8417, "name": "SD \/ eMMC", "order": "45", "unit": "", "value": [{"id": 1, "name": "1"} , {"id": 2, "name": "2"} ]} , {"display": "Checkbox", "id": 8419, "name": "Segment LCD", "order": "46", "unit": "", "value": [{"id": 1, "name": "13"} , {"id": 2, "name": "23"} , {"id": 3, "name": "100"} , {"id": 4, "name": "160"} , {"id": 5, "name": "40"} ]} , {"display": "Checkbox", "id": 8325, "name": "Graphic LCD", "order": "47", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Checkbox", "id": 8472, "name": "Video Decoder", "order": "48", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Checkbox", "id": 8276, "name": "Camera Interface", "order": "49", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Slider", "id": 8254, "name": "ADC channels", "order": "50", "unit": "", "value": [{"id": 1, "name": "2"} , {"id": 2, "name": "3"} , {"id": 3, "name": "4"} , {"id": 4, "name": "6"} , {"id": 5, "name": "7"} , {"id": 6, "name": "8"} , {"id": 7, "name": "10"} , {"id": 8, "name": "11"} , {"id": 9, "name": "12"} , {"id": 10, "name": "15"} , {"id": 11, "name": "16"} , {"id": 12, "name": "28"} ]} , {"display": "Checkbox", "id": 8256, "name": "ADC Resolution (bits)", "order": "51", "unit": "", "value": [{"id": 1, "name": "10"} , {"id": 2, "name": "12"} , {"id": 3, "name": "8"} ]} , {"display": "Slider", "id": 8258, "name": "ADC Speed (ksps)", "order": "52", "unit": "", "value": [{"id": 1, "name": "1.9"} , {"id": 2, "name": "15"} , {"id": 3, "name": "22.7"} , {"id": 4, "name": "50"} , {"id": 5, "name": "62.5"} , {"id": 6, "name": "72"} , {"id": 7, "name": "95"} , {"id": 8, "name": "125"} , {"id": 9, "name": "153.8"} , {"id": 10, "name": "200"} , {"id": 11, "name": "220"} , {"id": 12, "name": "300"} , {"id": 13, "name": "312"} , {"id": 14, "name": "384"} , {"id": 15, "name": "440"} , {"id": 16, "name": "460"} , {"id": 17, "name": "1000"} , {"id": 18, "name": "2000"} ]} , {"display": "Slider", "id": 8264, "name": "Analog Comparators", "order": "53", "unit": "", "value": [{"id": 1, "name": "1"} , {"id": 2, "name": "2"} , {"id": 3, "name": "3"} , {"id": 4, "name": "4"} , {"id": 5, "name": "8"} ]} , {"display": "Checkbox", "id": 8413, "name": "Resistive Touch Screen", "order": "54", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Slider", "id": 8286, "name": "DAC Channels", "order": "55", "unit": "", "value": [{"id": 0, "name": "0"} , {"id": 1, "name": "1"} , {"id": 2, "name": "2"} , {"id": 3, "name": "4"} ]} , {"display": "Checkbox", "id": 8288, "name": "DAC Resolution (bits)", "order": "56", "unit": "", "value": [{"id": 0, "name": "0"} , {"id": 1, "name": "10"} , {"id": 2, "name": "12"} , {"id": 3, "name": "16"} , {"id": 4, "name": "No"} ]} , {"display": "Checkbox", "id": 8447, "name": "Temp. Sensor", "order": "57", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Checkbox", "id": 8284, "name": "Crypto Engine", "order": "58", "unit": "", "value": [{"id": 0, "name": "AES"} , {"id": 1, "name": "AES\/DES"} , {"id": 2, "name": "No"} ]} , {"display": "Slider", "id": 8431, "name": "SRAM (Kbytes)", "order": "59", "unit": "", "value": [{"id": 0, "name": "0"} , {"id": 1, "name": "0.03"} , {"id": 2, "name": "0.06"} , {"id": 3, "name": "0.12"} , {"id": 4, "name": "0.125"} , {"id": 5, "name": "0.25"} , {"id": 6, "name": "0.5"} , {"id": 7, "name": "0.75"} , {"id": 8, "name": "1"} , {"id": 9, "name": "1.25"} , {"id": 10, "name": "1.375"} , {"id": 11, "name": "2"} , {"id": 12, "name": "2.1"} , {"id": 13, "name": "2.25"} , {"id": 14, "name": "2.5"} , {"id": 15, "name": "3.3"} , {"id": 16, "name": "4"} , {"id": 17, "name": "4.25"} , {"id": 18, "name": "6"} , {"id": 19, "name": "8"} , {"id": 21, "name": "8.25"} , {"id": 22, "name": "16"} , {"id": 23, "name": "20"} , {"id": 24, "name": "24"} , {"id": 25, "name": "32"} , {"id": 26, "name": "36"} , {"id": 27, "name": "48"} , {"id": 28, "name": "50"} , {"id": 29, "name": "64"} , {"id": 30, "name": "68"} , {"id": 31, "name": "96"} , {"id": 32, "name": "128"} , {"id": 33, "name": "160"} , {"id": 34, "name": "256"} , {"id": 35, "name": "512"} ]} , {"display": "Slider", "id": 8300, "name": "EEPROM (Bytes)", "order": "60", "unit": "", "value": [{"id": 1, "name": "0"} , {"id": 2, "name": "64"} , {"id": 3, "name": "128"} , {"id": 4, "name": "256"} , {"id": 5, "name": "512"} , {"id": 6, "name": "1024"} , {"id": 7, "name": "2048"} , {"id": 8, "name": "4096"} , {"id": 9, "name": "8192"} ]} , {"display": "Dropdown", "id": 8421, "name": "Self Program Memory", "order": "61", "unit": "", "value": [{"id": 0, "name": "API"} , {"id": 1, "name": "IAP"} , {"id": 2, "name": "NO"} , {"id": 3, "name": "YES"} ]} , {"display": "Checkbox", "id": 8306, "name": "External Bus Interface", "order": "62", "unit": "", "value": [{"id": 0, "name": "0"} , {"id": 1, "name": "1"} , {"id": 2, "name": "2"} ]} , {"display": "Dropdown", "id": 8298, "name": "DRAM Memory", "order": "63", "unit": "", "value": [{"id": 1, "name": "DDR2\/LPDDR, SDRAM\/LPSDR"} , {"id": 2, "name": "No"} , {"id": 3, "name": "sdram"} ]} , {"display": "Checkbox", "id": 8370, "name": "NAND Interface", "order": "64", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Checkbox", "id": 8392, "name": "picoPower", "order": "65", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Checkbox", "id": 8445, "name": "Temp. Range (deg C)", "order": "66", "unit": "", "value": [{"id": 0, "name": "-20 to 85"} , {"id": 2, "name": "-30 to 85"} , {"id": 3, "name": "-40 to 105"} , {"id": 4, "name": "-40 to 125"} , {"id": 5, "name": "-40 to 150"} , {"id": 6, "name": "-40 to 85"} ]} , {"display": "Dropdown", "id": 8331, "name": "I\/O Supply Class", "order": "67", "unit": "", "value": [{"id": 0, "name": "0.7 to 5.5"} , {"id": 1, "name": "1.6 to 3.6"} , {"id": 2, "name": "1.62 to 3.6"} , {"id": 3, "name": "1.62\/3.6"} , {"id": 4, "name": "1.7 to 5.5"} , {"id": 5, "name": "1.8 to 5.5"} , {"id": 6, "name": "1.8 to 9.0"} , {"id": 7, "name": "1.8\/3.3"} , {"id": 8, "name": "2.7 to 5.5"} , {"id": 9, "name": "3.0 to 3.6"} , {"id": 10, "name": "3.0 to 3.6 or 4.5 to 5.5"} , {"id": 11, "name": "3.0-3.6 or (1.65-1.95+3.0-3.6)"} , {"id": 12, "name": "3.3"} , {"id": 13, "name": "3.3\/5.0"} , {"id": 14, "name": "4.0 to 25"} ]} , {"display": "Dropdown", "id": 8378, "name": "Operating Voltage (Vcc)", "order": "68", "unit": "", "value": [{"id": 0, "name": "0.7 to 5.5"} , {"id": 1, "name": "0.9 to 1.1"} , {"id": 2, "name": "1.08 to 1.32"} , {"id": 5, "name": "1.6 to 3.6"} , {"id": 6, "name": "1.62 to 3.6"} , {"id": 8, "name": "1.65 to 1.95"} , {"id": 10, "name": "1.68 to 3.6"} , {"id": 13, "name": "1.7 to 5.5"} , {"id": 17, "name": "1.8 to 3.6"} , {"id": 18, "name": "1.8 to 5.5"} , {"id": 19, "name": "1.8 to 9.0"} , {"id": 31, "name": "2.4 to 3.6"} , {"id": 33, "name": "2.4 to 5.0"} , {"id": 34, "name": "2.4 to 5.5"} , {"id": 39, "name": "2.7 to 3.6"} , {"id": 41, "name": "2.7 to 5.5"} , {"id": 42, "name": "2.7 to 4.0"} , {"id": 43, "name": "2.7 to 6.0"} , {"id": 50, "name": "3.0 to 3.6"} , {"id": 51, "name": "3.0 to 3.6 or 4.5 to 5.5"} , {"id": 52, "name": "3.0 to 5.5"} , {"id": 55, "name": "3.0-3.6 or (1.65-1.95+3.0-3.6)"} , {"id": 61, "name": "4.0 to 25"} , {"id": 62, "name": "4.0 to 5.5"} , {"id": 63, "name": "4.0 to 6.0"} ]} , {"display": "Checkbox", "id": 8319, "name": "FPU", "order": "69", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Dropdown", "id": 8368, "name": "MPU \/ MMU", "order": "70", "unit": "", "value": [{"id": 0, "name": "no \/ no"} , {"id": 1, "name": "No \/ Yes"} , {"id": 2, "name": "No\/Yes"} , {"id": 3, "name": "Yes \/ No"} ]} , {"display": "Slider", "id": 8449, "name": "Timers", "order": "71", "unit": "", "value": [{"id": 0, "name": "0"} , {"id": 1, "name": "1"} , {"id": 2, "name": "2"} , {"id": 3, "name": "3"} , {"id": 4, "name": "4"} , {"id": 5, "name": "5"} , {"id": 6, "name": "6"} , {"id": 7, "name": "7"} , {"id": 8, "name": "8"} , {"id": 9, "name": "9"} , {"id": 10, "name": "10"} ]} , {"display": "Slider", "id": 8386, "name": "Output Compare channels", "order": "72", "unit": "", "value": [{"id": 0, "name": "0"} , {"id": 1, "name": "2"} , {"id": 2, "name": "3"} , {"id": 3, "name": "4"} , {"id": 4, "name": "5"} , {"id": 5, "name": "6"} , {"id": 6, "name": "8"} , {"id": 7, "name": "9"} , {"id": 8, "name": "10"} , {"id": 9, "name": "12"} , {"id": 10, "name": "13"} , {"id": 11, "name": "14"} , {"id": 12, "name": "16"} , {"id": 13, "name": "18"} , {"id": 14, "name": "22"} , {"id": 15, "name": "24"} ]} , {"display": "Slider", "id": 8333, "name": "Input Capture Channels", "order": "73", "unit": "", "value": [{"id": 0, "name": "0"} , {"id": 1, "name": "1"} , {"id": 2, "name": "2"} , {"id": 3, "name": "3"} , {"id": 4, "name": "4"} , {"id": 5, "name": "6"} , {"id": 6, "name": "9"} , {"id": 7, "name": "10"} , {"id": 8, "name": "12"} , {"id": 9, "name": "14"} , {"id": 10, "name": "16"} , {"id": 11, "name": "18"} , {"id": 12, "name": "22"} , {"id": 13, "name": "24"} ]} , {"display": "Slider", "id": 8400, "name": "PWM Channels", "order": "74", "unit": "", "value": [{"id": 0, "name": "0"} , {"id": 1, "name": "2"} , {"id": 2, "name": "3"} , {"id": 3, "name": "4"} , {"id": 4, "name": "6"} , {"id": 5, "name": "7"} , {"id": 6, "name": "8"} , {"id": 7, "name": "9"} , {"id": 8, "name": "10"} , {"id": 9, "name": "12"} , {"id": 10, "name": "13"} , {"id": 11, "name": "14"} , {"id": 12, "name": "15"} , {"id": 13, "name": "16"} , {"id": 14, "name": "18"} , {"id": 15, "name": "19"} , {"id": 16, "name": "20"} , {"id": 17, "name": "22"} , {"id": 18, "name": "24"} , {"id": 19, "name": "35"} , {"id": 20, "name": "36"} ]} , {"display": "Checkbox", "id": 8248, "name": "32kHz RTC", "order": "75", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Checkbox", "id": 8274, "name": "Calibrated RC Oscillator", "order": "76", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Checkbox", "id": 8337, "name": "ISP", "order": "77", "unit": "", "value": [{"id": 0, "name": "SPI"} , {"id": 1, "name": "SPI\/OCD"} , {"id": 2, "name": "SPI\/OCD\/UART"} , {"id": 3, "name": "UART"} , {"id": 4, "name": "UART\/CAN"} , {"id": 5, "name": "UART\/OCD"} , {"id": 6, "name": "UART\/USB"} ]} , {"display": "Slider", "id": 8352, "name": "Mask ROM (Kbytes)", "order": "79", "unit": "", "value": [{"id": 0, "name": "4"} , {"id": 1, "name": "8"} , {"id": 2, "name": "16"} , {"id": 3, "name": "32"} ]} , {"display": "Checkbox", "id": 8474, "name": "Watchdog", "order": "80", "unit": "", "value": {"id": 0, "name": "Yes"} } , {"display": "Checkbox", "id": 8321, "name": "Frequency Band", "order": "81", "unit": "", "value": [{"id": 2, "name": "2.4 GHz"} , {"id": 5, "name": "700\/800\/900MHz"} ]} , {"display": "Checkbox", "id": 8356, "name": "Max Data Rate (Mb\/s)", "order": "82", "unit": "", "value": [{"id": 0, "name": "0.25"} , {"id": 1, "name": "1"} , {"id": 2, "name": "2"} ]} , {"display": "Checkbox", "id": 8266, "name": "Antenna Diversity", "order": "83", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Checkbox", "id": 8308, "name": "External PA Control", "order": "84", "unit": "", "value": [{"id": 0, "name": "No"} , {"id": 1, "name": "Yes"} ]} , {"display": "Checkbox", "id": 8398, "name": "Power Output (dBm)", "order": "85", "unit": "", "value": [{"id": 0, "name": "10"} , {"id": 1, "name": "3"} , {"id": 2, "name": "3.5"} , {"id": 3, "name": "4"} ]} , {"display": "Checkbox", "id": 8409, "name": "Receiver Sensitivity (dBm)", "order": "86", "unit": "", "value": [{"id": 0, "name": "-100"} , {"id": 1, "name": "-101"} , {"id": 2, "name": "-110"} ]} , {"display": "Checkbox", "id": 8241, "name": "Receive Current Consumption (mA)", "order": "87", "unit": "", "value": [{"id": 0, "name": "6.0"} , {"id": 1, "name": "9.0"} , {"id": 2, "name": "11.8"} , {"id": 3, "name": "12.5"} , {"id": 4, "name": "13.2"} , {"id": 5, "name": "16.0"} , {"id": 6, "name": "16.6"} ]} , {"display": "Checkbox", "id": 8243, "name": "Transmit Current Consumption (mA)", "order": "88", "unit": "", "value": [{"id": 0, "name": "13.8"} , {"id": 1, "name": "14.4"} , {"id": 2, "name": "14.5"} , {"id": 3, "name": "17.0"} , {"id": 4, "name": "18 at 5dBm"} , {"id": 5, "name": "18.6"} ]} , {"display": "Checkbox", "id": 8239, "name": "Link Budget (dBm)", "order": "89", "unit": "", "value": [{"id": 0, "name": "103"} , {"id": 1, "name": "103.5"} , {"id": 2, "name": "104"} , {"id": 3, "name": "120"} , {"id": 4, "name": "105"} ]} , {"display": "Dropdown", "id": 9999, "name": "Packages", "order": "153", "unit": "", "value": [{"id": 5, "name": "CBGA 100C1 100,TQFP 100A 100"} , {"id": 6, "name": "CBGA 100C1 100,TQFP 100A 100,VFBGA 100C2 100 (10x10)"} , {"id": 36, "name": "LBGA R-LBGA144_E 144,LQFP R-LQ144_D 144"} , {"id": 38, "name": "LFBGA R-LFBGA144_H 144,LQFP R-LQ128_E 128"} , {"id": 39, "name": "LFBGA R-LFBGA144_J 144"} , {"id": 40, "name": "LFBGA R-LFBGA144_K 144,LQFP R-LQ128_H 128"} , {"id": 41, "name": "LFBGA R-LFBGA176_E 176,LQFP R-LQ176_D 176"} , {"id": 42, "name": "LFBGA R-LFBGA217_B 217"} , {"id": 43, "name": "LFBGA R-LFBGA217_B 217,PQFP R-SQ208_I 208"} , {"id": 44, "name": "LFBGA R-LFBGA217_F 217"} , {"id": 45, "name": "LFBGA R-LFBGA217_H 217,PQFP R-SQ208_I 208"} , {"id": 46, "name": "LFBGA R-LFBGA217_J 217"} , {"id": 47, "name": "LFBGA R-LFBGA217_L 217"} , {"id": 48, "name": "LFBGA R-LFBGA217_V 217"} , {"id": 49, "name": "LFBGA R-LFBGA256_B 256,PQFP R-SQ208_H 208"} , {"id": 50, "name": "LGA 36CK1 36 (8x5),TSOP 28T 28"} , {"id": 51, "name": "LQFP 144AA 144"} , {"id": 52, "name": "LQFP 144AA 144,TFBGA 7U 144"} , {"id": 56, "name": "LQFP 48AA 48"} , {"id": 57, "name": "LQFP RA 32,PLCC SI 28,SOIC TI 28"} , {"id": 58, "name": "LQFP RD 64,LQFP RL 44,PLCC S3 52,PLCC SL 44"} , {"id": 59, "name": "LQFP RD 64,LQFP RL 44,PLCC SL 44,PLCC SM 68"} , {"id": 60, "name": "LQFP RD 64,PLCC S3 52,SOIC TI 28"} , {"id": 61, "name": "LQFP RD 64,PLCC S3 52,VQFN (Punched) PU 32"} , {"id": 62, "name": "LQFP RD 64,VQFN (Sawn) PJ 64"} , {"id": 64, "name": "LQFP RL 44,MLF (VQFN) 44M1 44,PDIP 3C 40,PLCC SL 44,TQFP 44A 44"} , {"id": 65, "name": "LQFP RL 44,MLF (VQFN) 44M1 44,PLCC SL 44,TQFP 44A 44"} , {"id": 66, "name": "LQFP RL 44,PDIP 3C 40,PLCC SL 44"} , {"id": 67, "name": "LQFP RL 44,PLCC SL 44"} , {"id": 68, "name": "LQFP R-LQ048_B 48,QFN R-QFN048_B 48"} , {"id": 69, "name": "LQFP R-LQ048_E 48"} , {"id": 70, "name": "LQFP R-LQ048_E 48,QFN R-QFN048_F 48"} , {"id": 71, "name": "LQFP R-LQ064_B 64,QFN R-QFN064_B 64"} , {"id": 72, "name": "LQFP R-LQ064_C 64,QFN R-QFN064_B 64"} , {"id": 73, "name": "LQFP R-LQ064_E 64"} , {"id": 74, "name": "LQFP R-LQ064_E 64,QFN R-QFN064_B 64"} , {"id": 75, "name": "LQFP R-LQ064_K - 64 - RFO"} , {"id": 76, "name": "LQFP R-LQ064_K - 64 - RFO,QFN R-QFN064_B 64"} , {"id": 77, "name": "LQFP R-LQ100_A 100"} , {"id": 78, "name": "LQFP R-LQ100_H 100"} , {"id": 79, "name": "LQFP R-LQ100_H 100,TFBGA R-TFBGA100_P 100"} , {"id": 80, "name": "LQFP R-LQ100_I 100,TFBGA R-TFBGA100_P 100"} , {"id": 81, "name": "LQFP R-LQ100_M 100"} , {"id": 82, "name": "LQFP R-LQ100_M 100,TFBGA R-TFBGA100_S 100"} , {"id": 83, "name": "LQFP R-LQ100_O 100"} , {"id": 89, "name": "LQFP R-LQ144_H 144"} , {"id": 90, "name": "LQFP RO 80"} , {"id": 92, "name": "LQFP RU 144,TFBGA 7U 144"} , {"id": 93, "name": "MLF (VDFN) 10M1 10,MLF (WQFN) 20M1 20,PDIP 8P3 8,SOIC (150mil) 8S1 8,SOIC (208mil) 8S2 8"} , {"id": 98, "name": "MLF (VQFN) 28M1 28,MLF (VQFN) 32M1-A 32,PDIP 28P3 28,TQFP 32A 32"} , {"id": 99, "name": "MLF (VQFN) 28M1 28,MLF (VQFN) 32M1-A 32,PDIP 28P3 28,TQFP 32A 32,UFBGA 32CC1 32 (6x6)"} , {"id": 100, "name": "MLF (VQFN) 28M1 28,PDIP 28P3 28,TQFP 32A 32,UFBGA 32CC1 32 (6x6)"} , {"id": 101, "name": "MLF (VQFN) 32M1-A 32,PDIP 20P3 20,SOIC (300mil) 20S 20"} , {"id": 102, "name": "MLF (VQFN) 32M1-A 32,PDIP 20P3 20,SOIC (300mil) 20S2 20"} , {"id": 103, "name": "MLF (VQFN) 32M1-A 32,PDIP 20P3 20,SOIC (300mil) 20S2 20,TSSOP 6G 20"} , {"id": 104, "name": "MLF (VQFN) 32M1-A 32,PDIP 28P3 28,PLCC 32J 32,TQFP 32A 32"} , {"id": 105, "name": "MLF (VQFN) 32M1-A 32,PDIP 28P3 28,TQFP 32A 32"} , {"id": 106, "name": "MLF (VQFN) 32M1-A 32,PDIP 28P3 28,TQFP 32A 32,UFBGA 32CC1 32 (6x6)"} , {"id": 107, "name": "MLF (VQFN) 32M1-A 32,SOIC TG 20,TSSOP 6G 20"} , {"id": 108, "name": "MLF (VQFN) 32M1-A 32,TQFP 32A 32"} , {"id": 109, "name": "MLF (VQFN) 44M1 44"} , {"id": 110, "name": "MLF (VQFN) 44M1 44,PDIP 40P6 40,PLCC 44J 44,TQFP 44A 44"} , {"id": 111, "name": "MLF (VQFN) 44M1 44,PDIP 40P6 40,QFN 44MC 44,TQFP 44A 44"} , {"id": 112, "name": "MLF (VQFN) 44M1 44,PDIP 40P6 40,QFN 44MC 44,TQFP 44A 44,VFBGA 49C2 49"} , {"id": 113, "name": "MLF (VQFN) 44M1 44,PDIP 40P6 40,TQFP 44A 44"} , {"id": 114, "name": "MLF (VQFN) 44M1 44,TQFP 44A 44"} , {"id": 115, "name": "MLF (VQFN) 44M1 44,TQFP 44A 44,VFBGA 49C2 49"} , {"id": 116, "name": "MLF (VQFN) 64M1 64"} , {"id": 117, "name": "MLF (VQFN) 64M1 64,MLF (VQFN) 64M2 64,TQFP 64A 64"} , {"id": 118, "name": "MLF (VQFN) 64M1 64,QFN 64MC 64,TQFP 64A 64"} , {"id": 119, "name": "MLF (VQFN) 64M1 64,TQFP 64A 64"} , {"id": 120, "name": "MLF (VQFN) 64M2 64,TQFP 64A 64"} , {"id": 121, "name": "MLF (WQFN) 20M1 20,PDIP 14P3 14,SOIC (150mil) 14S1 14"} , {"id": 122, "name": "MLF (WQFN) 20M1 20,PDIP 14P3 14,SOIC (150mil) 14S1 14,SOIC 14S1 14"} , {"id": 123, "name": "MLF (WQFN) 20M1 20,PDIP 14P3 14,SOIC (150mil) 14S1 14,SOIC 14S1 14,UFBGA 15CC1 15,VQFN 20M2 20"} , {"id": 124, "name": "MLF (WQFN) 20M1 20,PDIP 14P3 14,SOIC (150mil) 14S1 14,UFBGA 15CC1 15,VQFN 20M2 20"} , {"id": 125, "name": "MLF (WQFN) 20M1 20,PDIP 20P3 20,SOIC (300mil) 20S 20"} , {"id": 126, "name": "MLF (WQFN) 20M1 20,PDIP 20P3 20,SOIC (300mil) 20S 20,VQFN 20M2 20"} , {"id": 127, "name": "MLF (WQFN) 20M1 20,PDIP 8P3 8,SOIC (150mil) 8S1 8,SOIC (208mil) 8S2 8"} , {"id": 128, "name": "MLF (WQFN) 20M1 20,PDIP 8P3 8,SOIC (208mil) 8S2 8"} , {"id": 129, "name": "MLF (WQFN) 20M1 20,PDIP 8P3 8,SOIC (208mil) 8S2 8,TSSOP 8X 8"} , {"id": 130, "name": "MLF (WQFN) 20M1 20,SOIC (300mil) 20S2 20"} , {"id": 132, "name": "PDIP 14P3 14,TSSOP 14X 14"} , {"id": 133, "name": "PDIP 16P3 16,TSSOP 16X 16"} , {"id": 138, "name": "PDIP 20P3 20,SOIC 20S2 20"} , {"id": 139, "name": "PDIP 20P3 20,SOIC 20S2 20,TSSOP 20X 20"} , {"id": 149, "name": "PDIP 40P6 40,PLCC 44J 44,TQFP 44A 44"} , {"id": 198, "name": "QFN PL 48"} , {"id": 200, "name": "QFN PN 32,SO TG 20"} , {"id": 201, "name": "QFN PN 32,SOIC TD 24"} , {"id": 206, "name": "QFN R-QFN048_E 48"} , {"id": 207, "name": "QFN R-QFN064_B 64,TQFP 64A 64"} , {"id": 208, "name": "QFN WG 48"} , {"id": 209, "name": "QFN WN 32"} , {"id": 216, "name": "SOIC (150mil) 14S1 14,TSSOP 14X 14,UFBGA 15CC1 15,VQFN 20M2 20,WLCSP 12U1 12"} , {"id": 217, "name": "SOIC (150mil) 14S1 14,TSSOP 20X 20,VQFN 20M2 20"} , {"id": 250, "name": "SOIC T4 32,VQFN (Punched) PU 32"} , {"id": 251, "name": "SOIC TD 24"} , {"id": 252, "name": "SOIC TG 20"} , {"id": 253, "name": "SOIC TG 20,TSSOP 6G 20,VQFN (Sawn) PN 32"} , {"id": 255, "name": "SOIC TU 14,VQFN (Sawn) PC 20"} , {"id": 256, "name": "SOIC-EIAJ T5 8,VQFN (Sawn) PC 20"} , {"id": 257, "name": "SOT23 6ST1 6,UDFN \/ USON 8MA4 8"} , {"id": 262, "name": "TFBGA R-TFBGA324_H 324"} , {"id": 263, "name": "TQFP 100A 100"} , {"id": 265, "name": "TQFP 32A 32"} , {"id": 266, "name": "TQFP 32A 32,VQFN (Sawn) PN 32"} , {"id": 268, "name": "TQFP 64A 64"} , {"id": 269, "name": "TQFP 64A 64,TQFP MF 64"} , {"id": 270, "name": "TQFP 64A 64,VQFN (Sawn) PJ 64"} , {"id": 271, "name": "TQFP MA 32,VQFN (Sawn) PN 32"} , {"id": 272, "name": "TQFP MA 32,VQFN (Sawn) PV 32"} , {"id": 273, "name": "TQFP MC 48,ULGA AA 48,VQFN (Sawn) PE 48"} , {"id": 274, "name": "TQFP MC 48,VQFN (Punched) PL 48"} , {"id": 275, "name": "TQFP MC 48,VQFN (Sawn) PE 48"} , {"id": 276, "name": "TQFP MD 64,VQFN (Sawn) PS 64"} , {"id": 277, "name": "TQFP MF 64,VQFN (Sawn) PJ 64"} , {"id": 278, "name": "TQFP MF 64,VQFN (Sawn) PS 64"} , {"id": 279, "name": "TQFP ML 44,VQFN (Sawn) PN 32"} , {"id": 280, "name": "TQFP ML 44,VQFN (Sawn) PW 44"} , {"id": 281, "name": "TQFP MT 100"} , {"id": 282, "name": "TQFP MT 100,VFBGA 7A 100"} , {"id": 285, "name": "TSSOP 44X1 44"} , {"id": 292, "name": "VQFN (Punched) PL 48"} , {"id": 293, "name": "VQFN (Sawn) PC 20"} , {"id": 294, "name": "VQFN (Sawn) PI 64"} , {"id": 295, "name": "VQFN (Sawn) PN 32"} , {"id": 297, "name": "VQFN 32QN1 32"} ]} ], "version": "2012-11-19 T13:06:01"} } } )
	"""
	current = 0
	total = 0

	def parse_deep(self, json_data):
		# Fill in the parameter values
		for i, device in enumerate(json_data["payload"]["items"]["item"]):
			self.element_create()
			if not device.has_key("pm") or not device.has_key("name"):
				continue
			# Add the name
			device_name = device["name"]
			self.element_add_value(device_name, "device name")
			# Add the datasheet URL
			if "datasheeturl" in device:
				datasheet = "http://www.atmel.com/" + device["datasheeturl"]
				self.element_add_value(datasheet, "datasheet")
			# Add the manufacturing status
			mature = device["matureproduct"]
			if mature == "0":
				self.element_add_value("production", "status")
			else:
				self.element_add_value("mature", "status")
			# Can happend if there is only 1 element
			if isinstance(device["pm"], dict):
				device["pm"] = [device["pm"]]
			for param in device["pm"]:
				if isinstance(param["i"], dict):
					value = param["i"]["value"]
				else:
					value = param["i"]
				category = param["id"]
				self.element_add_value(value, str(category))
		# Fill in the category names
		for category in json_data["payload"]["parameterconfig"]["pmc"]:
			self.category_mapping_add(category["id"], category["name"])
		# Calculate the number of pages
		self.current = int(json_data["payload"]["items"]["page"])
		self.total = int(json_data["payload"]["items"]["pages"])

	def page_current(self):
		return self.current

	def page_total(self):
		return self.total

	def load(self, data, options = {}):
		if options.has_key('data'):
			self.options = options['data']
		# Strip the _(.*)
		data = re.sub(r"^\s*_\s*\((.*)\)\s*$", r"\1", data)
		json_data = json.loads(data)
		self.parse_deep(json_data)

class Atmel(AtmelCommon):

	def get_options(self, options):
		return {
			'data': {
				'parser': AtmelParser,
				'encoding': 'utf-8',
				'timeout': 60
			}
		}

	specific_options_list = [
		{'display': 'Parametric Table', 'id': 'parametric', 'paging': True},
	]

	def update_options(self, page_number, options):
		base_url = "http://www.atmel.com/ProductFinder/ProductFinder.asmx/FilterData?supercategory=1&category=34864&callback=_"
		url = base_url + "&page=" + str(page_number)
		return {'data': {'url': url}}


	def setup_specific_parser_rules(self, parser):

		def category_post_processing_hook(category, options):
			"""
			1. In the SRAM memory, do not use the ratio * 1024
			"""
			if category.to_param() == "CategoryCPUSpeed":
				self.workaround("Set the CategoryCPUSpeed ratio to 1MHz")
				category.set_global_config('config_convert_ratio', 1*1000*1000)

		parser.hook("post_category_discovery", category_post_processing_hook)
