#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import datetime

from mculib.database import *
from mculib.parser.generic import *

def merge_parser_to_db(parser, db, trustability = TRUSTABILITY_AUTO, source = None, force = False, record = True, onlyexisting = False, onlyMCUorAlias = True):
	"""
	Merge either a GenericParserPort or a GenericParser to the database
	"""
	# Start to track the changes from now on
	timestamp = db.log().get_timestamp()

	# Go through all the new elements
	for device in parser.get_devices():

		# Retrieve the attributes of the devices
		device_name = device.get_device_name(strict = True, fullname = onlyMCUorAlias)

		# If the instance
		if isinstance(device_name, list):

			# Look for the parent MCU and make sure it exists
			mcu = db.find_mcu(device_name[0])
			if mcu == None:
				# And if the only exsting device option is enabled, ignore this entry
				if onlyexisting:
					continue
				# Otherwise create the MCU
				mcu = db.create_mcu(device_name[0])
			# Select the item to write
			item_list = [mcu]

			# If this is an alias
			if len(device_name) == 2:
				# Look for the alias
				alias = db.find_alias(mcu, device_name[1])
				if alias == None:
					# And if the only exsting device option is enabled, ignore this entry
					if onlyexisting:
						continue
					# Otherwise create the MCU
					alias = db.create_alias(mcu, device_name[1])
				# Select the item to write
				item_list = [alias]

		# in that case it can be alias or mcu or both
		elif isinstance(device_name, str):

			item_list = db.find_item(device_name, allow_multiple = True, include_aliases = True)
			# If no item has been found, it becomes a MCU by default
			if item_list == None:
				# And if the only exsting device option is enabled, ignore this entry
				if onlyexisting:
					continue
				# Otherwise create the MCU
				item_list = [db.create_mcu(device_name)]

		else:
			raise error("This device name type `%s' is not supported." % (str(device_name)))

		# Multiple MCU can be targeted, this happens when an alias and a mcu have the same name
		for item in item_list:
			# Merge the new_device with the mcu
			for category in device.get_device_categories():
				# Ignore some categories that should not be merged
				if category.to_param() in ["CategoryAlias"]:
					continue
				# Update the trustability if needed
				t = trustability
				if trustability == TRUSTABILITY_AUTO and category.config_reduced_trustability:
					t = TRUSTABILITY_AUTO_REDUCED
				# Set the new value
				db.set_item_parameter(item, category.to_param(), category.get_value(), t, source, force)

	# Clear the current device list in the parser, in order to record changes if any
	parser.clear_device_list()

	# Get the list of modified items
	for change in db.log().from_timestamp(timestamp).get_param():
		item_name = db.log().get_item_name_from_element(change)
		#if isinstance(item_name, list):
		#	item_name = item_name[len(item_name) - 1]
		param_name = db.log().get_param_from_element(change)
		value = db.log().get_value_from_element(change)
		previous_value = db.log().get_previous_value_from_element(change)
		parser.hook_proceed("post_param_merge_to_db", parser, db, item_name, param_name, value, previous_value, record)

	# Recursively call this function until there is no new devices to process
	if len(parser.get_devices()):
		merge_parser_to_db(parser, db, trustability, source, force, record, onlyexisting)

def merge_param_to_db_default_hook(parser, db, item_name, param_type, value, previous_value, record):
	"""
	Default hooking function that will be called once a parameter has been
	updated or created.
	"""
	# These actions will be done only if recording is enabled
	if record:
		# Create the current timestamp
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y-%m")

		# Handle specific rules for the device status
		if param_type == "CategoryDeviceStatus":
			# If the status changed from announced to production, setup the device launch date
			if previous_value in ["announced", ""] and value in ["production", "sampling"]:
				parser.add_param(item_name, "CategoryLaunchDate", timestamp)

		# First time the device has been discovered
		elif param_type == "CategoryDeviceName" and previous_value != value:
			# Update the launch date only if there is not a launch date set already
			if db.get_item_param_value(item_name, "CategoryLaunchDate") == "":
				parser.add_param(item_name, "CategoryLaunchDate", timestamp)

