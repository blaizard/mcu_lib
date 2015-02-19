#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import logging
import sys
import warnings
import inspect

# Constants
LOG_DEFAULT_LEVEL_ERROR = 0
LOG_DEFAULT_LEVEL_INFO = 3
LOG_DEFAULT_LEVEL_WARNING = 2
LOG_DEFAULT_LEVEL_WORKAROUND = 3
LOG_DEFAULT_LEVEL_DEBUG = 1
LOG_DEFAULT_VERBOSE_LEVEL = 1

LOG_TYPE_DEFAULT = 0
LOG_TYPE_COLOR = 2      # Add colors to the output

class error(Exception):
	def __init__(self, message, object = None):
		self.message = message
		Log.error(message, LOG_DEFAULT_LEVEL_ERROR, object)

class Log(object):
	verbose_level = LOG_DEFAULT_VERBOSE_LEVEL
	log_type = LOG_TYPE_DEFAULT
	hook_fct = None
	hook_args = None
	progress = []

	def __init__(self, level = LOG_DEFAULT_VERBOSE_LEVEL):
		logger = logging.getLogger('log')
		ch = logging.StreamHandler()
		Log.log_internal_set_handler(ch)
		logger.setLevel(logging.DEBUG)
		logger.addHandler(ch)
		Log.log_set_verbosity(level)
		Log.log_set_hook(None, None)
		# Reset the progress
		setattr(Log, "progress", [])

	@staticmethod
	def log_get_progress_index(identifier = "default"):
		# if there is an identifier look for it
		progress = getattr(Log, "progress")
		# Check if it exists
		for i, p in enumerate(progress):
			if p.has_key("id") and p["id"] == identifier:
				return i
		# If it does not exists, create it
		progress.append({"value": -1,"top": 0,"inc":1,"id":identifier})
		setattr(Log, "progress", progress)
		return len(progress) - 1

	@staticmethod
	def log_setup_progress(top, increment = 1, identifier = "default"):
		index = Log.log_get_progress_index(identifier)
		progress = getattr(Log, "progress")
		progress[index]["top"] = top
		progress[index]["inc"] = increment
		progress[index]["value"] = -increment
		setattr(Log, "progress", progress)

	@staticmethod
	def log_progress(identifier = "default"):
		index = Log.log_get_progress_index(identifier)
		progress = getattr(Log, "progress")
		progress[index]["value"] = min(progress[index]["value"] + progress[index]["inc"], progress[index]["top"])
		# If there are other progress below this level, remove them
		for p in progress[index+1:]:
			progress.pop()
		setattr(Log, "progress", progress)

	@staticmethod
	def log_identify_category(object):
		return object.__class__.__name__

	@staticmethod
	def log_internal_set_handler(handler):
		handler.setLevel(logging.DEBUG)
		formatter = logging.Formatter("[%(progress)s] [%(asctime)-15s] [%(levelname)s %(level)s] [%(subtype)s] - %(message)s")
		handler.setFormatter(formatter)

	@staticmethod
	def log_set_verbosity(level):
		setattr(Log, "verbose_level", int(level))

	@staticmethod
	def log_get_verbosity():
		return getattr(Log, "verbose_level")

	@staticmethod
	def log_set_file(filename):
		logger = logging.getLogger('log')
		fh = logging.FileHandler(filename)
		Log.log_internal_set_handler(fh)
		logger.addHandler(fh)

	@staticmethod
	def log_set_hook(fct, args = None):
		setattr(Log, "hook_fct", [fct]) # Trick to avoid a cast
		setattr(Log, "hook_args", args)

	@staticmethod
	def log_print(print_type, object = None, message = "", level = 1):
		if not isinstance(level, int):
			raise error("Level is not an integer")
		if level <= Log.verbose_level:

			if print_type == "info":
				fct = logging.getLogger('log').info
				color_wrap = "%s"
			elif print_type == "error":
				fct = logging.getLogger('log').error
				color_wrap = "\33[1;31m%s\33[m"
			elif print_type == "warning":
				fct = logging.getLogger('log').warn
				color_wrap = "\33[0;31m%s\33[m"
			elif print_type == "debug":
				fct = logging.getLogger('log').debug
				color_wrap = "\33[0;32m%s\33[m"
			elif print_type == "workaround":
				fct = logging.getLogger('log').info
				color_wrap = "\33[0;36m%s\33[m"
			elif print_type == "custom":
				fct = logging.getLogger('log').info
				color_wrap = "%s"
			else:
				raise error("Unknown print type: `%s'." % (str(print_type)))

			hook_fct = getattr(Log, "hook_fct")
			if hook_fct and hook_fct[0]:
				message = hook_fct[0](str(message), Log.hook_args)
			message = color_wrap % (str(message))

			# Set the progress
			progress = getattr(Log, "progress")
			progress_str = "-"

			if len(progress) > 0 and progress[0]["top"] > 0:
				value = max(0, progress[0]["value"])
				top = progress[0]["inc"]

				for p in progress[1:]:
					if p["top"] != 0:
						value = value + (max(0, p["value"]) * 1. / p["top"]) * top
						top = p["inc"] / p["top"]

				value = (value * 1. / progress[0]["top"]) * 100

				if value < 0.001:
					progress_str = "0%"
				elif value < 0.01:
					progress_str = ".00%u%%" % (int(value * 1000))
				elif value < 0.1:
					progress_str = ".0%u%%" % (int(value * 100))
				elif value < 1:
					progress_str = ".%u%%" % (int(value * 10))
				else:
					progress_str = "%u%%" % (int(value))

			fct(message, extra={"progress": progress_str, "level": level, "subtype": Log.log_identify_category(object)})

	@staticmethod
	def error(message, level = LOG_DEFAULT_LEVEL_ERROR, object = None):
		Log.log_print("error", object, message, level)

	@staticmethod
	def info(message, level = LOG_DEFAULT_LEVEL_INFO, object = None):
		Log.log_print("info", object, message, level)

	@staticmethod
	def warning(message, level = LOG_DEFAULT_LEVEL_WARNING, object = None):
		Log.log_print("warning", object, message, level)

	@staticmethod
	def workaround(message, level = LOG_DEFAULT_LEVEL_WORKAROUND, object = None):
		Log.log_print("workaround", object, "[WORKAROUND] %s" % (str(message)), level)

	@staticmethod
	def debug(message, level = LOG_DEFAULT_LEVEL_DEBUG, object = None):
		Log.log_print("debug", object, message, level)

