#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from mculib.parser.generic import *
from mculib.parser.deep import *

class STCommon(GenericParserPort):

	@staticmethod
	def get_manufacturer():
		return "st"

	def setup_specific_parser_rules(self, parser):
		pass

	def setup_parser_rules(self, parser):
		"""
		Rules that applies specificly to ST
		"""

		def category_pre_processing_hook(category, options):
			if category.to_param() == "CategoryCPUCore":
				category.add_translation_table([
					[ r".*\b(stm8)\b.*", "stm8" ]
				])
			if category.to_param() == "CategoryEBI":
				category.add_feature_regexpr(["fsmc"])
			if category.to_param() in ["CategoryWebPage", "CategoryDatasheet"]:
				category.set_base_url("http://www.st.com")

		parser.hook("pre_category_discovery", category_pre_processing_hook)
		self.setup_specific_parser_rules(parser)

class ST(STCommon):

	def get_options(self, options):
		return {
			'data': {
				'parser': JSONParser,
				'device_tag': ['records', None],
				'category_tag': [None],
				'category_param': {
					'id_tag': [],
					'id_attr': True,
					'value_tag': [],
					'value_attr': False,
				},
				'category_map_tag': ['metaData', 'fields', None],
				'category_map_param': {
					'id_tag': ["name"],
					'id_attr': False,
					'value_tag': ["header"],
					'value_attr': False,
				}
			}
		}

	# This is using flex messaging protocol AMFX
	#specific_options_list = [
	#	{'display': 'temp', 'id': 'temp', 'url': 'http://www.st.com/stonline/stappl/productcatalog/messagebroker/http',
	#		'xml': '<amfx ver="3" xmlns="http://www.macromedia.com/2005/amfx"><body><object type="flex.messaging.messages.RemotingMessage"><traits><string>body</string><string>clientId</string><string>destination</string><string>headers</string><string>messageId</string><string>operation</string><string>source</string><string>timestamp</string><string>timeToLive</string></traits><array length="2"><string>1169</string><string/></array><null/><string>remoteProductsView</string><object><traits><string>DSEndpoint</string><string>DSId</string></traits><string>my-http</string><string>A0FEF8E9-5609-1CED-0B94-C6B26A0C79F2</string></object><string>8EA2FFA9-D3E5-DC0D-C917-3126AB0DDB91</string><string>fetchProductsDataForSubClass</string><null/><int>0</int><int>0</int></object></body></amfx>'}
	#]

	specific_options_list = [
		# 32-bit
		{'display': 'STM32', 'id': 'stm32', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?subclassId=1169&lang=en_US&companyCode=&_dc=1362477299782'}]},
		# F0
		{'display': 'STM32 F0 Entry-level', 'id': 'stm32f0', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1574&subclassId=1169&lang=en_US&companyCode=&_dc=1362474908052'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f0', 'CategoryCPUCore': 'cm0'}},
		{'display': 'STM32 F030 Value Line', 'id': 'stm32f030', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1826&subclassId=1169&lang=en_US&_dc=1373290743429'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f0', 'CategoryDeviceFamily': 'stm32f030', 'CategoryCPUCore': 'cm0'}},
		{'display': 'STM32 F0x1', 'id': 'stm32f0x1', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=7&subclassId=1169&lang=en_US&_dc=1389860412304'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f0', 'CategoryCPUCore': 'cm0'}},
		{'display': 'STM32 F0x2', 'id': 'stm32f0x2', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1823&subclassId=1169&lang=en_US&_dc=1389860518882'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f0', 'CategoryCPUCore': 'cm0'}},
		# F1
		{'display': 'STM32 F1 Mainstream', 'id': 'stm32f1', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1031&subclassId=1169&lang=en_US&companyCode=&_dc=1362474940948'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f1', 'CategoryCPUCore': 'cm3'}},
		{'display': 'STM32 F100 Value Line', 'id': 'stm32f100', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=775&subclassId=1169&lang=en_US&companyCode=&_dc=1362475009658'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f1', 'CategoryDeviceFamily': 'stm32f100', 'CategoryCPUCore': 'cm3'}},
		{'display': 'STM32 F101', 'id': 'stm32f101', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1567&subclassId=1169&lang=en_US&companyCode=&_dc=1362475076921'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f1', 'CategoryDeviceFamily': 'stm32f101', 'CategoryCPUCore': 'cm3'}},
		{'display': 'STM32 F102', 'id': 'stm32f102', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1566&subclassId=1169&lang=en_US&companyCode=&_dc=1362475116430'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f1', 'CategoryDeviceFamily': 'stm32f102', 'CategoryCPUCore': 'cm3'}},
		{'display': 'STM32 F103', 'id': 'stm32f103', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1565&subclassId=1169&lang=en_US&companyCode=&_dc=1362475175208'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f1', 'CategoryDeviceFamily': 'stm32f103', 'CategoryCPUCore': 'cm3'}},
		{'display': 'STM32 F105/107', 'id': 'stm32f105_107', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1564&subclassId=1169&lang=en_US&companyCode=&_dc=1362475205816'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f1', 'CategoryDeviceFamily': 'stm32f105_107', 'CategoryCPUCore': 'cm3'}},
		# F2
		{'display': 'STM32 F2 Hi-Performance', 'id': 'stm32f2', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1575&subclassId=1169&lang=en_US&companyCode=&_dc=1362475889490'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f2', 'CategoryCPUCore': 'cm3'}},
		{'display': 'STM32 F205/215', 'id': 'stm32f205_215', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1433&subclassId=1169&lang=en_US&companyCode=&_dc=1362475974729'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f2', 'CategoryDeviceFamily': 'stm32f205_215', 'CategoryCPUCore': 'cm3'}},
		{'display': 'STM32 F207/217', 'id': 'stm32f207_217', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=9&subclassId=1169&lang=en_US&companyCode=&_dc=1362476020850'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f2', 'CategoryDeviceFamily': 'stm32f207_217', 'CategoryCPUCore': 'cm3'}},
		# F3
		{'display': 'STM32 F3 Analog & DSP', 'id': 'stm32f3', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1576&subclassId=1169&lang=en_US&companyCode=&_dc=1362476161234'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f3', 'CategoryCPUCore': 'cm4f'}},
		{'display': 'STM32 F302/303/313', 'id': 'stm32f302_303_313', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1531&subclassId=1169&lang=en_US&companyCode=&_dc=1362476268713'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f3', 'CategoryDeviceFamily': 'stm32f302_303_313', 'CategoryCPUCore': 'cm4f'}},
		{'display': 'STM32 F372/373/383', 'id': 'stm32f3', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=10&subclassId=1169&lang=en_US&companyCode=&_dc=1362476301055'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f3', 'CategoryDeviceFamily': 'stm32f372_373_383', 'CategoryCPUCore': 'cm4f'}},
		# F4
		{'display': 'STM32 F4 Hi-Performance & DSP', 'id': 'stm32f4', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1577&subclassId=1169&lang=en_US&companyCode=&_dc=1362476407281'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f4', 'CategoryCPUCore': 'cm4f'}},
		{'display': 'STM32 F405/415', 'id': 'stm32f405_415', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1035&subclassId=1169&lang=en_US&companyCode=&_dc=1362476549950'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f4', 'CategoryDeviceFamily': 'stm32f405_415', 'CategoryCPUCore': 'cm4f'}},
		{'display': 'STM32 F407/417', 'id': 'stm32f407_417', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=11&subclassId=1169&lang=en_US&companyCode=&_dc=1362476571686'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f4', 'CategoryDeviceFamily': 'stm32f407_417', 'CategoryCPUCore': 'cm4f'}},
		{'display': 'STM32 F427/437', 'id': 'stm32f427_437', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1789&subclassId=1169&lang=en_US&companyCode=&_dc=1362476609148'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f4', 'CategoryDeviceFamily': 'stm32f427_437', 'CategoryCPUCore': 'cm4f'}},
		{'display': 'STM32 F429/439', 'id': 'stm32f429_439', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1806&subclassId=1169&lang=en_US&companyCode=&_dc=1362476689957'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f4', 'CategoryDeviceFamily': 'stm32f429_439', 'CategoryCPUCore': 'cm4f'}},
		{'display': 'STM32 F446', 'id': 'stm32f446', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1875&subclassId=1169&lang=en_US&_dc=1418392671836'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f4', 'CategoryDeviceFamily': 'stm32f446', 'CategoryCPUCore': 'cm4f'}},
		# F7
		{'display': 'STM32 F7', 'id': 'stm32f7', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1858&subclassId=1169&lang=en_US&_dc=1411542089380'}], 'custom': {'CategoryDeviceTopFamily': 'stm32f7', 'CategoryDeviceFamily': 'stm32f7', 'CategoryCPUCore': 'cm7'}},
		# L0
		{'display': 'STM32 L0 series of ultra-low-power MCUs', 'id': 'stm32l0', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1817&subclassId=1169&lang=en_US&_dc=1392191247158'}], 'custom': {'CategoryDeviceTopFamily': 'stm32l0', 'CategoryCPUCore': 'cm0+'}},
		{'display': 'STM32 L0x1', 'id': 'stm32l0x1', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1843&subclassId=1169&lang=en_US&_dc=1393316259522'}], 'custom': {'CategoryDeviceTopFamily': 'stm32l0', 'CategoryDeviceFamily': 'stm32l0x1', 'CategoryCPUCore': 'cm0+'}},
		{'display': 'STM32 L0x2', 'id': 'stm32l0x2', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1844&subclassId=1169&lang=en_US&_dc=1393316383325'}], 'custom': {'CategoryDeviceTopFamily': 'stm32l0', 'CategoryDeviceFamily': 'stm32l0x2', 'CategoryCPUCore': 'cm0+'}},
		{'display': 'STM32 L0x3', 'id': 'stm32l0x3', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1845&subclassId=1169&lang=en_US&_dc=1392191284521'}], 'custom': {'CategoryDeviceTopFamily': 'stm32l0', 'CategoryDeviceFamily': 'stm32l0x3', 'CategoryCPUCore': 'cm0+'}},
		# L1
		{'display': 'STM32 L1 Ultra Low Power', 'id': 'stm32l1', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1295&subclassId=1169&lang=en_US&companyCode=&_dc=1362476791450'}], 'custom': {'CategoryDeviceTopFamily': 'stm32l1', 'CategoryCPUCore': 'cm3'}},
		{'display': 'STM32 L100 Value Line', 'id': 'stm32l100', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1808&subclassId=1169&lang=en_US&companyCode=&_dc=1362476857717'}], 'custom': {'CategoryDeviceTopFamily': 'stm32l1', 'CategoryDeviceFamily': 'stm32l100', 'CategoryCPUCore': 'cm3'}},
		{'display': 'STM32 L151/152', 'id': 'stm32l151_152', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=962&subclassId=1169&lang=en_US&companyCode=&_dc=1362476873678'}], 'custom': {'CategoryDeviceTopFamily': 'stm32l1', 'CategoryDeviceFamily': 'stm32l151_152', 'CategoryCPUCore': 'cm3'}},
		{'display': 'STM32 L162', 'id': 'stm32l162', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=13&subclassId=1169&lang=en_US&companyCode=&_dc=1362476917922'}], 'custom': {'CategoryDeviceTopFamily': 'stm32l1', 'CategoryDeviceFamily': 'stm32l162', 'CategoryCPUCore': 'cm3'}},
		# Touch
		{'display': 'STM32T Touch', 'id': 'stm32t', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1582&subclassId=1169&lang=en_US&companyCode=&_dc=1362476984813'}], 'custom': {'CategoryDeviceTopFamily': 'stm32t', 'CategoryDeviceFamily': 'stm32t'}},
		# Wireless
		{'display': 'STM32W Wireless', 'id': 'stm32w', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1581&subclassId=1169&lang=en_US&companyCode=&_dc=1362477260749'}], 'custom': {'CategoryDeviceTopFamily': 'stm32w', 'CategoryDeviceFamily': 'stm32w', 'CategoryCPUCore': 'cm3'}},

		# 8-bit
		{'display': 'STM8', 'id': 'stm8', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?subclassId=1244&lang=en_US&companyCode=&_dc=1362477611008'}], 'custom': {'CategoryCPUCore': 'stm8'}},
		# AF
		{'display': 'STM8 AF', 'id': 'stm8af', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1583&subclassId=1244&lang=en_US&companyCode=&_dc=1362482804350'}], 'custom': {'CategoryDeviceTopFamily': 'stm8af', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 AF52', 'id': 'stm8af52', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1543&subclassId=1244&lang=en_US&companyCode=&_dc=1362482854453'}], 'custom': {'CategoryDeviceTopFamily': 'stm8af', 'CategoryDeviceFamily': 'stm8af52', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 AF62', 'id': 'stm8af62', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=6&subclassId=1244&lang=en_US&companyCode=&_dc=1362482905131'}], 'custom': {'CategoryDeviceTopFamily': 'stm8af', 'CategoryDeviceFamily': 'stm8af62', 'CategoryCPUCore': 'stm8'}},
		# AL
		{'display': 'STM8 AL', 'id': 'stm8al', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1584&subclassId=1244&lang=en_US&companyCode=&_dc=1362482959617'}], 'custom': {'CategoryDeviceTopFamily': 'stm8al', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 AL31', 'id': 'stm8al31', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=3&subclassId=1244&lang=en_US&companyCode=&_dc=1362483052907'}], 'custom': {'CategoryDeviceTopFamily': 'stm8al', 'CategoryDeviceFamily': 'stm8al31', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 AL3L', 'id': 'stm8al3l', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=4&subclassId=1244&lang=en_US&companyCode=&_dc=1362483100263'}], 'custom': {'CategoryDeviceTopFamily': 'stm8al', 'CategoryDeviceFamily': 'stm8al3l', 'CategoryCPUCore': 'stm8'}},
		# L
		{'display': 'STM8 L', 'id': 'stm8l', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1336&subclassId=1244&lang=en_US&companyCode=&_dc=1362483176143'}], 'custom': {'CategoryDeviceTopFamily': 'stm8l', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 L051/052 Value Line', 'id': 'stm8al051_052', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1&subclassId=1244&lang=en_US&companyCode=&_dc=1362483209194'}], 'custom': {'CategoryDeviceTopFamily': 'stm8l', 'CategoryDeviceFamily': 'stm8l051_052', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 L101', 'id': 'stm8l', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1003&subclassId=1244&lang=en_US&companyCode=&_dc=1362483260297'}], 'custom': {'CategoryDeviceTopFamily': 'stm8l', 'CategoryDeviceFamily': 'stm8l101', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 L151/152', 'id': 'stm8l', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1570&subclassId=1244&lang=en_US&companyCode=&_dc=1362483306376'}], 'custom': {'CategoryDeviceTopFamily': 'stm8l', 'CategoryDeviceFamily': 'stm8l151_152', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 L162', 'id': 'stm8af', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1790&subclassId=1244&lang=en_US&companyCode=&_dc=1362483347243'}], 'custom': {'CategoryDeviceTopFamily': 'stm8l', 'CategoryDeviceFamily': 'stm8l162', 'CategoryCPUCore': 'stm8'}},
		# S
		{'display': 'STM8 S', 'id': 'stm8s', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1010&subclassId=1244&lang=en_US&companyCode=&_dc=1362483396086'}], 'custom': {'CategoryDeviceTopFamily': 'stm8s', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 S003/005/007 Value Line', 'id': 'stm8s003_005_007', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=2&subclassId=1244&lang=en_US&companyCode=&_dc=1362483470745'}], 'custom': {'CategoryDeviceTopFamily': 'stm8s', 'CategoryDeviceFamily': 'stm8s003_005_007', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 S103/105', 'id': 'stm8s103_105', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=754&subclassId=1244&lang=en_US&companyCode=&_dc=1362483516719'}], 'custom': {'CategoryDeviceTopFamily': 'stm8s', 'CategoryDeviceFamily': 'stm8s103_105', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 S207/208', 'id': 'stm8s207_208', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1571&subclassId=1244&lang=en_US&companyCode=&_dc=1362483556213'}], 'custom': {'CategoryDeviceTopFamily': 'stm8s', 'CategoryDeviceFamily': 'stm8s207_208', 'CategoryCPUCore': 'stm8'}},
		# T
		{'display': 'STM8 T', 'id': 'stm8t', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?seriesId=1598&subclassId=1244&lang=en_US&companyCode=&_dc=1362483606807'}], 'custom': {'CategoryDeviceTopFamily': 'stm8t', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 T141/143', 'id': 'stm8t141_143', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=1299&subclassId=1244&lang=en_US&companyCode=&_dc=1362483645789'}], 'custom': {'CategoryDeviceTopFamily': 'stm8t', 'CategoryDeviceFamily': 'stm8t141_143', 'CategoryCPUCore': 'stm8'}},
		{'display': 'STM8 TL52/L53', 'id': 'stm8tl52_l53', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?lineId=15&subclassId=1244&lang=en_US&companyCode=&_dc=1362483687114'}], 'custom': {'CategoryDeviceTopFamily': 'stm8t', 'CategoryDeviceFamily': 'stm8tl52_l53', 'CategoryCPUCore': 'stm8'}},

		# Ultra Low Power MCUs
		{'display': 'ST Ultra Low Power MCUs', 'id': 'ulp', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?subclassId=1544&lang=en_US&companyCode=&_dc=1362483839131'}],
				'ignore_categories': [r"(16|32).*timer.*"]}, # Bug in this category
		# Legacy
		{'display': 'ST Legacy MCUs', 'id': 'legacy', 'data': [{'url': 'http://www.st.com/stonline/stappl/productcatalog/jsp/jsonDataForL3.jsp?subclassId=1714&lang=en_US&companyCode=&_dc=1362483970916'}], 'custom': {'CategoryLegacy': 'yes'},
				'ignore_categories': [r"(16|32).*timer.*"]}, # Bug in this category

	]
