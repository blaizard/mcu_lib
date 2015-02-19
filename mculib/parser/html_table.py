#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from generic import *
from mculib.helper import *
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint

from bs4 import BeautifulSoup

class HTMLTableParser(GenericParser):
	options = {}

	# Default category row
	category_row = 0

	def select_table(self, soup):
		if not self.options.has_key("css_selector"):
			raise error("A table CSS selector `css_selector' must be set.", self)
		table_list = soup.select(self.options["css_selector"])
		if len(table_list) > 1:
			raise error("More than one table has been identified, please review the matching parameters.", self)
		if len(table_list) == 0:
			raise error("No table has been identified, please review the matching parameters.", self)
		table = table_list[0]
		# Make sure this element is a table
		if table.name != "table":
			raise error("The element identified is not a table.", self)

		return table

	def parse_horizontal_table(self, table):

		# Count the rows
		row_list = table.find_all("tr")
		self.info("Table identified, %i row(s)" % (len(row_list)), 2)

		# List all the rows
		for row_index, row in enumerate(row_list):
			# Create the device
			if not self.parse_table_device(row_index):
				continue
			# Manually count
			cell_index = 0
			# List all the cells from this row
			for cell in row.find_all(re.compile("^(td|th)$")):
				# Fill in the categories
				cell_index = self.parse_table_cell(row_index, cell_index, cell)

	def parse_vertical_table(self, table):

		# Count the number of rows
		row_list = table.find_all("tr")
		max_rows = 0
		for row in row_list:
			max_rows = max(max_rows, len(row.find_all(re.compile("^(td|th)$"))))
		self.info("Table identified, %i row(s)" % (max_rows), 2)

		# List all the rows
		for row_index in range(max_rows):

			# Create the device
			if not self.parse_table_device(row_index):
				continue
			# Count
			cell_index = 0

			# Identify the categories for this row
			for row in row_list:
				cell_list = row.find_all(re.compile("^(td|th)$"))
				# Isolate the x cell
				cell = cell_list[row_index]
				# Fill in the categories
				cell_index = self.parse_table_cell(row_index, cell_index, cell)


	def parse_table_device(self, row_index):
		# Ignore this row if needed
		if self.options.has_key("ignore_rows") and row_index in self.options["ignore_rows"]:
			return False
		# Create a new element
		self.element_create()
		return True

	def parse_table_cell(self, row_index, cell_index, cell):
		# Check the column type, by default, it looks for text
		parser_options = {
			"type": "text"
		}
		if row_index != self.options["category_row"] and self.options.has_key("column_type") and self.options["column_type"].has_key(cell_index):
			parser_options = self.options["column_type"][cell_index]

		cell_value = ""

		# If the value is a text
		if parser_options["type"] == "text":
			cell_value = str(cell.get_text("\n", strip = True).encode('ascii', 'ignore'))

		# If the value is empty, look if there is an URL
		if cell_value == "" or parser_options["type"] == "url":
			url_list = []
			# If there is a special match requirement
			if parser_options.has_key("match"):
				match_list = parser_options["match"]
				if not isinstance(match_list, list):
					match_list = [match_list]
				for match in match_list:
					for anchor in cell.findAll('a', href = True):
						if re.match(match, anchor.get_text(), re.IGNORECASE):
							url_list.append(anchor['href'])
					# If nothing has been found, go for the next match item
					if len(url_list) > 0:
						break
			# Get the URL out of the content
			if len(url_list) == 0:
				url_list = re.findall('(?:http[s]?|ftp)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', cell.renderContents())
			# If there is no URL found, look for anchors
			if len(url_list) == 0:
				for anchor in cell.findAll('a', href = True):
					url_list.append(anchor['href'])
			# Extract the URL
			if len(url_list) > 0:
				cell_value = url_list[0]

		# Repeat if a colspan is found
		repeat = 1
		if cell.has_attr("colspan"):
			repeat = int(cell["colspan"])

		# Add the values, normal case, repeat = 1, but sometimes, after a colspan for example it can be more.
		for i in range(0, repeat):
			# Check if the current row is a category row
			if row_index == self.options["category_row"]:
				self.category_add(cell_value)
			else:
				self.element_add_value(cell_value)
			self.info("[%i, %i] (category=%s) %s" % (row_index, cell_index, str(row_index == self.category_row), cell_value), 3)
			cell_index = cell_index + 1

		return cell_index

	def parse_table(self, soup):
		# Identify the table
		table = self.select_table(soup)
		# Parse the table
		if self.options.has_key("table_type") and self.options["table_type"] == "vertical":
			self.parse_vertical_table(table)
		else:
			self.parse_horizontal_table(table)

	def load(self, data, options = {}):
		if options.has_key('data'):
			self.options = options['data']
		# Set up the category rows argument
		if not self.options.has_key("category_row"):
			self.options["category_row"] = 0
		soup = BeautifulSoup(data)
		self.parse_table(soup)
