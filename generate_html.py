#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import os.path
import shutil
import sys
import datetime
import json

from mculib import *
from mculib.categories import *
from mculib.database import Database
from mculib.parser.html_table import *

output_dir = "output"

# Wrapper template helper function
def create_page_from_template(env, template, data, filename):
	"""
	Fill a page template
	"""

	def get_file_size(path):
		unit = "B"
		size = os.path.getsize(path)
		if size > 1024 * 1024:
			size = size / (1024 * 1024)
			unit = "MB"
		elif size > 1024:
			size = size / 1024
			unit = "KB"
		return "%.0f%s" % (size, str(unit))

	# Load the template
	template_file_path = os.path.join(env.get_template_path(), template)
	f = open(template_file_path, "r")
	template = f.read()
	f.close()
	# Fill the template
	for key, value in data.items():
		template = template.replace(key, value)
	# Save the new page
	page_out = os.path.join(output_dir, filename)
	f = open(page_out, "wb")
	f.write(template)
	f.close

	Log.info("Generated `%s' (%s)" % (str(page_out), str(get_file_size(page_out))), 1)

def get_and_format_category(db, category, mcu):
	"""
	This function will get a category from the parametric categories list and
	format it
	"""

	param_type = category['class'].to_param()
	# Read the parameter list for this MCU
	param = db.get_parameter(mcu, param_type)
	if param != None and db.get_param_value(param):
		timestamp = db.get_param_date(param)
		if isinstance(timestamp, float):
			date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
		else:
			date = ""
		return [
			db.get_param_value(param),
			db.get_param_trustability(param),
			db.get_param_source(param),
			date,
			db.get_param_comment(param),
		]
	return None

if __name__ == "__main__":

	env = Env(enable_write_db = False)

	# Load the database
	db = Database(env.get_database_path())

	# Read the parametric categories
	parametric_categories = get_parametric_categories()

	# Generate the MCU table
	mcu_db = {}
	for mcu in db.get_mcu_list():

		mcu_entry = {}

		# List all the category that need to be displayed
		for category in parametric_categories:
			value = get_and_format_category(db, category, mcu)
			if value != None:
				mcu_entry[category['id']] = value

		# Add the new MCU
		mcu_db[db.get_name(mcu)] = mcu_entry

	# Build the category list
	category_list = [
		{'param': 'name', 'name': 'Device', 'category': "ID", 'is_list': False, 'is_multi': False}
	]
	for category in parametric_categories:
		if not category.has_key('display'):
			continue
		new_category = {
			'param': category['id'],
			'name': category['display'],
			'is_list': category_is_list(category['class']),
			'is_multi': category_is_multi(category['class']),
			'is_group': category_is_group(category['class']),
			'type': category['class'].get_type()
		}
		if category.has_key("units"):
			new_category['units'] = category['units']
		if category.has_key("category"):
			new_category['category'] = category['category']
		if category.has_key("compare"):
			new_category['compare'] = category['compare']
		if category.has_key("common"):
			new_category['common'] = category['common']
		if category.has_key("hide"):
			new_category['hide'] = category['hide']
		if category_is_multi(category['class']):
			new_category['nb_fields'] = category['class'].config_nb_values
		category_list.append(new_category)

	# Create the output directory if it does not exists
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	output_dir = os.path.join(output_dir, "website")
	if os.path.exists(output_dir):
		shutil.rmtree(output_dir, True)
	# Copy the content of the website template to the output directory
	website_template = os.path.join(env.get_template_path(), "website")
	shutil.copytree(website_template, output_dir)

	Log.info("Generating micro-site: `%s'" % (str(output_dir)), 1)

	# Cut the MCU list into parts
	manufacturer_list = {}
	for device_name in mcu_db:
		mcu = mcu_db[device_name]
		# Filter the MCUs
		# Keep only the non-hidden MCUs
		if (mcu.has_key('hidden') and mcu['hidden'][0] == "yes"):
			continue

		if mcu.has_key("manufacturer") and mcu["manufacturer"]:
			manufacturer = mcu["manufacturer"][0]
		else:
			manufacturer = "uncategorized"

		# Check if this MCU needs to be placed in the legacy list
		if (mcu.has_key('status') and mcu['status'][0] == "mature") or db.get_item_param_value(device_name, "CategoryLegacy", include_aliases = False) == "yes":
			manufacturer += "_legacy"
		if not manufacturer_list.has_key(manufacturer):
			manufacturer_list[manufacturer] = {}
		manufacturer_list[manufacturer][device_name] = mcu

	# Generate the changes log
	log = DatabaseLog()
	log.read()
	create_page_from_template(env, "changes_template.js", {"%CHANGES%": json.dumps(log.get_element_list())}, "changes.js")

	# Generate MCU data
	for manufacturer in manufacturer_list:
		mcu_db = manufacturer_list[manufacturer]
		file_name = "data_" + manufacturer + ".js"
		data = {
			"%CATEGORY%": manufacturer,
			"%CATEGORY_DATA%": json.dumps(category_list),
			"%MCU_DATA%": json.dumps(mcu_db),
		}
		create_page_from_template(env, "data_template.js", data, file_name)

	# Generate the pack list
	pack_list = [x for x in manufacturer_list]
	pack_list.sort()
	data = {
		"%PACK_LIST%": json.dumps(pack_list)
	}
	create_page_from_template(env, "availability_template.js", data, "availability.js")

	# Close the environment
	env.close()
