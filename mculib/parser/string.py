#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from generic import GenericParser
from mculib.helper import *

class StringParser(GenericParser):
	options = {}

	def load(self, data, options = {}):
		"""
		Load
		"""
		if options.has_key('data'):
			self.options = options['data']
		if not self.options.has_key("category"):
			raise error("Missing `category' attribute in the options.")

		index = self.category_add(self.options["display"])
		self.category_set_class(index, self.options["class"])
		self.info("Map `%s' and assing `%s' to category (%i)." % (self.options["class"].to_param(), self.options["display"], index), 2)
		self.element_create()

		self.element_add_value(data)
