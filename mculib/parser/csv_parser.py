#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import re
import csv
from generic import GenericParser
from mculib.helper import *

class CSVParser(GenericParser):
	options = {}

	common_options = {
		'map_categories': [{}]
	}

	def load(self, data, options = {}):
		"""
		Load
		"""
		if options.has_key('data'):
			self.options = options['data']

		# Parse the CSV data
		data = csv.reader(open(self.options['file'], 'r'), delimiter=';', quotechar='"')

		# Assume that the first line is the category line
		category_list = data.next()
		for category_value in category_list:
			self.category_add(category_value)

		for element in data:
			self.element_create()
			first = True
			for element_value in element:
				if first:
					if re.match(r"^SAM", element_value):
						element_value = "at" + element_value
					first = False
				self.element_add_value(element_value)
