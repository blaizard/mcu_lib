#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import re

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
		<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
			<s:Body>
				<GetMCUItemsResponse xmlns="http://schema.silabs.com/webservices/2011/01">
					<GetMCUItemsResult xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
						<MCUItem>
							<MHz>20</MHz>
							<McuCore>8051</McuCore>
							<FlashBytes>32 kB</FlashBytes>
							<RamBytes>0.25</RamBytes>
							<DigitalPort>32</DigitalPort>
							<Communications>I2C; SPI; UART</Communications>
							<PcaChannels>5</PcaChannels>
							<Timers16Bit>4</Timers16Bit>
							<InternalOsc>±20%</InternalOsc>
							<Adc1>12-bit, 8-ch., 100 ksps</Adc1>
							<Adc2>—</Adc2>
							<Dac>12-bit, 2-ch.</Dac>
							<TempSensor>true</TempSensor>
							<DebugInterface>JTAG</DebugInterface>
							<Other>—</Other>
							<McuPackage>TQFP64</McuPackage>
							<DevKitLink>&lt;a href="/products/mcu/Pages/C8051F005DK.aspx"&gt;C8051F005DK.aspx&lt;/a&gt;</DevKitLink>
							<DevKit>C8051F005DK</DevKit>
							<DataSheetLink>&lt;a href="/Support%20Documents/TechnicalDocs/C8051F0xx.pdf"&gt;C8051F0xx.pdf&lt;/a&gt;</DataSheetLink>
							<DataShortLink>&lt;a href="/Support%20Documents/TechnicalDocs/C8051F000-Short.pdf"&gt;C8051F000_short.pdf&lt;/a&gt;</DataShortLink>
							<ErrataLink/>
							<Vref>true</Vref>
							<Comparators>2</Comparators>
							<Alternative/>
							<AECQ100>false</AECQ100>
							<CapSense>false</CapSense>
							<PartNumber>C8051F000</PartNumber>
							<PartNumberLink>&lt;a href="/products/mcu/mixed-signalmcu/Pages/C8051F00x1x.aspx"&gt;C8051F0xx.aspx&lt;/a&gt;</PartNumberLink>
							<OrderPartNumber>C8051F000-GQ</OrderPartNumber>
							<SampleAvailable>true</SampleAvailable>
							<BuyAvailable>true</BuyAvailable>
							<ReleaseDate>0001-01-01T00:00:00</ReleaseDate>
							<PackageType>TQFP64</PackageType>
							<PackageSize>12x12 mm</PackageSize>
							<Automotive>false</Automotive>
						</MCUItem>
						<MCUItem>
							...
						</MCUItem>
					</GetMCUItemsResult>
				</GetMCUItemsResponse>
			</s:Body>
		</s:Envelope>
	"""

	def parse_deep(self, data):
		data = data.encode('ascii', 'replace')
		data = BeautifulSoup(data)
		for index, d in enumerate(data.find_all("mcuitem")):
			self.element_create()
			for i, c in enumerate(d.find_all(True)):
				self.element_add_value(c.text, c.name)

		# Add custom category mapping
		self.category_mapping_add("mhz", "cpu speed (MHz)")
		self.category_mapping_add("mcucore", "cpu")
		self.category_mapping_add("flashbytes", "flash (kb)")
		self.category_mapping_add("rambytes", "ram (kb)")
		self.category_mapping_add("digitalport", "i/o")
		self.category_mapping_add("adc1", "adc 1")
		self.category_mapping_add("adc2", "adc 2")
		self.category_mapping_add("communications", "digital")
		self.category_mapping_add("timers16bit", "16-bit timers")
		self.category_mapping_add("internalosc", "oscillator accuracy")
		self.category_mapping_add("tempsensor", "temperature sensor")
		self.category_mapping_add("mcupackage", "package")
		self.category_mapping_add("datasheetlink", "datasheet link")
		self.category_mapping_add("orderpartnumber", "")
		self.category_mapping_add("partnumber", "part number")

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
				'url': 'http://www.silabs.com/_vti_bin/ParametricSearchLists.svc',
				'xml': "<SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">"
						"<SOAP-ENV:Body>"
							"<i0:GetMCUItems xmlns:i0=\"http://schema.silabs.com/webservices/2011/01\">"
								"<i0:UserPassword>P@ssw0rd</i0:UserPassword>"
								"<i0:UserId>flashLists</i0:UserId>"
							"</i0:GetMCUItems>"
						"</SOAP-ENV:Body>"
					"</SOAP-ENV:Envelope>",
				'headers': {
					'soapaction': 'http://schema.silabs.com/webservices/2011/01/ParametricSearchListsServiceContract/GetMCUItems',
					'Content-Type': 'text/xml; charset=utf-8'
				}
			},
		}

	specific_options_list = [
		{'display': 'Parametric', 'id': 'parametric', 'data': [{}]},
	]


