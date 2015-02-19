#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from mculib.parser.generic import *
from mculib.parser.deep import *
from mculib.parser.html_table import *

from bs4 import BeautifulSoup

class RenesasCommon(GenericParserPort):
	@staticmethod
	def get_manufacturer():
		return "renesas"

	def setup_specific_parser_rules(self, parser):
		pass

	def setup_parser_rules(self, parser):
		"""
		Rules that applies specificly to Renesas
		"""

		def category_pre_processing_hook(category, options):
			"""
			"""
			if category.to_param() == "CategoryPackage":
				category.set_package_translation_table([
					[ r"plqp", "lqfp" ],
					[ r"plsp", "lssop" ],
					[ r"pwqn", "hwqfn" ],
					[ r"prsp", "ssop" ],
					[ r"ptlg", "tflga" ],
					[ r"plbg", "lfbga" ],
				])
			if category.to_param() in ["CategorySPI"]:
				category.add_feature_regexpr([r"clocked\s*serial\s*interface"])

		parser.hook("pre_category_discovery", category_pre_processing_hook)

		self.setup_specific_parser_rules(parser)

class RenesasParser(HTMLTableParser):
	"""
	Data have the following format:
	<table id="parametricResult" class="searchResultsTable">
		<tr>
			<th colspan="2"><span>Document</span></th>
			<th ><span id="sort1" class="sortUp btn" onclick="sort('ss2', '1', this);"> Part Name</span></th>
			<th ><span id="sort2" class="sortUp btn" onclick="sort('ss3', '1', this);"> Buy or Sample</span></th>
			<th ><span id="sort3" class="sortUp btn" onclick="sort('sn4', '1', this);"> Price</span></th>
			<th ><span id="sort4" class="sortUp btn" onclick="sort('sn5', '1', this);"> Bit Size</span></th>
			<th ><span id="sort5" class="sortUp btn" onclick="sort('ss6', '1', this);"> Family</span></th>
			<th ><span id="sort6" class="sortUp btn" onclick="sort('ss7', '1', this);"> Series</span></th>
			<th ><span id="sort7" class="sortUp btn" onclick="sort('ss8', '1', this);"> Group</span></th>
			<th ><span id="sort8" class="sortUp btn" onclick="sort('sn9', '1', this);"> Program<br>Memory (KB)</span></th>
			<th ><span id="sort9" class="sortUp btn" onclick="sort('sn10', '1', this);"> RAM<br>(KB)</span></th>
			<th ><span id="sort10" class="sortUp btn" onclick="sort('sn11', '1', this);"> Data Flash (KB)</span></th>
			<th ><span id="sort11" class="sortUp btn" onclick="sort('ss12', '1', this);"> Program<br>Memory<br>Type</span></th>
			<th ><span id="sort12" class="sortUp btn" onclick="sort('ss13', '1', this);"> Cache<br>Memory</span></th>
			<th ><span id="sort13" class="sortUp btn" onclick="sort('ss14', '1', this);"> Cache<br>Memory<br>Remarks</span></th>
			<th ><span id="sort14" class="sortUp btn" onclick="sort('sn15', '1', this);"> Pin Count</span></th>
			<th ><span id="sort15" class="sortUp btn" onclick="sort('ss16', '1', this);"> CPU</span></th>
			<th ><span id="sort16" class="sortUp btn" onclick="sort('sn17', '1', this);"> Max. Freq (MHz)</span></th>
			<th ><span id="sort17" class="sortUp btn" onclick="sort('ss18', '1', this);"> Sub-clock<br>(32.768 kHz)</span></th>
			<th ><span id="sort18" class="sortUp btn" onclick="sort('ss19', '1', this);"> On-chip<br>Oscillator</span></th>
			<th ><span id="sort19" class="sortUp btn" onclick="sort('ss20', '1', this);"> On-chip<br>Oscillator<br>Freq. (MHz)</span></th>
			<th ><span id="sort20" class="sortUp btn" onclick="sort('ss21', '1', this);"> PLL</span></th>
			<th ><span id="sort21" class="sortUp btn" onclick="sort('ss22', '1', this);"> RTC</span></th>
			<th ><span id="sort22" class="sortUp btn" onclick="sort('ss23', '1', this);"> Power-On Reset</span></th>
			<th ><span id="sort23" class="sortUp btn" onclick="sort('ss24', '1', this);"> Low Voltage Detection</span></th>
			<th ><span id="sort24" class="sortUp btn" onclick="sort('ss25', '1', this);"> Memory<br>Management<br>Unit</span></th>
			<th ><span id="sort25" class="sortUp btn" onclick="sort('ss26', '1', this);"> Floating Point Unit</span></th>
			<th ><span id="sort26" class="sortUp btn" onclick="sort('ss27', '1', this);"> DMA</span></th>
			<th ><span id="sort27" class="sortUp btn" onclick="sort('ss28', '1', this);"> DMA<br>Remarks</span></th>
			<th ><span id="sort28" class="sortUp btn" onclick="sort('ss29', '1', this);"> External<br>Bus<br>Expansion</span></th>
			<th ><span id="sort29" class="sortUp btn" onclick="sort('sn30', '1', this);"> External<br>Interrupt<br>Pins</span></th>
			<th ><span id="sort30" class="sortUp btn" onclick="sort('sn31', '1', this);"> I/O<br>Ports</span></th>
			<th ><span id="sort31" class="sortUp btn" onclick="sort('sn32', '1', this);"> 8-bit<br>Timer (ch)</span></th>
			<th ><span id="sort32" class="sortUp btn" onclick="sort('sn33', '1', this);"> 16-bit<br>Timer (ch)</span></th>
			<th ><span id="sort33" class="sortUp btn" onclick="sort('sn34', '1', this);"> 32-bit<br>Timer (ch)</span></th>
			<th ><span id="sort34" class="sortUp btn" onclick="sort('sn35', '1', this);"> Watchdog<br>Timer (ch)</span></th>
			<th ><span id="sort35" class="sortUp btn" onclick="sort('ss36', '1', this);"> Other<br>Timers</span></th>
			<th ><span id="sort36" class="sortUp btn" onclick="sort('sn37', '1', this);"> PWM<br>Output</span></th>
			<th ><span id="sort37" class="sortUp btn" onclick="sort('ss38', '1', this);"> 3-phase<br>PWM<br>Output<br>Function</span></th>
			<th ><span id="sort38" class="sortUp btn" onclick="sort('sn39', '1', this);"> 8-bit<br>A/D<br>Converter (ch)</span></th>
			<th ><span id="sort39" class="sortUp btn" onclick="sort('sn40', '1', this);"> 10-bit<br>A/D<br>Converter (ch)</span></th>
			<th ><span id="sort40" class="sortUp btn" onclick="sort('sn41', '1', this);"> 12-bit<br>A/D<br>Converter (ch)</span></th>
			<th ><span id="sort41" class="sortUp btn" onclick="sort('sn42', '1', this);"> Over<br>14-bit<br>A/D<br>Converter (ch)</span></th>
			<th ><span id="sort42" class="sortUp btn" onclick="sort('ss43', '1', this);"> Delta-Sigma<br>A/D<br>Converter</span></th>
			<th ><span id="sort43" class="sortUp btn" onclick="sort('sn44', '1', this);"> 8-bit<br>D/A<br>Converter (ch)</span></th>
			<th ><span id="sort44" class="sortUp btn" onclick="sort('sn45', '1', this);"> 10-bit<br>D/A<br>Converter (ch)</span></th>
			<th ><span id="sort45" class="sortUp btn" onclick="sort('sn46', '1', this);"> 12-bit<br>D/A<br>Converter (ch)</span></th>
			<th ><span id="sort46" class="sortUp btn" onclick="sort('sn47', '1', this);"> Over<br>14-bit<br>D/A<br>Converter (ch)</span></th>
			<th ><span id="sort47" class="sortUp btn" onclick="sort('sn48', '1', this);"> CAN (ch)</span></th>
			<th ><span id="sort48" class="sortUp btn" onclick="sort('ss49', '1', this);"> Ethernet</span></th>
			<th ><span id="sort49" class="sortUp btn" onclick="sort('ss50', '1', this);"> Ethernet<br>Remarks</span></th>
			<th ><span id="sort50" class="sortUp btn" onclick="sort('ss51', '1', this);"> USB<br>Host</span></th>
			<th ><span id="sort51" class="sortUp btn" onclick="sort('ss52', '1', this);"> USB<br>Peripheral</span></th>
			<th ><span id="sort52" class="sortUp btn" onclick="sort('sn53', '1', this);"> USB<br>Ports (ch)</span></th>
			<th ><span id="sort53" class="sortUp btn" onclick="sort('ss54', '1', this);"> USB<br>Hi-Speed<br>Support</span></th>
			<th ><span id="sort54" class="sortUp btn" onclick="sort('sn55', '1', this);"> USB<br>Endpoints</span></th>
			<th ><span id="sort55" class="sortUp btn" onclick="sort('ss56', '1', this);"> USB<br>Isochronous<br>Transfer<br>Support</span></th>
			<th ><span id="sort56" class="sortUp btn" onclick="sort('ss57', '1', this);"> USB<br>Remarks</span></th>
			<th ><span id="sort57" class="sortUp btn" onclick="sort('sn58', '1', this);"> Clocked<br>Serial<br>Interface (ch)</span></th>
			<th ><span id="sort58" class="sortUp btn" onclick="sort('sn59', '1', this);"> SPI (ch)</span></th>
			<th ><span id="sort59" class="sortUp btn" onclick="sort('sn60', '1', this);"> UART (ch)</span></th>
			<th ><span id="sort60" class="sortUp btn" onclick="sort('sn61', '1', this);"> I2C (ch)</span></th>
			<th ><span id="sort61" class="sortUp btn" onclick="sort('sn62', '1', this);"> LIN (ch)</span></th>
			<th ><span id="sort62" class="sortUp btn" onclick="sort('sn63', '1', this);"> IEBus (ch)</span></th>
			<th ><span id="sort63" class="sortUp btn" onclick="sort('ss64', '1', this);"> Serial<br>Interface<br>Remarks</span></th>
			<th ><span id="sort64" class="sortUp btn" onclick="sort('sn65', '1', this);"> LCD<br>Segment<br>Count</span></th>
			<th ><span id="sort65" class="sortUp btn" onclick="sort('ss66', '1', this);"> LCD<br>Remarks</span></th>
			<th ><span id="sort66" class="sortUp btn" onclick="sort('ss67', '1', this);"> Display<br>Function</span></th>
			<th ><span id="sort67" class="sortUp btn" onclick="sort('ss68', '1', this);"> Display<br>Function<br>Remarks</span></th>
			<th ><span id="sort68" class="sortUp btn" onclick="sort('sn69', '1', this);"> Operating<br>Voltage<br>Max (V)</span></th>
			<th ><span id="sort69" class="sortUp btn" onclick="sort('sn70', '1', this);"> Operating<br>Voltage<br>Min (V)</span></th>
			<th ><span id="sort70" class="sortUp btn" onclick="sort('ss71', '1', this);"> Power<br>Supply</span></th>
			<th ><span id="sort71" class="sortUp btn" onclick="sort('sn72', '1', this);"> Operating<br>Temperature<br>Max (&#176;C)</span></th>
			<th ><span id="sort72" class="sortUp btn" onclick="sort('sn73', '1', this);"> Operating<br>Temperature<br>Min (&#176;C)</span></th>
			<th ><span id="sort73" class="sortUp btn" onclick="sort('ss74', '1', this);"> Operating<br>Temperature<br>Remarks</span></th>
			<th ><span id="sort74" class="sortUp btn" onclick="sort('ss75', '1', this);"> Remarks</span></th>
			<th ><span id="sort75" class="sortUp btn" onclick="sort('ss76', '1', this);"> Production<br>Status</span></th>
			<th ><span>Package<br>Code</span></th>
			<th ><span id="sort77" class="sortUp btn" onclick="sort('ss78', '1', this);"> Part Name</span></th>
		</tr>
		<tr>
			<td width="6px"><input type="checkbox" id="172608" value="172608" onclick="compareBoxChange(this)" /></td>
			<td align="center">
				<a onclick="openSubWindow('/request?SCREEN_ID=ViewDocumentList&EXECUTE_ACTION=search&LAYER_ID=169370&PART_NO=R5F10CGBJFB')" href="javascript:void(0)"><acronym title="Document List">
					<img alt="PDF" src="/media/common/icon_pdf_list_s.gif"></acronym>
				</a>
			</td>
			<td class="nobr"><a href="/products/mpumcu/rl78/rl78d1x/rl78d1a/device/R5F10CGBJFB.jsp" target="_blank">R5F10CGBJFB</a></td>
			<td align="center">-</td>
			<td>-</td>
			<td>16</td>
			<td><a href="/products/mpumcu/rl78/index.jsp" target="_blank">RL78</a></td>
			<td><a href="/products/mpumcu/rl78/rl78d1x/index.jsp" target="_blank">RL78/D1x</a></td>
			... (<td><a href="/products/mpumcu/rl78/rl78d1x/rl78d1a/index.jsp" target="_blank">RL78/D1A</a></td><td>24</td><td>2</td><td>8</td><td>Flash memory</td><td>NO</td><td>-</td><td>48</td><td>RL78</td><td>32</td><td>NO</td><td>YES</td><td>32M, 24M, 16M, 12M, 8M, 4M Low-speed Oscillator 15kHz</td><td>YES</td><td>YES</td><td>YES</td><td>YES</td><td>NO</td><td>NO</td><td>YES</td><td>DMAC x 2 ch</td><td>NO</td><td>6</td><td>38</td><td>0</td><td>24</td><td>0</td><td>1</td><td>Interval Timer x 1 ch, Wakeup Timer x 1ch</td><td>16</td><td>NO</td><td>0</td><td>5</td><td>0</td><td>0</td><td>NO</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>NO</td><td>-</td><td>NO</td><td>NO</td><td>0</td><td>NO</td><td>0</td><td>NO</td><td>-</td><td>2</td><td>0</td><td>1</td><td>1</td><td>1</td><td>0</td><td>-</td><td>27</td><td>-</td><td>NO</td><td>-</td><td>5.5</td><td>2.7</td><td>-</td><td>85</td><td>-40</td><td>Ambient Temperature</td><td>Automotive</td><td>Under Development</td><td><a href="/products/mpumcu/rl78/rl78d1x/rl78d1a/device/R5F10CGBJFB.jsp#package">PLQP0048KF-A<BR>(P48GA-50-8EU-1)</a></td><td class="nobr"><a href="/products/mpumcu/rl78/rl78d1x/rl78d1a/device/R5F10CGBJFB.jsp" target="_blank">R5F10CGBJFB</a></td>)
		</tr>
		...
	"""

	current = 0
	total = 0

	def page_current(self):
		return self.current

	def page_total(self):
		return self.total

	def load(self, data, options = {}):
		"""
		Read the number of pages and the page number.
			<p class="match">
				42 matches <br/> (1 to 42 are displayed.)
			</p>
		"""
		soup = BeautifulSoup(data)
		# Read the number of pages
		match_list = soup.find_all("p", {"class" : "match"})
		if len(match_list) != 1:
			raise error("Found %i page info, there should be only 1." % (len(match_list)))
		for match in match_list:
			m = re.match(r"\s*([0-9]+)\s*match.*\(\s*([0-9]+)\s*to\s*([0-9]+)\s*.*\).*", match.get_text(), flags=re.IGNORECASE|re.DOTALL)
			if not m:
				raise error("Cannot identify the page number.")
			total_entries = int(m.group(1))
			first_entry = int(m.group(2))
			last_entry = int(m.group(3))
			# Calculates the number of pages
			self.total = (total_entries + Renesas.nb_entries_per_page - 1)/ Renesas.nb_entries_per_page
			# Calculates the current page
			self.current = (last_entry - 1) / Renesas.nb_entries_per_page

		super(RenesasParser, self).load(data, options)

class Renesas(RenesasCommon):

	nb_entries_per_page = 100

	def get_options(self, options):
		return {
			'ignore_categories': [2, r"\s*family\s*"],
			'data': {
				'parser': RenesasParser,
				'encoding': 'utf-8',
				'timeout': 60,
				'url': 'http://am.renesas.com/req/include_product_search.do',
				'attrs':{'id': "parametricResult"},
				'post': {
					'event': 'parametricSearch',
					'prdCategoryKey': '',
					'region': 'am',
					'requestCategory': 'H',
					'copyToClipFlg': 0,
					'sessionClearFlg': 'true',
					'lastSelectedCon': '',
					'lastSelectedConId': '',
					'selectedConList': '',
					'currentSelectorCondition': '',
					'currentSelectorConditionId': '',
					'selectorFqlStr': '',
					'seletableRange': '',
					'slctFlg': 1,
					'seeMoreFlg': 0,
					'autoSearchFlag': 'on',
					'headerLayerId': '',
					'encodeHeaderLayerName': '',
					'hits': nb_entries_per_page,
					'sortStr': '',
					'sortIds': '',
					'compareList': '',
					'includeDiv': 'PS',
					'specDispFlg': 'F',
					'item': nb_entries_per_page
				},
			}
		}

	specific_options_list2 = [
		{'display': 'MCU and MPU', 'id': 'mcu_mpu', 'paging': True, 'data': [ {'post': {
'event':'parametricSearch',
'prdCategoryKey':1,
'region':"",
'requestCategory':"C",
'copyToClipFlg':0,
'sessionClearFlg':'true',
'layerIds':"",
'lastSelectedCon':"",
'lastSelectedConId':"",
'selectedConList':"",
'currentSelectorCondition':"",
'currentSelectorConditionId':"",
'selectorFqlStr':"",
'seletableRange':"",
'slctFlg':0,
'seeMoreFlg':0,
'valueA':0,
'valueB':"&ge;2048",
'valueA':"&le;10",
'valueB':"&ge;200",
'valueA':"&lt;30",
'valueB':"&gt;256",
'valueA':"&le;1.5",
'valueB':"&ge;4.5",
'valueA':"&le;16",
'valueB':"&ge;2048",
'autoSearchFlag':'on',
'headerLayerId':"",
'encodeHeaderLayerName':"",
'hits':0,
'pageNo':0,
'sortStr':"",
'sortIds':"",
'compareList':"",
'includeDiv':'PL',
'specDispFlg':'S',
'item':20
}} ]},
		{'display': 'RL78', 'id': 'rl78', 'paging': True, 'data': [ {'post': {'layerId': 115079, 'layerIds': 115079}} ]},
	]

	specific_options_list = [

		# RX Family
		{'display': 'RX', 'id': 'rx', 'paging': True, 'data': [ {'post': {'layerId': 2881, 'layerIds': 2881}} ], 'custom': {'CategoryDeviceTopFamily': 'rx'}},
		# RX100
		{'display': 'RX100', 'id': 'rx100', 'paging': True, 'data': [ {'post': {'layerId': 175377, 'layerIds': 175377}} ], 'custom': {'CategoryDeviceTopFamily': 'rx'}},
		{'display': 'RX110', 'id': 'rx110', 'paging': True, 'data': [ {'post': {'layerId': 184785, 'layerIds': 184785}} ], 'custom': {'CategoryDeviceTopFamily': 'rx', 'CategoryDeviceFamily': 'rx110'}},
		{'display': 'RX111', 'id': 'rx111', 'paging': True, 'data': [ {'post': {'layerId': 175378, 'layerIds': 175378}} ], 'custom': {'CategoryDeviceTopFamily': 'rx', 'CategoryDeviceFamily': 'rx111'}},
		# RX200
		{'display': 'RX200', 'id': 'rx200', 'paging': True, 'data': [ {'post': {'layerId': 112383, 'layerIds': 112383}} ], 'custom': {'CategoryDeviceTopFamily': 'rx'}},
		{'display': 'RX210', 'id': 'rx210', 'paging': True, 'data': [ {'post': {'layerId': 112384, 'layerIds': 112384}} ], 'custom': {'CategoryDeviceTopFamily': 'rx', 'CategoryDeviceFamily': 'rx210'}},
		{'display': 'RX220', 'id': 'rx220', 'paging': True, 'data': [ {'post': {'layerId': 167804, 'layerIds': 167804}} ], 'custom': {'CategoryDeviceTopFamily': 'rx', 'CategoryDeviceFamily': 'rx220'}},
		{'display': 'RX21A', 'id': 'rx21a', 'paging': True, 'data': [ {'post': {'layerId': 158110, 'layerIds': 158110}} ], 'custom': {'CategoryDeviceTopFamily': 'rx', 'CategoryDeviceFamily': 'rx21a'}},
		# RX600
		{'display': 'RX600', 'id': 'rx600', 'paging': True, 'data': [ {'post': {'layerId': 2882, 'layerIds': 2882}} ], 'custom': {'CategoryDeviceTopFamily': 'rx'}},
		{'display': 'RX610', 'id': 'rx610', 'paging': True, 'data': [ {'post': {'layerId': 3010, 'layerIds': 3010}} ], 'custom': {'CategoryDeviceTopFamily': 'rx', 'CategoryDeviceFamily': 'rx610'}},
		{'display': 'RX62G', 'id': 'rx62g', 'paging': True, 'data': [ {'post': {'layerId': 115925, 'layerIds': 115925}} ], 'custom': {'CategoryDeviceTopFamily': 'rx', 'CategoryDeviceFamily': 'rx62g'}},
		{'display': 'RX62N/1', 'id': 'rx62n_621', 'paging': True, 'data': [ {'post': {'layerId': 3011, 'layerIds': 3011}} ], 'custom': {'CategoryDeviceTopFamily': 'rx', 'CategoryDeviceFamily': 'rx62n_621'}},
		{'display': 'RX62T', 'id': 'rx62t', 'paging': True, 'data': [ {'post': {'layerId': 106552, 'layerIds': 106552}} ], 'custom': {'CategoryDeviceTopFamily': 'rx', 'CategoryDeviceFamily': 'rx62t'}},
		{'display': 'RX630', 'id': 'rx630', 'paging': True, 'data': [ {'post': {'layerId': 112217, 'layerIds': 112217}} ], 'custom': {'CategoryDeviceTopFamily': 'rx', 'CategoryDeviceFamily': 'rx630'}},
		{'display': 'RX63N/1', 'id': 'rx63n_631', 'paging': True, 'data': [ {'post': {'layerId': 112234, 'layerIds': 112234}} ], 'custom': {'CategoryDeviceTopFamily': 'rx', 'CategoryDeviceFamily': 'rx63n_631'}},
		{'display': 'RX63T', 'id': 'rx63t', 'paging': True, 'data': [ {'post': {'layerId': 115924, 'layerIds': 115924}} ], 'custom': {'CategoryDeviceTopFamily': 'rx', 'CategoryDeviceFamily': 'rx63t'}},

		# H8 Value Series
		# No data

		# RL78 Family
		{'display': 'RL78', 'id': 'rl78', 'paging': True, 'data': [ {'post': {'layerId': 115079, 'layerIds': 115079}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78'}},
		# RL78D1x
		{'display': 'RL78/D1A', 'id': 'rl78d1a', 'paging': True, 'data': [ {'post': {'layerId': 169370, 'layerIds': 169370}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78d1a'}},
		# RL78F1x
		{'display': 'RL78/F12', 'id': 'rl78f12', 'paging': True, 'data': [ {'post': {'layerId': 115647, 'layerIds': 115647}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78f12'}},
		{'display': 'RL78/F13', 'id': 'rl78f13', 'paging': True, 'data': [ {'post': {'layerId': 185915, 'layerIds': 185915}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78f13'}},
		{'display': 'RL78/F14', 'id': 'rl78f14', 'paging': True, 'data': [ {'post': {'layerId': 185916, 'layerIds': 185916}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78f14'}},
		# RL78G1x
		{'display': 'RL78/G10', 'id': 'rl78g10', 'paging': True, 'data': [ {'post': {'layerId': 175355, 'layerIds': 175355}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78g10'}},
		{'display': 'RL78/G12', 'id': 'rl78g12', 'paging': True, 'data': [ {'post': {'layerId': 115081, 'layerIds': 115081}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78g12'}},
		{'display': 'RL78/G13', 'id': 'rl78g13', 'paging': True, 'data': [ {'post': {'layerId': 115082, 'layerIds': 115082}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78g13'}},
		{'display': 'RL78/G14', 'id': 'rl78g14', 'paging': True, 'data': [ {'post': {'layerId': 115085, 'layerIds': 115085}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78g14'}},
		{'display': 'RL78/G1A', 'id': 'rl78g1a', 'paging': True, 'data': [ {'post': {'layerId': 145847, 'layerIds': 145847}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78g1a'}},
		{'display': 'RL78/G1C', 'id': 'rl78g1c', 'paging': True, 'data': [ {'post': {'layerId': 169408, 'layerIds': 169408}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78g1c'}},
		# RL78I1x
		{'display': 'RL78/I1A', 'id': 'rl78i1a', 'paging': True, 'data': [ {'post': {'layerId': 115086, 'layerIds': 115086}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78i1a'}},
		# RL78L1x
		{'display': 'RL78/L12', 'id': 'rl78l12', 'paging': True, 'data': [ {'post': {'layerId': 158037, 'layerIds': 158037}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78l12'}},
		{'display': 'RL78/L13', 'id': 'rl78l13', 'paging': True, 'data': [ {'post': {'layerId': 167957, 'layerIds': 167957}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78l13'}},
		{'display': 'RL78/L1C', 'id': 'rl78l1c', 'paging': True, 'data': [ {'post': {'layerId': 185668, 'layerIds': 185668}} ], 'custom': {'CategoryDeviceTopFamily': 'rl78', 'CategoryDeviceFamily': 'rl78l1c'}},

		# 78K Family
		{'display': '78K', 'id': '78k', 'paging': True, 'data': [ {'post': {'layerId': 115087, 'layerIds': 115087}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		# 78K0/Dx
		{'display': '78K0/Dx', 'id': '78k0dx', 'paging': True, 'data': [ {'post': {'layerId': 115088, 'layerIds': 115088}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': '78K0/Dx2', 'id': '78k0dx2', 'paging': True, 'data': [ {'post': {'layerId': 115089, 'layerIds': 115089}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0dx2'}},
		# 78K0/Fx
		{'display': '78K0/Fx', 'id': '78k0fx', 'paging': True, 'data': [ {'post': {'layerId': 115091, 'layerIds': 115091}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': '78K0/Fx2', 'id': '78k0fx2', 'paging': True, 'data': [ {'post': {'layerId': 115092, 'layerIds': 115092}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0fx2'}},
		{'display': '78K0/Fx2-L', 'id': '78k0fx2l', 'paging': True, 'data': [ {'post': {'layerId': 115093, 'layerIds': 115093}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0fx2l'}},
		# 78K0/Ix
		{'display': '78K0/Ix', 'id': '78k0ix', 'paging': True, 'data': [ {'post': {'layerId': 115095, 'layerIds': 115095}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': '78K0/Ix2', 'id': '78k0ix2', 'paging': True, 'data': [ {'post': {'layerId': 115096, 'layerIds': 115096}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0ix2'}},
		# 78K0/Kx
		{'display': '78K0/Kx', 'id': '78k0kx', 'paging': True, 'data': [ {'post': {'layerId': 115097, 'layerIds': 115097}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': '78K0/Kx2', 'id': '78k0kx2', 'paging': True, 'data': [ {'post': {'layerId': 115098, 'layerIds': 115098}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0kx2'}},
		{'display': '78K0/Kx2-A', 'id': '78k0kx2a', 'paging': True, 'data': [ {'post': {'layerId': 115099, 'layerIds': 115099}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0kx2a'}},
		{'display': '78K0/Kx2-C', 'id': '78k0kx2c', 'paging': True, 'data': [ {'post': {'layerId': 115100, 'layerIds': 115100}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0kx2c'}},
		{'display': '78K0/Kx2-L', 'id': '78k0kx2l', 'paging': True, 'data': [ {'post': {'layerId': 115101, 'layerIds': 115101}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0kx2l'}},
		# 78K0/Lx
		{'display': '78K0/Lx', 'id': '78k0lx', 'paging': True, 'data': [ {'post': {'layerId': 115104, 'layerIds': 115104}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': '78K0/Lx3', 'id': '78k0lx3', 'paging': True, 'data': [ {'post': {'layerId': 115107, 'layerIds': 115107}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0lx3'}},
		{'display': '78K0/Lx3-M', 'id': '78k0lx3m', 'paging': True, 'data': [ {'post': {'layerId': 115109, 'layerIds': 115109}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0lx3m'}},
		# 78K0R/Fx
		{'display': '78K0R/Fx', 'id': '78k0rfx', 'paging': True, 'data': [ {'post': {'layerId': 115220, 'layerIds': 115220}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': '78K0R/Fx3', 'id': '78k0rfx3', 'paging': True, 'data': [ {'post': {'layerId': 115221, 'layerIds': 115221}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0rfx3'}},
		# 78K0R/Hx
		{'display': '78K0R/Hx', 'id': '78k0rhx', 'paging': True, 'data': [ {'post': {'layerId': 115222, 'layerIds': 115222}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': '78K0R/Hx3', 'id': '78k0rhx3', 'paging': True, 'data': [ {'post': {'layerId': 115223, 'layerIds': 115223}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0rhx3'}},
		# 78K0R/Ix
		{'display': '78K0R/Ix', 'id': '78k0rix', 'paging': True, 'data': [ {'post': {'layerId': 115224, 'layerIds': 115224}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': '78K0R/Ix3', 'id': '78k0rix3', 'paging': True, 'data': [ {'post': {'layerId': 115225, 'layerIds': 115225}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0rix3'}},
		# 78K0R/Kx
		{'display': '78K0R/Kx', 'id': '78k0rkx', 'paging': True, 'data': [ {'post': {'layerId': 115226, 'layerIds': 115226}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': '78K0R/Kx3', 'id': '78k0rkx3', 'paging': True, 'data': [ {'post': {'layerId': 115227, 'layerIds': 115227}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0rkx3'}},
		{'display': '78K0R/Kx3-A', 'id': '78k0rkx3a', 'paging': True, 'data': [ {'post': {'layerId': 115228, 'layerIds': 115228}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0rkx3a'}},
		{'display': '78K0R/Kx3-C', 'id': '78k0rkx3c', 'paging': True, 'data': [ {'post': {'layerId': 115229, 'layerIds': 115229}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0rkx3c'}},
		{'display': '78K0R/Kx3-L', 'id': '78k0rkx3l', 'paging': True, 'data': [ {'post': {'layerId': 115230, 'layerIds': 115230}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0rkx3l'}},
		{'display': '78K0R/Kx3-L (USB)', 'id': '78k0rkx3l_usb', 'paging': True, 'data': [ {'post': {'layerId': 115231, 'layerIds': 115231}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0rkx3l_usb'}},
		# 78K0R/Lx
		{'display': '78K0R/Lx', 'id': '78k0rlx', 'paging': True, 'data': [ {'post': {'layerId': 115232, 'layerIds': 115232}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': '78K0R/Lx3', 'id': '78k0rlx3', 'paging': True, 'data': [ {'post': {'layerId': 115233, 'layerIds': 115233}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0rlx3'}},
		{'display': '78K0R/Lx3-M', 'id': '78k0rlx3m', 'paging': True, 'data': [ {'post': {'layerId': 115234, 'layerIds': 115234}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0rlx3m'}},
		# 78K0S/Kx
		{'display': '78K0S/Kx', 'id': '78k0skx', 'paging': True, 'data': [ {'post': {'layerId': 115240, 'layerIds': 115240}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': '78K0S/Kx1+', 'id': '78k0skx1', 'paging': True, 'data': [ {'post': {'layerId': 115241, 'layerIds': 115241}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': '78k0skx1'}},
		# UPD179F1xx
		{'display': 'UPD179F1xx', 'id': 'upd179f1xx', 'paging': True, 'data': [ {'post': {'layerId': 115112, 'layerIds': 115112}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': 'UPD179F11x/UPD179F12x', 'id': 'upd179f11x_12x', 'paging': True, 'data': [ {'post': {'layerId': 115114, 'layerIds': 115114}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd179f11x_12x'}},
		# UPD78F07xx
		{'display': 'UPD78F07xx', 'id': 'upd78f07xx', 'paging': True, 'data': [ {'post': {'layerId': 115116, 'layerIds': 115116}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': 'UPD78F071x', 'id': 'upd78f071x', 'paging': True, 'data': [ {'post': {'layerId': 115117, 'layerIds': 115117}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78f071x'}},
		{'display': 'UPD78F073x', 'id': 'upd78f073x', 'paging': True, 'data': [ {'post': {'layerId': 115118, 'layerIds': 115118}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78f073x'}},
		# UPD78F80xx
		{'display': 'UPD78F80xx', 'id': 'upd78f80xx', 'paging': True, 'data': [ {'post': {'layerId': 115236, 'layerIds': 115236}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': 'UPD78F8025', 'id': 'upd78f8025', 'paging': True, 'data': [ {'post': {'layerId': 115237, 'layerIds': 115237}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78f8025'}},
		{'display': 'UPD78F8069', 'id': 'upd78f8069', 'paging': True, 'data': [ {'post': {'layerId': 183067, 'layerIds': 183067}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78f8069'}},
		# UPD7800xx
		{'display': 'UPD7800xx', 'id': 'upd7800xx', 'paging': True, 'data': [ {'post': {'layerId': 115122, 'layerIds': 115122}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': 'UPD78002xA', 'id': 'upd78002xa', 'paging': True, 'data': [ {'post': {'layerId': 115123, 'layerIds': 115123}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78002xa'}},
		{'display': 'UPD78003xA', 'id': 'upd78003xa', 'paging': True, 'data': [ {'post': {'layerId': 115126, 'layerIds': 115126}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78003xa'}},
		{'display': 'UPD78003xAS', 'id': 'upd78003xas', 'paging': True, 'data': [ {'post': {'layerId': 115136, 'layerIds': 115136}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78003xas'}},
		{'display': 'UPD78005x', 'id': 'upd78005x', 'paging': True, 'data': [ {'post': {'layerId': 115138, 'layerIds': 115138}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78005x'}},
		{'display': 'UPD78006x', 'id': 'upd78006x', 'paging': True, 'data': [ {'post': {'layerId': 115139, 'layerIds': 115139}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78006x'}},
		{'display': 'UPD78007x', 'id': 'upd78007x', 'paging': True, 'data': [ {'post': {'layerId': 115141, 'layerIds': 115141}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78007x'}},
		# UPD7802xx
		{'display': 'UPD7802xx', 'id': 'upd7802xx', 'paging': True, 'data': [ {'post': {'layerId': 115144, 'layerIds': 115144}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': 'UPD78023x', 'id': 'upd78023x', 'paging': True, 'data': [ {'post': {'layerId': 115147, 'layerIds': 115147}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78023x'}},
		# UPD7803xx
		{'display': 'UPD7803xx', 'id': 'upd7803xx', 'paging': True, 'data': [ {'post': {'layerId': 115148, 'layerIds': 115148}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': 'UPD78030x', 'id': 'upd78030x', 'paging': True, 'data': [ {'post': {'layerId': 115149, 'layerIds': 115149}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78030x'}},
		{'display': 'UPD78031x', 'id': 'upd78031x', 'paging': True, 'data': [ {'post': {'layerId': 115150, 'layerIds': 115150}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78031x'}},
		{'display': 'UPD78032x', 'id': 'upd78032x', 'paging': True, 'data': [ {'post': {'layerId': 115151, 'layerIds': 115151}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78032x'}},
		{'display': 'UPD78033x', 'id': 'upd78033x', 'paging': True, 'data': [ {'post': {'layerId': 115152, 'layerIds': 115152}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78033x'}},
		{'display': 'UPD78034x', 'id': 'upd78034x', 'paging': True, 'data': [ {'post': {'layerId': 115153, 'layerIds': 115153}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78034x'}},
		{'display': 'UPD78035x', 'id': 'upd78035x', 'paging': True, 'data': [ {'post': {'layerId': 115154, 'layerIds': 115154}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78035x'}},
		# UPD7808xx
		{'display': 'UPD7808xx', 'id': 'upd7808xx', 'paging': True, 'data': [ {'post': {'layerId': 115157, 'layerIds': 115157}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': 'UPD78086x', 'id': 'upd78086x', 'paging': True, 'data': [ {'post': {'layerId': 115158, 'layerIds': 115158}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78086x'}},
		# UPD7809xx
		{'display': 'UPD7809xx', 'id': 'upd7809xx', 'paging': True, 'data': [ {'post': {'layerId': 115159, 'layerIds': 115159}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': 'UPD78095x', 'id': 'upd78095x', 'paging': True, 'data': [ {'post': {'layerId': 115160, 'layerIds': 115160}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78095x'}},
		{'display': 'UPD78098x', 'id': 'upd78098x', 'paging': True, 'data': [ {'post': {'layerId': 115161, 'layerIds': 115161}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78098x'}},
		# UPD7890xx/7891xx
		{'display': 'UPD7890xx/7891xx', 'id': 'upd7890xx_1xx', 'paging': True, 'data': [ {'post': {'layerId': 115242, 'layerIds': 115242}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': 'UPD78902x', 'id': 'upd78902x', 'paging': True, 'data': [ {'post': {'layerId': 115244, 'layerIds': 115244}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78902x'}},
		{'display': 'UPD78904x', 'id': 'upd78904x', 'paging': True, 'data': [ {'post': {'layerId': 115245, 'layerIds': 115245}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78904x'}},
		{'display': 'UPD78905x', 'id': 'upd78905x', 'paging': True, 'data': [ {'post': {'layerId': 115379, 'layerIds': 115379}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78905x'}},
		{'display': 'UPD78906x', 'id': 'upd78906x', 'paging': True, 'data': [ {'post': {'layerId': 115380, 'layerIds': 115380}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78906x'}},
		{'display': 'UPD78907x', 'id': 'upd78907x', 'paging': True, 'data': [ {'post': {'layerId': 115246, 'layerIds': 115246}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78907x'}},
		{'display': 'UPD78908x', 'id': 'upd78908x', 'paging': True, 'data': [ {'post': {'layerId': 115247, 'layerIds': 115247}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78908x'}},
		{'display': 'UPD78910xA', 'id': 'upd78910xa', 'paging': True, 'data': [ {'post': {'layerId': 115248, 'layerIds': 115248}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78910xa'}},
		{'display': 'UPD78911xA', 'id': 'upd78911xa', 'paging': True, 'data': [ {'post': {'layerId': 115250, 'layerIds': 115250}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78911xa'}},
		{'display': 'UPD78913xA', 'id': 'upd78913xa', 'paging': True, 'data': [ {'post': {'layerId': 115254, 'layerIds': 115254}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78913xa'}},
		{'display': 'UPD78916x', 'id': 'upd78916x', 'paging': True, 'data': [ {'post': {'layerId': 115255, 'layerIds': 115255}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78916x'}},
		{'display': 'UPD78917x', 'id': 'upd78917x', 'paging': True, 'data': [ {'post': {'layerId': 115256, 'layerIds': 115256}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78917x'}},
		# UPD7893xx/7894xx
		{'display': 'UPD7893xx/7894xx', 'id': 'upd7893xx_4xx', 'paging': True, 'data': [ {'post': {'layerId': 115257, 'layerIds': 115257}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': 'UPD78930x', 'id': 'upd78930x', 'paging': True, 'data': [ {'post': {'layerId': 115258, 'layerIds': 115258}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78930x'}},
		{'display': 'UPD78931x', 'id': 'upd78931x', 'paging': True, 'data': [ {'post': {'layerId': 115259, 'layerIds': 115259}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78931x'}},
		{'display': 'UPD78932x', 'id': 'upd78932x', 'paging': True, 'data': [ {'post': {'layerId': 115260, 'layerIds': 115260}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78932x'}},
		{'display': 'UPD78940xA', 'id': 'upd78940xa', 'paging': True, 'data': [ {'post': {'layerId': 115261, 'layerIds': 115261}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78940xa'}},
		{'display': 'UPD78941xA', 'id': 'upd78941xa', 'paging': True, 'data': [ {'post': {'layerId': 115262, 'layerIds': 115262}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78941xa'}},
		{'display': 'UPD78942x', 'id': 'upd78942x', 'paging': True, 'data': [ {'post': {'layerId': 115263, 'layerIds': 115263}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78942x'}},
		{'display': 'UPD78943x', 'id': 'upd78943x', 'paging': True, 'data': [ {'post': {'layerId': 115264, 'layerIds': 115264}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78943x'}},
		{'display': 'UPD78944x', 'id': 'upd78944x', 'paging': True, 'data': [ {'post': {'layerId': 115265, 'layerIds': 115265}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78944x'}},
		{'display': 'UPD78945x', 'id': 'upd78945x', 'paging': True, 'data': [ {'post': {'layerId': 115266, 'layerIds': 115266}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78945x'}},
		{'display': 'UPD78946x', 'id': 'upd78946x', 'paging': True, 'data': [ {'post': {'layerId': 115267, 'layerIds': 115267}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78946x'}},
		{'display': 'UPD78947x', 'id': 'upd78947x', 'paging': True, 'data': [ {'post': {'layerId': 115268, 'layerIds': 115268}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78947x'}},
		{'display': 'UPD78948x', 'id': 'upd78948x', 'paging': True, 'data': [ {'post': {'layerId': 115269, 'layerIds': 115269}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78948x'}},
		# UPD7898xx
		{'display': 'UPD7898xx', 'id': 'upd7898xx', 'paging': True, 'data': [ {'post': {'layerId': 115270, 'layerIds': 115270}} ], 'custom': {'CategoryDeviceTopFamily': '78k'}},
		{'display': 'UPD78980x', 'id': 'upd78980x', 'paging': True, 'data': [ {'post': {'layerId': 115271, 'layerIds': 115271}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78980x'}},
		{'display': 'UPD78983x', 'id': 'upd78983x', 'paging': True, 'data': [ {'post': {'layerId': 115272, 'layerIds': 115272}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78983x'}},
		{'display': 'UPD78988x', 'id': 'upd78988x', 'paging': True, 'data': [ {'post': {'layerId': 115277, 'layerIds': 115277}} ], 'custom': {'CategoryDeviceTopFamily': '78k', 'CategoryDeviceFamily': 'upd78988x'}},

		# M32R Family
		# M32R/ECU
		# M32176
		{'display': 'M32176', 'id': 'm32176', 'paging': True, 'data': [ {'post': {'layerId': 43, 'layerIds': 43}} ], 'custom': {'CategoryDeviceTopFamily': 'm32r', 'CategoryDeviceFamily': '32176'}},
		{'display': 'M32186', 'id': 'm32186', 'paging': True, 'data': [ {'post': {'layerId': 1653, 'layerIds': 1653}} ], 'custom': {'CategoryDeviceTopFamily': 'm32r', 'CategoryDeviceFamily': '32186'}},
		{'display': 'M32192', 'id': 'm32192', 'paging': True, 'data': [ {'post': {'layerId': 40, 'layerIds': 40}} ], 'custom': {'CategoryDeviceTopFamily': 'm32r', 'CategoryDeviceFamily': '32192'}},
		{'display': 'M32196', 'id': 'm32196', 'paging': True, 'data': [ {'post': {'layerId': 1654, 'layerIds': 1654}} ], 'custom': {'CategoryDeviceTopFamily': 'm32r', 'CategoryDeviceFamily': '32196'}},

		# M16C Family (R32C/M32C/M16C)
		# R32C/100
		{'display': 'R32C/160, R32C/161', 'id': 'r32c160_161', 'paging': True, 'data': [ {'post': {'layerId': 2491, 'layerIds': 2491}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'r32c160_161'}},
		{'display': 'R32C/151, R32C/152, R32C/153, R32C/156, R32C/157', 'id': 'r32c151_152_153_156_157', 'paging': True, 'data': [ {'post': {'layerId': 2490, 'layerIds': 2490}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'r32c151_152_153_156_157'}},
		{'display': 'R32C/142, R32C/145', 'id': 'r32c142_145', 'paging': True, 'data': [ {'post': {'layerId': 2737, 'layerIds': 2737}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'r32c142_145'}},
		{'display': 'R32C/120, R32C/121', 'id': 'r32c120_121', 'paging': True, 'data': [ {'post': {'layerId': 2488, 'layerIds': 2488}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'r32c120_121'}},
		{'display': 'R32C/116A, R32C/117A, R32C/118A', 'id': 'r32c116a_117a_118a', 'paging': True, 'data': [ {'post': {'layerId': 106550, 'layerIds': 106550}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'r32c116a_117a_118a'}},
		{'display': 'R32C/116, R32C/117, R32C/118', 'id': 'r32c116_117_118', 'paging': True, 'data': [ {'post': {'layerId': 2662, 'layerIds': 2662}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'r32c116_117_118'}},
		{'display': 'R32C/111', 'id': 'r32c111', 'paging': True, 'data': [ {'post': {'layerId': 2468, 'layerIds': 2468}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'r32c111'}},
		# M32C/80
		{'display': 'M32C/8B', 'id': 'm32c8b', 'paging': True, 'data': [ {'post': {'layerId': 2511, 'layerIds': 2511}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm32c8b'}},
		{'display': 'M32C/8A', 'id': 'm32c8a', 'paging': True, 'data': [ {'post': {'layerId': 2384, 'layerIds': 2384}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm32c8a'}},
		{'display': 'M32C/88', 'id': 'm32c88', 'paging': True, 'data': [ {'post': {'layerId': 1623, 'layerIds': 1623}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm32c88'}},
		{'display': 'M32C/87', 'id': 'm32c87', 'paging': True, 'data': [ {'post': {'layerId': 51, 'layerIds': 51}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm32c87'}},
		{'display': 'M32C/85', 'id': 'm32c85', 'paging': True, 'data': [ {'post': {'layerId': 52, 'layerIds': 52}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm32c85'}},
		{'display': 'M32C/84', 'id': 'm32c84', 'paging': True, 'data': [ {'post': {'layerId': 53, 'layerIds': 53}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm32c84'}},
		{'display': 'M32C/83', 'id': 'm32c83', 'paging': True, 'data': [ {'post': {'layerId': 54, 'layerIds': 54}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm32c83'}},
		{'display': 'M32C/80', 'id': 'm32c80', 'paging': True, 'data': [ {'post': {'layerId': 57, 'layerIds': 57}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm32c80'}},
		{'display': 'M32C/86', 'id': 'm32c86', 'paging': True, 'data': [ {'post': {'layerId': 57, 'layerIds': 57}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm32c86'}},
		# M16C/60
		{'display': 'M16C/65C', 'id': 'm16c65c', 'paging': True, 'data': [ {'post': {'layerId': 112212, 'layerIds': 112212}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c65c'}},
		{'display': 'M16C/65', 'id': 'm16c65', 'paging': True, 'data': [ {'post': {'layerId': 2391, 'layerIds': 2391}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c65'}},
		{'display': 'M16C/64C', 'id': 'm16c64c', 'paging': True, 'data': [ {'post': {'layerId': 112211, 'layerIds': 112211}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c64c'}},
		{'display': 'M16C/64A', 'id': 'm16c64a', 'paging': True, 'data': [ {'post': {'layerId': 2849, 'layerIds': 2849}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c64a'}},
		{'display': 'M16C/63', 'id': 'm16c63', 'paging': True, 'data': [ {'post': {'layerId': 2738, 'layerIds': 2738}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c63'}},
		{'display': 'M16C/6C', 'id': 'm16c6c', 'paging': True, 'data': [ {'post': {'layerId': 2808, 'layerIds': 2808}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c6c'}},
		{'display': 'M16C/6B', 'id': 'm16c6b', 'paging': True, 'data': [ {'post': {'layerId': 2866, 'layerIds': 2866}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c6b'}},
		{'display': 'M16C/62P', 'id': 'm16c62p', 'paging': True, 'data': [ {'post': {'layerId': 330, 'layerIds': 330}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c62p'}},
		{'display': 'M16C/62N', 'id': 'm16c62n', 'paging': True, 'data': [ {'post': {'layerId': 329, 'layerIds': 329}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c62n'}},
		{'display': 'M16C/62A, M16C/62M', 'id': 'm16c62a_62m', 'paging': True, 'data': [ {'post': {'layerId': 328, 'layerIds': 328}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c62a_62m'}},
		{'display': 'M16C/6N4, M16C/6N5', 'id': 'm16c6n4_6n5', 'paging': True, 'data': [ {'post': {'layerId': 66, 'layerIds': 66}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c6n4_6n5'}},
		{'display': 'M16C/6NK, M16C/6NL, M16C/6NM, M16C/6NN', 'id': 'm16c6nk_6nl_6nm_6nn', 'paging': True, 'data': [ {'post': {'layerId': 1597, 'layerIds': 1597}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c6nk_6nl_6nm_6nn'}},
		{'display': 'M16C/64', 'id': 'm16c64', 'paging': True, 'data': [ {'post': {'layerId': 2390, 'layerIds': 2390}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c64'}},
		{'display': 'M16C/6S1', 'id': 'm16c6s1', 'paging': True, 'data': [ {'post': {'layerId': 112754, 'layerIds': 112754}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c6s1'}},
		# M16C/50
		{'display': 'M16C/5M, M16C/57', 'id': 'm16c5m_57', 'paging': True, 'data': [ {'post': {'layerId': 2752, 'layerIds': 2752}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c5m_57'}},
		{'display': 'M16C/5L, M16C/56', 'id': 'm16c5l_56', 'paging': True, 'data': [ {'post': {'layerId': 2751, 'layerIds': 2751}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c5l_56'}},
		{'display': 'M16C/5LD, M16C/56D', 'id': 'm16c5ld_56d', 'paging': True, 'data': [ {'post': {'layerId': 2995, 'layerIds': 2995}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c5ld_56d'}},
		# M16C/30
		{'display': 'M16C/30P', 'id': 'm16c30p', 'paging': True, 'data': [ {'post': {'layerId': 907, 'layerIds': 907}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c30p'}},
		# M16C/Tiny
		{'display': 'M16C/26A', 'id': 'm16c26a', 'paging': True, 'data': [ {'post': {'layerId': 916, 'layerIds': 916}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c26a'}},
		{'display': 'M16C/28', 'id': 'm16c28', 'paging': True, 'data': [ {'post': {'layerId': 77, 'layerIds': 77}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c28'}},
		{'display': 'M16C/29', 'id': 'm16c29', 'paging': True, 'data': [ {'post': {'layerId': 76, 'layerIds': 76}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c29'}},
		# M16C/20
		# No data
		# M16C/10
		{'display': 'M16C/1N', 'id': 'm16c1n', 'paging': True, 'data': [ {'post': {'layerId': 80, 'layerIds': 80}} ], 'custom': {'CategoryDeviceTopFamily': 'm16c', 'CategoryDeviceFamily': 'm16c1n'}},
		# M16C/80
		# No data

		# R8C Family
		{'display': 'R8C', 'id': 'r8c', 'paging': True, 'data': [ {'post': {'layerId': 81, 'layerIds': 81}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c'}},
		# R8C/Lx
		{'display': 'R8C/Lx', 'id': 'r8clx', 'paging': True, 'data': [ {'post': {'layerId': 2710, 'layerIds': 2710}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c'}},
		{'display': 'R8C/L3AA, R8C/L3AB Group', 'id': 'r8cl3aa_l3ab', 'paging': True, 'data': [ {'post': {'layerId': 2714, 'layerIds': 2714}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cl3aa_l3ab'}},
		{'display': 'R8C/L35C', 'id': 'r8cl35c', 'paging': True, 'data': [ {'post': {'layerId': 3007, 'layerIds': 3007}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cl35c'}},
		{'display': 'R8C/L36C', 'id': 'r8cl36c', 'paging': True, 'data': [ {'post': {'layerId': 3006, 'layerIds': 3006}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cl36c'}},
		{'display': 'R8C/L38C', 'id': 'r8cl38c', 'paging': True, 'data': [ {'post': {'layerId': 3005, 'layerIds': 3005}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cl38c'}},
		{'display': 'R8C/L3AC', 'id': 'r8cl3ac', 'paging': True, 'data': [ {'post': {'layerId': 3004, 'layerIds': 3004}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cl3ac'}},
		{'display': 'R8C/L35M', 'id': 'r8cl35m', 'paging': True, 'data': [ {'post': {'layerId': 108320, 'layerIds': 108320}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cl35m'}},
		{'display': 'R8C/L36M', 'id': 'r8cl36m', 'paging': True, 'data': [ {'post': {'layerId': 108321, 'layerIds': 108321}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cl36m'}},
		{'display': 'R8C/L38M', 'id': 'r8cl38m', 'paging': True, 'data': [ {'post': {'layerId': 108322, 'layerIds': 108322}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cl38m'}},
		{'display': 'R8C/L3AM', 'id': 'r8cl3am', 'paging': True, 'data': [ {'post': {'layerId': 108323, 'layerIds': 108323}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cl3am'}},
		{'display': 'R8C/LA3A', 'id': 'r8cla3a', 'paging': True, 'data': [ {'post': {'layerId': 3102, 'layerIds': 3102}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cla3a'}},
		{'display': 'R8C/LA5A', 'id': 'r8cla5a', 'paging': True, 'data': [ {'post': {'layerId': 3101, 'layerIds': 3101}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cla5a'}},
		{'display': 'R8C/LA6A', 'id': 'r8cla6a', 'paging': True, 'data': [ {'post': {'layerId': 3096, 'layerIds': 3096}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cla6a'}},
		{'display': 'R8C/LA8A', 'id': 'r8cla8a', 'paging': True, 'data': [ {'post': {'layerId': 3097, 'layerIds': 3097}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cla8a'}},
		{'display': 'R8C/LAPS', 'id': 'r8claps', 'paging': True, 'data': [ {'post': {'layerId': 115772, 'layerIds': 115772}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8claps'}},
		{'display': 'R8C/LAPS', 'id': 'r8claps', 'paging': True, 'data': [ {'post': {'layerId': 115772, 'layerIds': 115772}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8claps'}},
		{'display': 'R8C/L36A, R8C/L36B', 'id': 'r8cl36a_l36b', 'paging': True, 'data': [ {'post': {'layerId': 2712, 'layerIds': 2712}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cl36a_l36b'}},
		# R8C/Mx
		{'display': 'R8C/Mx', 'id': 'r8cmx', 'paging': True, 'data': [ {'post': {'layerId': 3098, 'layerIds': 3098}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c'}},
		{'display': 'R8C/M11A', 'id': 'r8cm11a', 'paging': True, 'data': [ {'post': {'layerId': 3099, 'layerIds': 3099}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cm11a'}},
		{'display': 'R8C/M12A', 'id': 'r8cm12a', 'paging': True, 'data': [ {'post': {'layerId': 3100, 'layerIds': 3100}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cm12a'}},
		{'display': 'R8C/M13B', 'id': 'r8cm13b', 'paging': True, 'data': [ {'post': {'layerId': 108283, 'layerIds': 108283}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8cm13b'}},
		# R8C/5x
		{'display': 'R8C/5x', 'id': 'r8c5x', 'paging': True, 'data': [ {'post': {'layerId': 113446, 'layerIds': 113446}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c'}},
		{'display': 'R8C/54E, R8C/54F, R8C/54G, R8C/54H', 'id': 'r8c54e_54f_54g_54h', 'paging': True, 'data': [ {'post': {'layerId': 113447, 'layerIds': 113447}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c54e_54f_54g_54h'}},
		{'display': 'R8C/56E, R8C/56F, R8C/56G, R8C/56H', 'id': 'r8c56e_56f_56g_56h', 'paging': True, 'data': [ {'post': {'layerId': 113448, 'layerIds': 113448}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c56e_56f_56g_56h'}},
		# R8C/3x
		{'display': 'R8C/3x', 'id': 'r8c3x', 'paging': True, 'data': [ {'post': {'layerId': 2781, 'layerIds': 2781}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c'}},
		{'display': 'R8C/38A', 'id': 'r8c38a', 'paging': True, 'data': [ {'post': {'layerId': 2960, 'layerIds': 2960}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c38a'}},
		{'display': 'R8C/32C', 'id': 'r8c32c', 'paging': True, 'data': [ {'post': {'layerId': 2986, 'layerIds': 2986}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c32c'}},
		{'display': 'R8C/33C', 'id': 'r8c33c', 'paging': True, 'data': [ {'post': {'layerId': 2987, 'layerIds': 2987}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c33c'}},
		{'display': 'R8C/34C', 'id': 'r8c34c', 'paging': True, 'data': [ {'post': {'layerId': 106705, 'layerIds': 106705}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c34c'}},
		{'display': 'R8C/35C', 'id': 'r8c35c', 'paging': True, 'data': [ {'post': {'layerId': 2988, 'layerIds': 2988}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c35c'}},
		{'display': 'R8C/36C', 'id': 'r8c36c', 'paging': True, 'data': [ {'post': {'layerId': 3015, 'layerIds': 3015}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c36c'}},
		{'display': 'R8C/38C', 'id': 'r8c38c', 'paging': True, 'data': [ {'post': {'layerId': 3016, 'layerIds': 3016}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c38c'}},
		{'display': 'R8C/3GC', 'id': 'r8c3gc', 'paging': True, 'data': [ {'post': {'layerId': 106707, 'layerIds': 106707}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c3gc'}},
		{'display': 'R8C/3JC', 'id': 'r8c3jc', 'paging': True, 'data': [ {'post': {'layerId': 106706, 'layerIds': 106706}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c3jc'}},
		{'display': 'R8C/32D', 'id': 'r8c32d', 'paging': True, 'data': [ {'post': {'layerId': 2989, 'layerIds': 2989}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c32d'}},
		{'display': 'R8C/33D', 'id': 'r8c33d', 'paging': True, 'data': [ {'post': {'layerId': 2990, 'layerIds': 2990}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c33d'}},
		{'display': 'R8C/35D', 'id': 'r8c35d', 'paging': True, 'data': [ {'post': {'layerId': 2991, 'layerIds': 2991}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c35d'}},
		{'display': 'R8C/3GD', 'id': 'r8c3gd', 'paging': True, 'data': [ {'post': {'layerId': 2992, 'layerIds': 2992}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c3gd'}},
		{'display': 'R8C/32M', 'id': 'r8c32m', 'paging': True, 'data': [ {'post': {'layerId': 108316, 'layerIds': 108316}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c32m'}},
		{'display': 'R8C/33M', 'id': 'r8c33m', 'paging': True, 'data': [ {'post': {'layerId': 108317, 'layerIds': 108317}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c33m'}},
		{'display': 'R8C/34M', 'id': 'r8c34m', 'paging': True, 'data': [ {'post': {'layerId': 108318, 'layerIds': 108318}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c34m'}},
		{'display': 'R8C/35M', 'id': 'r8c35m', 'paging': True, 'data': [ {'post': {'layerId': 108319, 'layerIds': 108319}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c35m'}},
		{'display': 'R8C/36M', 'id': 'r8c36m', 'paging': True, 'data': [ {'post': {'layerId': 113143, 'layerIds': 113143}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c36m'}},
		{'display': 'R8C/38M', 'id': 'r8c38m', 'paging': True, 'data': [ {'post': {'layerId': 113144, 'layerIds': 113144}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c38m'}},
		{'display': 'R8C/3GM', 'id': 'r8c3gm', 'paging': True, 'data': [ {'post': {'layerId': 115445, 'layerIds': 115445}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c3gm'}},
		{'display': 'R8C/3JM', 'id': 'r8c3jm', 'paging': True, 'data': [ {'post': {'layerId': 115446, 'layerIds': 115446}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c3jm'}},
		{'display': 'R8C/33T', 'id': 'r8c33t', 'paging': True, 'data': [ {'post': {'layerId': 2980, 'layerIds': 2980}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c33t'}},
		{'display': 'R8C/3JT', 'id': 'r8c3jt', 'paging': True, 'data': [ {'post': {'layerId': 107972, 'layerIds': 107972}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c3jt'}},
		{'display': 'R8C/36T-A', 'id': 'r8c36ta', 'paging': True, 'data': [ {'post': {'layerId': 115410, 'layerIds': 115410}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c36ta'}},
		{'display': 'R8C/38T-A', 'id': 'r8c38ta', 'paging': True, 'data': [ {'post': {'layerId': 115411, 'layerIds': 115411}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c38ta'}},
		{'display': 'R8C/3MK', 'id': 'r8c3mk', 'paging': True, 'data': [ {'post': {'layerId': 112218, 'layerIds': 112218}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c3mk'}},
		{'display': 'R8C/34K', 'id': 'r8c34k', 'paging': True, 'data': [ {'post': {'layerId': 112219, 'layerIds': 112219}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c34k'}},
		{'display': 'R8C/3MU', 'id': 'r8c3mu', 'paging': True, 'data': [ {'post': {'layerId': 108284, 'layerIds': 108284}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c3mu'}},
		{'display': 'R8C/3MQ', 'id': 'r8c3mq', 'paging': True, 'data': [ {'post': {'layerId': 112216, 'layerIds': 112216}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c3mq'}},
		{'display': 'R8C/34U', 'id': 'r8c34u', 'paging': True, 'data': [ {'post': {'layerId': 112220, 'layerIds': 112220}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c34u'}},
		{'display': 'R8C/32G, R8C/32H', 'id': 'r8c32g_32h', 'paging': True, 'data': [ {'post': {'layerId': 112213, 'layerIds': 112213}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c32g_32h'}},
		{'display': 'R8C/33G, R8C/33H', 'id': 'r8c33g_33h', 'paging': True, 'data': [ {'post': {'layerId': 108028, 'layerIds': 108028}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c33g_33h'}},
		{'display': 'R8C/34P, R8C/34R', 'id': 'r8c34p_34r', 'paging': True, 'data': [ {'post': {'layerId': 112409, 'layerIds': 112409}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c34p_34r'}},
		{'display': 'R8C/34W, R8C/34X, R8C/34Y, R8C/34Z', 'id': 'r8c34w_34x_34y_34z', 'paging': True, 'data': [ {'post': {'layerId': 107153, 'layerIds': 107153}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c34w_34x_34y_34z'}},
		{'display': 'R8C/36W, R8C/36X, R8C/36Y, R8C/36Z', 'id': 'r8c36w_36x_36y_36z', 'paging': True, 'data': [ {'post': {'layerId': 107166, 'layerIds': 107166}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c36w_36x_36y_36z'}},
		{'display': 'R8C/38W, R8C/38X, R8C/38Y, R8C/38Z', 'id': 'r8c38w_38x_38y_38z', 'paging': True, 'data': [ {'post': {'layerId': 107167, 'layerIds': 107167}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c38w_38x_38y_38z'}},
		{'display': 'R8C/35A', 'id': 'r8c35a', 'paging': True, 'data': [ {'post': {'layerId': 2472, 'layerIds': 2472}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c35a'}},
		{'display': 'R8C/36A', 'id': 'r8c36a', 'paging': True, 'data': [ {'post': {'layerId': 2959, 'layerIds': 2959}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c36a'}},
		{'display': 'R8C/3GA', 'id': 'r8c3ga', 'paging': True, 'data': [ {'post': {'layerId': 2961, 'layerIds': 2961}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c3ga'}},
		# R8C/2x
		{'display': 'R8C/2x', 'id': 'r8c2x', 'paging': True, 'data': [ {'post': {'layerId': 2780, 'layerIds': 2780}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c'}},
		{'display': 'R8C/20', 'id': 'r8c20', 'paging': True, 'data': [ {'post': {'layerId': 1681, 'layerIds': 1681}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c20'}},
		{'display': 'R8C/21', 'id': 'r8c21', 'paging': True, 'data': [ {'post': {'layerId': 1682, 'layerIds': 1682}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c21'}},
		{'display': 'R8C/22', 'id': 'r8c22', 'paging': True, 'data': [ {'post': {'layerId': 1683, 'layerIds': 1683}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c22'}},
		{'display': 'R8C/23', 'id': 'r8c23', 'paging': True, 'data': [ {'post': {'layerId': 1684, 'layerIds': 1684}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c23'}},
		{'display': 'R8C/24', 'id': 'r8c24', 'paging': True, 'data': [ {'post': {'layerId': 1685, 'layerIds': 1685}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c24'}},
		{'display': 'R8C/25', 'id': 'r8c25', 'paging': True, 'data': [ {'post': {'layerId': 1686, 'layerIds': 1686}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c25'}},
		{'display': 'R8C/26', 'id': 'r8c26', 'paging': True, 'data': [ {'post': {'layerId': 1921, 'layerIds': 1921}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c26'}},
		{'display': 'R8C/27', 'id': 'r8c27', 'paging': True, 'data': [ {'post': {'layerId': 1922, 'layerIds': 1922}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c27'}},
		{'display': 'R8C/28', 'id': 'r8c28', 'paging': True, 'data': [ {'post': {'layerId': 1923, 'layerIds': 1923}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c28'}},
		{'display': 'R8C/29', 'id': 'r8c29', 'paging': True, 'data': [ {'post': {'layerId': 1924, 'layerIds': 1924}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c29'}},
		{'display': 'R8C/2A', 'id': 'r8c2a', 'paging': True, 'data': [ {'post': {'layerId': 2122, 'layerIds': 2122}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c2a'}},
		{'display': 'R8C/2B', 'id': 'r8c2b', 'paging': True, 'data': [ {'post': {'layerId': 2123, 'layerIds': 2123}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c2b'}},
		{'display': 'R8C/2C', 'id': 'r8c2c', 'paging': True, 'data': [ {'post': {'layerId': 2124, 'layerIds': 2124}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c2c'}},
		{'display': 'R8C/2D', 'id': 'r8c2d', 'paging': True, 'data': [ {'post': {'layerId': 2125, 'layerIds': 2125}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c2d'}},
		{'display': 'R8C/2E', 'id': 'r8c2e', 'paging': True, 'data': [ {'post': {'layerId': 2445, 'layerIds': 2445}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c2e'}},
		{'display': 'R8C/2F', 'id': 'r8c2f', 'paging': True, 'data': [ {'post': {'layerId': 2446, 'layerIds': 2446}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c2f'}},
		{'display': 'R8C/2G', 'id': 'r8c2g', 'paging': True, 'data': [ {'post': {'layerId': 2447, 'layerIds': 2447}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c2g'}},
		{'display': 'R8C/2H', 'id': 'r8c2h', 'paging': True, 'data': [ {'post': {'layerId': 2448, 'layerIds': 2448}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c2h'}},
		{'display': 'R8C/2J', 'id': 'r8c2j', 'paging': True, 'data': [ {'post': {'layerId': 2449, 'layerIds': 2449}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c2j'}},
		{'display': 'R8C/2K', 'id': 'r8c2k', 'paging': True, 'data': [ {'post': {'layerId': 2450, 'layerIds': 2450}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c2k'}},
		{'display': 'R8C/2L', 'id': 'r8c2l', 'paging': True, 'data': [ {'post': {'layerId': 2451, 'layerIds': 2451}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c2l'}},
		# R8C/1x
		{'display': 'R8C/1x', 'id': 'r8c1x', 'paging': True, 'data': [ {'post': {'layerId': 2779, 'layerIds': 2779}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c'}},
		{'display': 'R8C/18', 'id': 'r8c18', 'paging': True, 'data': [ {'post': {'layerId': 1647, 'layerIds': 1647}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c18'}},
		{'display': 'R8C/19', 'id': 'r8c19', 'paging': True, 'data': [ {'post': {'layerId': 1648, 'layerIds': 1648}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c19'}},
		{'display': 'R8C/1A', 'id': 'r8c1a', 'paging': True, 'data': [ {'post': {'layerId': 1733, 'layerIds': 1733}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c1a'}},
		{'display': 'R8C/1B', 'id': 'r8c1b', 'paging': True, 'data': [ {'post': {'layerId': 1734, 'layerIds': 1734}} ], 'custom': {'CategoryDeviceTopFamily': 'r8c', 'CategoryDeviceFamily': 'r8c1b'}},

		# RZ Family
		{'display': 'RZ Family', 'id': 'rz', 'paging': True, 'data': [ {'post': {'layerId': 184671, 'layerIds': 184671}} ], 'custom': {'CategoryDeviceTopFamily': 'rz'}},
		# RZ/A Family
		{'display': 'RZ/A', 'id': 'rza', 'paging': True, 'data': [ {'post': {'layerId': 184672, 'layerIds': 184672}} ], 'custom': {'CategoryDeviceTopFamily': 'rz'}},
		{'display': 'RZ/A1', 'id': 'rza1', 'paging': True, 'data': [ {'post': {'layerId': 184673, 'layerIds': 184673}} ], 'custom': {'CategoryDeviceTopFamily': 'rz', 'CategoryDeviceFamily': 'rza1'}},

		# SuperH RISC engine Family
		{'display': 'SuperH Family', 'id': 'superh', 'paging': True, 'data': [ {'post': {'layerId': 2, 'layerIds': 2}} ], 'custom': {'CategoryDeviceTopFamily': 'superh'}},
		# SH72Ax Series
		{'display': 'SH72Ax', 'id': 'sh72ax', 'paging': True, 'data': [ {'post': {'layerId': 154309, 'layerIds': 154309}} ], 'custom': {'CategoryDeviceTopFamily': 'superh'}},
		{'display': 'SH72A0, SH72A2', 'id': 'sh72a0_a2', 'paging': True, 'data': [ {'post': {'layerId': 154318, 'layerIds': 154318}} ], 'custom': {'CategoryDeviceTopFamily': 'superh', 'CategoryDeviceFamily': 'sh72a0_a2'}},
		{'display': 'SH72AW, SH72AY', 'id': 'sh72aw_ay', 'paging': True, 'data': [ {'post': {'layerId': 154317, 'layerIds': 154317}} ], 'custom': {'CategoryDeviceTopFamily': 'superh', 'CategoryDeviceFamily': 'sh72aw_ay'}},
		# SH7250 Series
		{'display': 'SH7250', 'id': 'sh7250', 'paging': True, 'data': [ {'post': {'layerId': 2754, 'layerIds': 2754}} ], 'custom': {'CategoryDeviceTopFamily': 'superh'}},
		{'display': 'SH7253', 'id': 'sh7253', 'paging': True, 'data': [ {'post': {'layerId': 3025, 'layerIds': 3025}} ], 'custom': {'CategoryDeviceTopFamily': 'superh', 'CategoryDeviceFamily': 'sh7253'}},
		{'display': 'SH7254R', 'id': 'sh7254r', 'paging': True, 'data': [ {'post': {'layerId': 2755, 'layerIds': 2755}} ], 'custom': {'CategoryDeviceTopFamily': 'superh', 'CategoryDeviceFamily': 'sh7254r'}},
		{'display': 'SH7256R', 'id': 'sh7256r', 'paging': True, 'data': [ {'post': {'layerId': 112274, 'layerIds': 112274}} ], 'custom': {'CategoryDeviceTopFamily': 'superh', 'CategoryDeviceFamily': 'sh7256r'}},

	]

	def update_options(self, page_number, options):
		return {'data': {'post': { 'pageNo': (page_number + 1) }}}

	def setup_specific_parser_rules(self, parser):
		pass
