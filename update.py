#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import os.path
import shutil
import sys
import shlex

from optparse import OptionParser, OptionGroup

from mculib import *
from mculib.database import *
from mculib.parser import *
from mculib.categories import *

global_db = None

class StringPort(GenericParserPort):

	def get_options(self, options):
		return {
			'data': {'parser': StringParser, 'string': "", 'category': None},
			'id': 'string',
			'display': 'String Parser',
		}

	specific_options_list = []

	def __init__(self, options = {}):
		self.specific_options_list = []
		super(StringPort, self).__init__()

	def add_device(self, device_name, c, string, display):
		self.specific_options_list.append({
			'custom': {
				'CategoryDeviceName': device_name
			},
			'data': [{'display': display, 'class': c, 'string': string}]
		})

class CSVPort(GenericParserPort):

	def get_options(self, options):
		return {
			'data': {'parser': CSVParser, 'encoding': 'iso-8859-1'},
			'id': 'csv',
			'display': 'CSV Parser',
		}

	specific_options_list = []

	def __init__(self):
		self.specific_options_list = []
		super(CSVPort, self).__init__()

	def add_file(self, file_path):
		self.specific_options_list.append({
			'data': [{'file': file_path}]
		})

def format_value_and_highlight(value, is_list, list_index, field_index):
	color_wrap = "\33[0;31m%s\33[m"
	if isinstance(value, list):
		if is_list and list_index < len(value):
			if isinstance(value[list_index], list) and field_index:
				if field_index < len(value[list_index]):
					value[list_index][field_index] = color_wrap % (str(value[list_index][field_index]))
			else:
				value[list_index] = color_wrap % (str(value[list_index]))
	else:
		value = color_wrap % (str(value))
	return str(value).decode('string_escape')

def get_param_id(value, t = "class"):
	"""
	This function retrieve the parameter ID and translate it to a category class.
	"""
	# Check if it is part of the list
	if len([x for x in get_parametric_categories() if x["id"] == value]) == 0:
		# If the value is not a valid parametric ID,
		# then parse it to look for a match into the categories
		return value
	# Convert it to a category class
	category = get_parametric_categories(value)
	return category[t]

def validate_arg_number(args, min_arg, max_arg = None):
	"""
	This function will return an error if the number of argument is too low or too high
	"""
	if len(args) < min_arg:
		raise error("Not enough arguments, please double check the command help for `%s'." % (args[0]))
	if max_arg and len(args) > max_arg:
		raise error("Too many arguments, please double check the command help for `%s'." % (args[0]))

def deal_with_options(env, args_parser, args = sys.argv[1:]):

	Log.info("Parsing command line: `%s'" % (" ".join(args)), 2)

	# Parse the options
	(options, args) = args_parser.parse_args(args = args)

	# If from filename
	if options.file_name:
		data = read_file(options.file_name)
		action_list = data.split("\n")
		# Set the progress top value
		Log.log_setup_progress(len(action_list), identifier = "file_action_list")
		for line in action_list:
			# Increase the progress
			Log.log_progress(identifier = "file_action_list")
			deal_with_options(env, args_parser, shlex.split(line))
		return

	# Hanlde types
	if len(args):
		if args[0] == "string":
			# Check the arguments
			validate_arg_number(args, 4)
			category_id = args[1]
			category_class = get_param_id(category_id)
			category_display = get_param_id(category_id, "display")
			string = args[2]

			# Loop through the devices
			for device in args[3:]:

				# Attach a secific parser if it can find one
				manufacturer = env.get_db().get_item_param_value(device, "CategoryDeviceManufacturer", include_aliases = True, first_if_multi = True)
				parser_class = StringPort
				for parser_ports in parser_ports_list:
					device_parser = parser_ports['common']
					if device_parser.get_manufacturer() == manufacturer:
						Log.info("Identified specific device parser (%s) for device `%s'." % (device_parser.__name__, str(device)), 2)
						if parser_class != StringPort:
							raise error("More than one parser has been identified for this device.")
						parser_class = type('SpecificStringPort', (device_parser, StringPort), {})

				# Create the parser class
				parser = parser_class()
				parser.add_device(device, category_class, string, category_display)
				# Fetch data
				parser.fetch()
				# Merge the parser with the database
				merge_parser_to_db(parser, env.get_db(), trustability = env.get_trustability(), source = env.get_source(), force = env.get_force(), record = env.get_record(), onlyexisting = env.get_only_existing())

		elif args[0] == "nop":
			pass

		elif args[0] == "clean":
			"""
			Clean-up the database for a specific part
			"""
			validate_arg_number(args, 1)

			# Get the device list
			db = env.get_db()
			device_list = args[1:]

			# If the device list is empty, list all devices
			if len(device_list) == 0:
				mcu_list = db.get_mcu_list()
			# Else generates the mcu list
			else:
				mcu_list = []
				for mcu_name in device_list:
					mcu = db.find_mcu(mcu_name)
					mcu_list.append(mcu)
			# Clean the MCU list
			db.clean_up(mcu_list)

		elif args[0] == "group":
			"""
			This action will group the category of different devices.
			If the category is a group master, it will merge the different groups into one.
			"""
			validate_arg_number(args, 4)

			category_class = get_param_id(args[1])
			param_type = category_class.to_param()
			db = env.get_db()

			# If the category is a group
			if category_class.is_group():

				# Need to get a reference device, where all other groups will be merged to
				reference_device_found = False
				device_list = args[2:]
				for index, reference_device in enumerate(device_list):
					# Find the first device with a valid group
					reference_group_name = db.get_item_param_value(reference_device, param_type)
					if reference_group_name != "":
						reference_device_found = True
						device_list.pop(index)
						break

				# If no group exists, try to create one
				if not reference_device_found:
					reference_device = args[2]
					reference_item = db.find_mcu(reference_device)
					group = db.create_group("", param_type)
					reference_group_name = db.get_name(group)
					if reference_group_name == "":
						raise error("The group name for `%s' cannot be generated, need to abort." % (str(param_type)))

				# Get the reference group item
				reference_group_item = db.find_group(reference_group_name, param_type)

				# List all devices and merge their group into the referenced one
				for device in device_list:
					# Find the device
					item = db.find_mcu(device)
					group_name = db.get_item_param_value(item, param_type)
					# If they have a group, merge it with the reference group
					if group_name != "":
						group_item = db.find_group(group_name, param_type)
					        db.merge_item(reference_group_item, group_item)
					# Add the group to their parameters
					db.set_mcu_parameter(item, param_type, reference_group_name, trustability = env.get_trustability(), source = env.get_source(), force = env.get_force())
			else:

				raise error("Not implemented yet")

		elif args[0] == "merge":
			# Check the arguments
			validate_arg_number(args, 3)
			mcu_name = args[1]
			db = env.get_db()

			# If the destination MCU does not exists, create it
			item_dst = db.find_mcu(mcu_name)
			if item_dst == None:
				item_dst = db.create_mcu(mcu_name)
			# Loop through the device list
			for src_mcu_name in args[2:]:
				item_src = db.find_mcu(src_mcu_name)
				if item_src == None:
					raise error("This item `%s' does not exists." % (str(src_mcu_name)))
				db.merge_item(item_dst, item_src)
			# Delete the items if write is enable
			if env.get_write():
				for src_mcu_name in args[2:]:
					item_src = db.find_mcu(src_mcu_name)
					db.delete_item(item_src)

		elif args[0] == "comment":
			# Check the arguments
			validate_arg_number(args, 4)
			param_type = get_param_id(args[1]).to_param()
			comment = args[2]
			db = env.get_db()

			# Loop through the devices
			for device in args[3:]:
				mcu = db.find_mcu(device)
				if mcu == None:
					raise error("This MCU (%s) cannot be identified." % (mcu_name))
				param = db.get_parameter(mcu, param_type)
				if param == None:
					param = db.create_param(mcu, param_type)
				db.set_param_comment(param, comment)

		elif args[0] == "csv":

			# Check the arguments
			validate_arg_number(args, 2)
			file_path = args[1]

			parser = CSVPort()
			parser.add_file(file_path)
			# Fetch data
			parser.fetch()
			# Merge the parser with the database
			merge_parser_to_db(parser, env.get_db(), trustability = env.get_trustability(), source = env.get_source(), force = env.get_force(), record = env.get_record(), onlyexisting = env.get_only_existing())

		elif args[0] == "convert":

			# Check the arguments
			validate_arg_number(args, 3)
			parameter = args[1]
			action = args[2]
			arg_list = args[3:]

			# Select devices/parameters
			db = env.get_db()
			mcu_list = db.get_mcu_list()

			if action == "value2multi":
				# Go through the MCU list
				for mcu in mcu_list:
					# Get the value of the selected parameter
					param = db.get_parameter(mcu, parameter)
					if param != None:
						# This is the MCU instance
						parent_item = db.get_param_parent(param)

						param.attrib["type"] = "GenericCategory"
						value = db.get_param_value(param)
						param.attrib["type"] = parameter
						param.set('value', str([value, '']))

						# Mark the MCU as changed
						db.set_change_value(parent_item)
						print db.get_param_value(param)
			else:
				raise error("Unknown action type `%s', please check the help." % (action))

		elif args[0] == "select":

			# Check the arguments
			validate_arg_number(args, 3)
			device_selector = args[1]
			action = args[2]
			arg_list = args[3:]

			# Select devices/parameters
			db = env.get_db()
			selector = DatabaseSelector(device_selector)
			selector.select(db)
			match_list = selector.get_match_list()

			# Process the action
			if action == "print":
				"""
				Print the selection
				"""
				for mcu_name in match_list:
					item = match_list[mcu_name]
					string = "Selected %s" % (mcu_name)
					for match in item['match']:
						value = db.get_param_value(match['param'])
						display_value = format_value_and_highlight(value, db.is_param_list(match['param']), match['list_index'], match['field_index'])
						string += " - %s::%s from `%s'" % (db.get_param_type(match['param']), match['value'], display_value)
					Log.info(string, 0)
				Log.info("%i device(s) selected." % (len(match_list)), 0)

			elif action == "copy":
				"""
				Copy a parameter to another
				"""
				for mcu_name in match_list:
					item = match_list[mcu_name]
					for match in item['match']:
						pass

			elif action == "remove":
				"""
				Remove the parameter specified in the argument for the matching MCUs
				"""
				for mcu_name in match_list:
					item = match_list[mcu_name]
					mcu = item['mcu']
					if len(item['match']):
						# Selec tthe last item only
					        match = item['match'][len(item['match']) - 1]
						param = match['param']
						if param != None:
							db.delete_param(param)

			else:
				raise error("Unknown action type `%s', please check the help." % (action))

		else:
			raise error("Unknown command type `%s', please double check the command help." % (args[0]))

	else:
		# Check if there is data from stdin
		while True:
			line = sys.stdin.readline()
			if not line:
				break
			deal_with_options(env, args_parser, shlex.split(line))
		return

if __name__ == "__main__":

	args_parser = OptionParser(usage="""[options] <type> <arg1> [<arg2> ...]
   CSV parser: [options] csv <file_path>
String parser: [options] string <param_id> <string> <device1> [<device2> ...]
      Comment: [options] comment <param_id> <comment> <device1> [<device2> ...]
   Parameters: [options] select <device_selector> <action> [<arg1> ...]
        Merge: [options] merge <destination> <source1> [<source2> ...]
        Merge: [options] group <param_id> <device1> [<device2> ...]
     Clean-up: [options] clean <device1> [<device2> ...]
 No Operation: [options] nop

- <device_selector>: [!][<param_name>][:<multi_value_index (a number)>][=<regexpr>][;<device_selector>]
- <param_id>:  A category parameter ID, it can be one of these values: (%s)
- <param_name>: A category parameter name, it can be one of these values: (%s)
""" % (";".join([x['id'] for x in get_parametric_categories()]), ";".join([x.to_param() for x in get_category_list()])))

	args_parser.add_option("-i", "--input", default=None, dest="file_name", help="The path of a file containing instructions to update the database. Instructions are a list of command line using the same format as the one handle by this tool.")

	env = Env(args_parser = args_parser, enable_write_db = True)

	# Deal with the options
	deal_with_options(env, args_parser)

	# Close the environment
	env.close()
