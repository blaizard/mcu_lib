#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

# Implement using this: https://services.digikey.com/
# NEED A PARTNER GUID !!!

from mculib.parser.generic import *
from mculib.parser.deep import *
from mculib.parser.html_table import *

from bs4 import BeautifulSoup

class DigikeyAPICommon(GenericParserPort):
	@staticmethod
	def get_manufacturer():
		return "digikey"

	def setup_specific_parser_rules(self, parser):
		pass

	def setup_parser_rules(self, parser):
		"""
		Rules that applies specificly to DigiKey
		"""
		self.setup_specific_parser_rules(parser)

class DigikeyAPIParser(GenericParser):
	"""
	"""
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
		# If not fond, it means this went directly to the product detail page
		if len(match_list) != 2:
			return
		#	raise error("Found %i page info, there should be 2." % (len(match_list)))
		for match in match_list:
			m = re.match(r"\s*Page\s*([0-9]+)\s*/\s*([0-9]+)\s*", match.get_text(), flags=re.IGNORECASE|re.DOTALL)
			if not m:
				raise error("Cannot identify the page number.")
			self.current = int(m.group(1)) - 1
			self.total = int(m.group(2))

class DigikeyAPI(DigikeyAPICommon):

	username = "mcuanalyst"
	password = "abcdefgh"

	def get_options(self, options):
		return {
			'data': {
				'parser': DigikeyAPIParser,
				'encoding': 'utf-8',
				'timeout': 60,
				'headers': {
					'Content-Type': 'application/soap+xml; charset=utf-8'
				},
				'url': 'http://servicestest.digikey.com/search/search.asmx'
			}
		}

	def page_data(self, page_number, options):
		return [ {'post': '<?xml version="1.0" encoding="utf-8"?>' +
		'<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">' +
		'<soap12:Header>' +
		'<Security xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">' +
		'<UsernameToken>' +
		'<Username>' + "mcuanalyst" + '</Username>' +
		'<Password>' + "abcdefgh" + '</Password>' +
		'</UsernameToken>' +
		'</Security>' +
		'<PartnerInformation xmlns="http://services.digikey.com/SearchWS">' +
		'<PartnerID>' + '</PartnerID>' +
		'</PartnerInformation>' +
		'</soap12:Header>' +
		'<soap12:Body>' +
		'<KeywordSearchIncludeAllPricing xmlns="http://services.digikey.com/SearchWS">' +
		'<keywords>' + 'atmega324p' + '</keywords>' +
		'<recordCount>' + str(100) + '</recordCount>' +
		'<recordStartPosition>' + str(0) + '</recordStartPosition>' +
		'<options>All</options>' +
		'</KeywordSearchIncludeAllPricing>' +
		'</soap12:Body>' +
		'</soap12:Envelope>'} ]


	specific_options_list = [
		{'display': 'Search', 'id': 'search', 'paging': True},
	]
