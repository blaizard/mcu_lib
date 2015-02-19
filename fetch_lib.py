#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import os.path
import shutil
import sys
import re
import json

from optparse import OptionParser, OptionGroup

from mculib import *
from mculib.database import Database
from mculib.parser import *

def fetch_manufacturer(env, manufacturer_str, class_list, id_list = None):
	"""
	This function will fetch normal parser
	"""
	global_options = {
		'data': {
			'proxy': env.get_proxy(),
		},
		'custom': {
			'CategoryDeviceManufacturer': manufacturer_str,
			# By default Devices discovered automatically are not legacy unless specified
			'CategoryDiscovered': "automatic",
			'CategoryLegacy': "false"
		}
	}
	parserFetchMerge(env, class_list, id_list, global_options)

def fetch_device(env, class_list, id_list = None):
	"""
	This function will fetch device parsers,
	these are called with a device argument name and is used to fetch more specific info
	for a particular device.
	"""
	db = env.get_db()

	# Select all visible devices
	mcu_list = DatabaseSelector(db).select("!CategoryHidden=yes;!CategoryDeviceStatus=mature;!CategoryLegacy=yes").get() #CategoryDeviceManufacturer=nxp;

	# Set the progress top value
	Log.log_setup_progress(len(mcu_list), identifier = "fetch_device")

	# Loop through
	for mcu in mcu_list:
		# Increase the progress
		Log.log_progress(identifier = "fetch_device")

		mcu_name = db.get_name(mcu)
		# build the exclude list, to make sure other MCUs with similar names are not included
		others = db.find_mcu_match(mcu_name)
		# Look for other MCUs which would also match, these should be excluded from the match
		device_exclude = [db.get_name(m) for m in others if db.get_name(m) != mcu_name]
		# Read the name of this device
		global_options = {
			'data': {
				'proxy': env.get_proxy(),
			},
			'device': mcu_name,
			'device_exclude': device_exclude,
			'custom': {
				'CategoryAlias': mcu_name,
				'CategoryDiscovered': "automatic"
			}
		}
		parserFetchMerge(env, class_list, id_list, global_options)

	#	break

if __name__ == "__main__":

	# Generate the help string
	help_str = ""
	for platform in parser_ports_list + device_parser_ports_list:
		help_str += "\n" + platform["common"].get_manufacturer() + ":\n\t"
		x = []
		for c in platform["specific"]:
			x.extend(c.get_ids())
		help_str += ', '.join(x)

	args_parser = OptionParser(usage="""[options] platform [id1 ...]
Automatic data-mining from supported platforms. Supported platforms/ids are: %s""" % (help_str))

	env = Env(args_parser = args_parser, enable_write_db = True)

	(options, args) = args_parser.parse_args()

	if len(args) < 1:
		raise error("There must be at least 1 argument.")

	# Read the platform name passed into argument
	platform_name = args[0]

	# Read the IDs if any
	id_list = None
	if len(args) > 1:
		id_list = args[1:]

	# Fetch the manufacturer website
	if platform_name in [x["common"].get_manufacturer() for x in parser_ports_list]:
		for x in parser_ports_list:
			if x["common"].get_manufacturer() == platform_name:
				fetch_manufacturer(env, platform_name, x["specific"], id_list = id_list)
	# Fetch the device specific website
	elif platform_name in [x["common"].get_manufacturer() for x in device_parser_ports_list]:
		for x in device_parser_ports_list:
			if x["common"].get_manufacturer() == platform_name:
				fetch_device(env, x["specific"], id_list = id_list)
	else:
		raise error("Platform unknown (%s)." % (str(platform_name)))

	# Close the environment
	env.close()
