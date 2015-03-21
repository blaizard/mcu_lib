#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import os.path
from mculib.log import *
from optparse import OptionParser, OptionGroup

class MCULibClass(object):
	def error(self, message, level = LOG_DEFAULT_LEVEL_ERROR):
		Log.error(message, level, self)
	def info(self, message, level = LOG_DEFAULT_LEVEL_INFO):
		Log.info(message, level, self)
	def warning(self, message, level = LOG_DEFAULT_LEVEL_WARNING):
		Log.warning(message, level, self)
	def workaround(self, message, level = LOG_DEFAULT_LEVEL_WORKAROUND):
		Log.workaround(message, level, self)
	def debug(self, message, level = LOG_DEFAULT_LEVEL_DEBUG):
		Log.debug(message, level, self)

from mculib.database import *

class Env(MCULibClass):
	database_path = "database"
	template_path = "resources/templates"
#	proxy = {'http': 'http://squid.norway.atmel.com:3128', 'https': 'http://squid.norway.atmel.com:3128'}
	proxy = {}
	source = None
	trustability = TRUSTABILITY_AUTO
	force = False
	write = False
	only_print = False
	db = None
	db_prev_sub_dir = None
	selector = None
	unsafe = False
	analyze = False
	cleanup = False
	record = True
	onlyexisting = False

	def __init__(self, args_parser = None, enable_write_db = False):
		# Initialize logging system
		Log()
		# Deal with common arguments
		self.parse_args(args_parser, enable_write_db)
		self.info("Environment initialized.", 1)

	def close(self):
		"""
		Close the environment and perform specific actions
		"""
		# Clean-up the database
		if self.cleanup:
			self.get_db().clean_up(self.get_db().get_mcu_list())
		# Analyze the log
		if self.analyze:
			analyze_log = DatabaseAnalyze()
			analyze_log.read()
			analyze_log.analyze(self.get_db())
			if self.get_write():
				analyze_log.write()
		# Write all MCUs that have been updated
		if self.get_write():
			self.get_db().write_all()
		# End message
		self.info("Environment closed.", 1)

	def get_db(self, sub_dir = ""):
		if self.db == None or self.db_prev_sub_dir != sub_dir:
			db_path = self.get_database_path(sub_dir)
			# Make sure the directory exists, if not create it
			if not os.path.exists(db_path):
				self.info("Creating new directory `%s'" % (str(db_path)))
				os.makedirs(db_path)
			self.db = Database(db_path, record = self.record)
			# Validate database
			if not self.unsafe:
				self.db.sanity_check()
			self.db_prev_sub_dir = sub_dir
		return self.db

	def parse_args(self, args_parser = None, enable_write_db = False):

		# Create the argument parser if not exists
		if args_parser == None:
			args_parser = OptionParser(usage="""[options]""")

		# Common options
		if enable_write_db:
			args_parser.add_option("-s", "--source", default=None, dest="source", help="The source of this paramter value (default=`%s')." % (str(self.source)))
			args_parser.add_option("-t", "--trust", default=None, dest="trust", help="Set the trustability of the value set (default=`%s')." % (str(self.trustability)))
			args_parser.add_option("-f", "--force", action="store_true", default=False, dest="force", help="Set this value if you want the value to be set even if the trustability index is lower  (default=`%s')." % (str(self.force)))
			args_parser.add_option("-w", "--write", action="store_true", dest="write", default=False, help="Write the data to the database (default=`%s')." % (str(self.trustability)))
		args_parser.add_option("-x", "--selector", default=None, dest="selector", help="Select devices and/or categories using regular expressions.")
		args_parser.add_option("-p", "--print", action="store_true", default=False, dest="only_print", help="Only print the output, do not write anything to the database.")
		args_parser.add_option("-v", "--verbose", default=None, dest="verbosity_level", help="A value from 0 to 3, defining the level of verbosity. 0 == no verbosity, 3 maximal verbosity (default=`%s')." % (str(Log.log_get_verbosity())))
		args_parser.add_option("-l", "--log", dest="log", default=None, help="Write the logging output to a file.")
		args_parser.add_option("-u", "--unsafe", dest="unsafe", action="store_true", default=False, help="Do not run the sanity check on the whole database, this options should be used only to fix the database.")
		args_parser.add_option("-a", "--analyze", dest="analyze", action="store_true", default=False, help="This option activates the database log analyzis. If the write option is enabled, it will write back the data to a file.")
		args_parser.add_option("-c", "--cleanup", dest="cleanup", action="store_true", default=False, help="Clean-up the database, the information will be stored only if the --write option is also specified.")
		args_parser.add_option("-r", "--norecord", dest="norecord", action="store_true", default=False, help="Do not store records of the data fetched.")
		args_parser.add_option("-o", "--onlyexisting", dest="onlyexisting", action="store_true", default=False, help="Update only exisitng devices, ignore new entries.")

		# Parse the options
		(options, args) = args_parser.parse_args(args = sys.argv[1:])

		# Deal first with the logging system
		if options.verbosity_level:
			Log.log_set_verbosity(options.verbosity_level)
		if options.log:
			Log.log_set_file(options.log)

		# Set environment options
		if enable_write_db:
			if options.source:
				self.source = options.source
			if options.trust:
				self.trustability = options.trust
			if options.force:
				self.force = True
			if options.write:
				self.write = True

		if options.unsafe:
			self.unsafe = True

		if options.analyze:
			self.analyze = True

		if options.cleanup:
			self.cleanup = True

		if options.norecord:
			self.record = False

		if options.onlyexisting:
			self.onlyexisting = True

		if options.selector:
			db = self.get_db()
			self.selector = DatabaseSelector(options.selector)
			self.selector.select(db)
			if options.only_print:
				self.selector.print_selection(db)

		if options.only_print:
			self.only_print = options.only_print

	# Get environment parameters
	def get_source(self):
		return self.source
	def get_trustability(self):
		return self.trustability
	def get_force(self):
		return self.force
	def get_record(self):
		return self.record
	def get_only_existing(self):
		return self.onlyexisting
	def get_write(self):
		if self.only_print:
			return False
		return self.write

	# Returns directory path
	def get_database_path(self, sub_dir = ""):
		path = os.path.join(self.database_path, sub_dir)
		return path
	def get_template_path(self, sub_dir = ""):
		path = os.path.join(self.template_path, sub_dir)
		return path
	def get_proxy(self):
		return self.proxy

