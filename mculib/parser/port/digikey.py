#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

# Implement using this: https://services.digikey.com/

from mculib.parser.generic import *
from mculib.parser.deep import *
from mculib.parser.html_table import *

from bs4 import BeautifulSoup

import urllib

class DigikeyCommon(GenericParserPort):
	@staticmethod
	def get_manufacturer():
		return "digikey"

	def setup_specific_parser_rules(self, parser):
		pass

	def setup_parser_rules(self, parser):
		"""
		Rules that applies specificly to DigiKey
		"""
		def category_pre_processing_hook(category, options):
			if category.to_param() in ["CategoryOrderPage"]:
				category.set_base_url("http://www.digikey.com/")

		parser.hook("pre_category_discovery", category_pre_processing_hook)
		self.setup_specific_parser_rules(parser)

class DigikeyParser(HTMLTableParser):
	"""
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
			<div class="paging" style="display: inline;">
				<span class="current-page">Page 1/1</span>
			</div>
		"""
		soup = BeautifulSoup(data)
		# Read the number of pages
		match_list = soup.find_all("span", {"class" : "current-page"})
		# If not fond, it means this went directly to the product detail page or there is no entries
		if len(match_list) != 2:
			# If there is no records
			if len(soup.find_all("p", {"class" : "no-records"})) > 0:
				# Nothing has been found
				return False
			# Add the next parser then
			GenericParserPort.add_next_parser(DigikeyProduct({
				'data': {'string': data}
			}))
			# This must be a page parser then, ignore
			return False

		# Get the page count
		for match in match_list:
			m = re.match(r"\s*Page\s*([0-9]+)\s*/\s*([0-9]+)\s*", match.get_text(), flags=re.IGNORECASE|re.DOTALL)
			if not m:
				raise error("Cannot identify the page number.")
			self.current = int(m.group(1)) - 1
			self.total = int(m.group(2))

		super(DigikeyParser, self).load(data, options)

class Digikey(DigikeyCommon):

	specific_options_list = [
		{'display': 'Search', 'id': 'search', 'paging': True},
	]

	def get_options(self, options):
		return {
			'data': {
				'parser': DigikeyParser,
				'encoding': 'utf-8',
				'timeout': 60,
				'css_selector': "table#productTable",
				'ignore_rows': [1],
				'column_type': {
					3: {"type": "url"}
				}
			},
			'ignore_categories': [r".*digi-key.*part.*number.*", r"^\s*manufacturer\s*$"],
			'ignore_categories_obj': [CategoryPricing],
			'map_categories': [
				[1, CategoryDatasheet],
				[r".*digi-key.*part.*number.*", CategoryOrderPage]
			]
		}

	def update_options(self, page_number, options):
		return {'data': {'url': "http://www.digikey.com/product-search/en/integrated-circuits-ics/embedded-microcontrollers/?x=0&y=0&lang=en&site=us&pageSize=25&k=" + urllib.quote_plus(options["device"]) + "&page=" + str(page_number + 1)}}

	def setup_specific_parser_rules(self, parser):
		def post_discovery_hook(parser, options):
			"""
			Hook used to discover the prices
			"""
			# Loop through the devices discovered
			for d in parser.get_devices():
				# If the device has this category
				c = d.get_device_category("CategoryOrderPage", strict = False)
				if c != None:
					url = c.get_value()
					GenericParserPort.add_next_parser(DigikeyProduct({
						'data': {'url': url},
						'device': d.get_device_name(strict = True, fullname = False)
					}))

		parser.hook("post_discovery", post_discovery_hook)

class DigikeyProductParser(HTMLTableParser):
	"""
	This parser adds the pricing parser
	"""
	def load(self, data, options = {}):

		# Add the pricing parser
		GenericParserPort.add_next_parser(DigikeyProductPrice({
			'data': {'string': data},
			'device': options['device']
		}))

		super(DigikeyProductParser, self).load(data, options)

class DigikeyProduct(DigikeyCommon):

	specific_options_list = [
		{'display': 'Product', 'id': 'product'},
	]

	def get_options(self, options):
		return {
			'data': {
				'parser': DigikeyProductParser,
				'encoding': 'utf-8',
				'timeout': 60,
				'css_selector': "td.attributes-table-main > table",
				'table_type': "vertical",
				'column_type': {
					0: {"type": "url", "match": [r"(?!.*(errata|support|spec|short))(?=.*datasheet).*", r"(?!.*(errata|support|spec|short))(?=.*family).*", r"(?!.*(errata|support|spec|short)).*"]}
				}
			},
			'ignore_categories': [".*pcn.*packaging.*", r".*family.*", r".*standard.*package.*"],
			'ignore_categories_obj': [CategoryDeviceName, CategoryDeviceFamily, CategoryDeviceTopFamily, CategoryPricing],
			'custom': {'CategoryDeviceName': options["device"]}
		}

class DigikeyProductPrice(DigikeyCommon):

	specific_options_list = [
		{'display': 'Price', 'id': 'price'}
	]

	def get_options(self, options):
		return {
			'data': {
				'parser': HTMLTableParser,
				'encoding': 'utf-8',
				'timeout': 60,
				'css_selector': "table#pricing"
			},
			'ignore_categories': [r".*extended.*price.*"],
			'ignore_categories_obj': [CategoryDeviceName, CategoryDeviceFamily, CategoryDeviceTopFamily, CategoryPricing],
			'custom': {'CategoryDeviceName': options["device"]}
		}

	def setup_specific_parser_rules(self, parser):
		"""
		Rules that applies specificly to DigiKey
		"""
		def pre_discovery_hook(parser, options):
			"""
			Hook used to discover the prices
			"""
			# Save the values
			elements = object_clone(parser.elements)
			# Clear the parser
			parser.reset()
			parser.element_create()
			# Discover the prices
			for element in elements:
				volume = element[0].replace(",", "")
				price = element[1]
				if is_number(volume) and is_number(price):
					parser.element_add_value(volume + " @ US$" + price, CategoryPricingDigiKey)

		parser.hook("pre_discovery", pre_discovery_hook)
