#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import re
import inspect
import copy
import pprint
from mculib.log import *
from types import *

def object_print(x):
	"""
	Print the attribute of the object
	"""
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(x)

def object_clone(x):
	"""
	Create a clone of x
	"""
	return copy.deepcopy(x)

def object_merge(object1, object2):
	"""
	object2 will be merged into object1
	"""
	if isinstance(object1, dict) and isinstance(object2, dict):
		for key in object2.keys():
			value = object2[key]
			if isinstance(value, dict):
				if not object1.has_key(key):
					object1[key] = {}
				object1[key] = object_merge(object1[key], value)
			else:
				object1[key] = value
		return object1
	elif isinstance(object1, list) and isinstance(object2, list):
		for i, value in enumerate(object2):
			object1[i] = object_merge(object1[i], value)
		return object1
	else:
		return object2

def object_to_class(object):
	"""
	It can take either a class, a string or an instance in parameter
	"""
	try:
		if isinstance(object, str):
			return eval(object)
		elif inspect.isclass(object):
			return object
		else:
			return object.__class__
	except:
		raise error("The object (%s) is not identifiale" % (str(object)))

def visualize_xml(element, level=0):
	"""
	Visualize all ElementTree nodes by printing them to screen
	"""

	output = '%s<%s>' % ( '| '*level, element.tag )
	output = output.ljust(30)

	attr = "attributes: "
	for key, value in element.attrib.items():
		attr += "%s=%s, " % (key, value)

	print output, attr[:80]
	for child in element:
		visualize_xml(child, level+1)

def read_file(filename):
	"""
	Opens the specified file and returns its contents, if it
	could be opened. Otherwise, an error message is printed.
	"""
	try:
		f = open(filename, "r")
	except IOError:
		raise IOError("Cannot dump content of file `%s'" % (filename))

	data = f.read()
	f.close()
	return data

def write_file(filename, data):
	"""
	Write data to a file
	"""
	try:
		f = open(filename, "w")
	except IOError:
		raise IOError("Cannot write data into the file `%s'" % (filename))

	data = data.encode("utf-8", "replace")

	f.write(data)
	f.close()

def is_float(string):
	if re.match(r"^\s*[-+]{0,1}[0-9]+[\.,][0-9]*\s*$", str(string)):
		return True
	return False

def is_integer(string):
	if re.match(r"^\s*[-+]{0,1}[0-9]+\s*$", str(string)):
		return True
	return False

def is_number(string):
	if re.match(r"^\s*[-+]{0,1}[0-9]+[\.,]{0,1}[0-9]*\s*$", str(string)):
		return True
	return False

def to_number(string):
	if is_integer(string):
		return int(string)
	if is_float(string):
		return float(string.replace(",", "."))
	return None

"""
Different strategies when merging data together
"""
MERGE_STARTEGY_MASK = 15
MERGE_STRATEGY_REPLACE = 0 # By default replace the original value by the new one
MERGE_STRATEGY_ADD = 1 # Add numbers
MERGE_STRATEGY_MAX = 2 # Keep the maximum number
MERGE_STRATEGY_MIN = 3 # Keep the minimum number
MERGE_STRATEGY_FILL = 4 # Only fill out the blanks. Add items to the list if needed.
MERGE_KEEP_EMPTY = 16 # Keep empty element in the list
MERGE_KEEP_ORDER = 32 # Keep the order when merging 2 lists
MERGE_MULTILINE = 64 # Take into account the newline character as if each line was a separate element
MERGE_CONCATENATE = 128 # Concatenate strings
MERGE_STRING = 256 # Consider the values has string (do not consider numbers)
MERGE_REMOVE_DUPLICATES = 512 # Remove duplicates from the list
MERGE_LIST_NO_ADD = 1024 # Prevent adding new items to a list, if a new item is discovered, ignore it.

"""
Values for yes and no
"""
YES_VALUES = ["yes"]
NO_VALUES = ["no", "-"]
EMPTY_VALUES = [""]

def options_prepare(options = {}):
	default_options = {
		'separator': '/',
		'newline': '\n',
		'conflict': None,
		'list_rules': []
		#	{
				# If the pattern match the following, elements will "None" value not be considered
			#	'pattern': [r"(no|0)"], # or [r"(no|0)", None, None]
				# Fill the elements that have not been evaluated (or the
			#	'fill': '-' # Fill all the elements that have not been evaluated
					# [None, '-', '-'] # Fill all the non-None elements with the value
		#	}
	}
	for key in options:
		default_options[key] = options[key]
	return default_options

def merge_lists(original, new, strategy = MERGE_STRATEGY_REPLACE, options = {}):
	"""
	Merge 2 lists of values together.
	For the definition of what a value is, look at `merge_values'.
	TODO: allow_update, strategy
	"""

	# Make sure the options are up-to-date
	options = options_prepare(options)

	# original must be a LIST
	if not isinstance(original, list):
		raise error("The original value is not a list!")
	# LIST & VALUE
	if not isinstance(new, list):
		output = original + [new]
	# LIST & LIST
	elif len(original) == 0:
		output = new
	elif len(new) == 0:
		output = original
	# LIST-VALUE & LIST-VALUE
	elif not isinstance(original[0], list) and not isinstance(new[0], list):
		if (strategy & MERGE_LIST_NO_ADD):
			output = original
		else:
			if (strategy & MERGE_KEEP_ORDER):
				# Duplicate the list
				new_list = list(original)
				for v in new:
					if v not in new_list:
						new_list.append(v)
			else:
				new_list = list(set(original + new))
			if not (strategy & MERGE_KEEP_EMPTY):
				new_list = filter(len, new_list)
			output = new_list
	# LIST-LIST
	elif isinstance(original[0], list):
		# LIST-LIST & LIST-LIST
		if not isinstance(new[0], list):
			new = [new]
		# Re-copy the original variable into the output variable
		result = []
		for o in original:
			if not isinstance(o, list):
				raise error("Incompatible type: %s" % (str(original)))
			if len(o) != 0:
				result.append(list(o))
		# Look if a value already exists
		for n in new:
			if not isinstance(n, list):
				raise error("Incompatible type: %s" % (str(new)))
			is_match = False
			# This variable records the match with the most probability
			match_record = [False, -1, -1]
			for j, o in enumerate(result):
				is_match = True
				similarity = 0
				for i in range(min(len(o), len(n))):
					# Check if this field can be ignored
					if options['conflict'] and not options['conflict'][i]:
						continue
					# Count the number of identical elements that identifies this field with the current one
					if o[i] == n[i]:
						similarity = similarity + 1
					# If this filed is not a match
					if o[i] != n[i] and o[i] not in EMPTY_VALUES and n[i] not in EMPTY_VALUES:
						is_match = False
						break
				# If the last item was a match, record it
				if is_match:
					# If this item has more similarities than the previous one, keep this one instead
					if similarity > match_record[1]:
						match_record = [True, similarity, j]
					# Continue to look for other potential fit
			# If there was a match
			if match_record[0]:
				j = match_record[2]
				o = result[j]
				result[j] = merge_values(o, n, strategy = strategy, options = options)

			elif not (strategy & MERGE_LIST_NO_ADD):
				result.append(n)
		output = result
	else:
		# Any other type... throw an error
		raise error("Type not supported: (%s, %s)!" % (str(original), str(new)))

	# Remove duplicates
	if (strategy & MERGE_REMOVE_DUPLICATES):
		new_list = []
		for element in output:
			if list_index_of(new_list, element) == -1:
				new_list.append(element)
		return new_list

	return output

def list_compare(l1, l2):
	"""
	Returns 0 if the list matches
	Returns -1 if l1 contains more info than l2
	Returns 1 if l2 contains more info than l1
	Returns 2 if completely different
	"""

	# Check if v1 is included into v2
	def is_included_into(l1, l2):
		result = 0
		for v1 in l1:
			# Special case if l2 is empty
			if len(l2) == 0:
				return -1
			# By default there is no match
			best_r = 2
			for v2 in l2:
				r = value_compare(v1, v2)
				# There is a match
				if r == 0:
					best_r = 0
					break
				# If there is a partial match
				if r in [-1, 1]:
					best_r = r
			# Merge with the current result
			if result == 0:
				result = best_r
			elif best_r == 0:
				pass
			elif result == best_r:
				pass
			else:
				result = 2
		return result

	r1 = is_included_into(l1, l2)
	r2 = is_included_into(l2, l1)

	# The two list are similar
	if r1 == 0 and r2 == 0:
		return 0
	# Means there is more info in l1 or l1 is diff and r2 is equal
	elif r1 in [-1, 2] and r2 in [0, 1]:
		return -1
	# Means there is more info in l2 or l2 is diff and r1 is equal
	elif r1 == [0, 1] and r2 in [-1, 2]:
		return 1
	# These should be impossible cases
	elif r1 == 1 and r2 == 0:
		raise error("This should never happen: `%s' has more info than `%s' and `%s' is included into `%s'." % (str(l2), str(l1), str(l2), str(l1)))
	elif r1 == 0 and r2 == 1:
		raise error("This should never happen: `%s' has more info than `%s' and `%s' is included into `%s'." % (str(l1), str(l2), str(l1), str(l2)))
	# Any other result combination is different
	return 2


def value_compare(v1, v2):
	"""
	Returns 0 if the values matches
	Returns -1 if v1 contains more info than v2
	Returns 1 if v2 contains more info than v1
	Returns 2 if completely different
	"""
	if isinstance(v1, list) and isinstance(v2, list):
		# By defautl values are similar
		result = 0
		for i in range(min(len(v1), len(v2))):
			r = value_compare(v1[i], v2[i])
			if result == 0:
				result = r
			elif r == 0:
				pass
			elif result == r:
				pass
			else:
				result = 2
		for j in range(i + 1, max(len(v1), len(v2))):
			if j < len(v1):
				# If v1 contains already more info, then the result is -1
				if result == -1:
					break
				v = v1[j]
			else:
				# If v2 contains already more info, then the result is 1
				if result == 1:
					break
				v = v2[j]
			if v not in EMPTY_VALUES:
				result = 2
				break
		return result
	# Handle strings
	elif isinstance(v1, str) and isinstance(v2, str):
		if v1 in EMPTY_VALUES and v2 not in EMPTY_VALUES:
			return 1
		if v2 in EMPTY_VALUES and v1 not in EMPTY_VALUES:
			return -1
		elif v1 in YES_VALUES and is_number(v2):
			return 1
		elif v2 in YES_VALUES and is_number(v1):
			return -1
		elif v1 in YES_VALUES and v2 in YES_VALUES:
			return 0
		elif v1 in NO_VALUES and v2 in NO_VALUES:
			return 0
		elif is_number(v1) and is_number(v2):
			# Check number, they can be written differently but be identical
			if to_number(v1) == to_number(v2):
				return 0
		elif v1 == v2:
			return 0
		return 2
	return 2

def list_index_of(my_list, element):
	"""
	Returns the index of the first element that matches `element' in the list.
	If there is no match, returns -1.
	"""
	for i, e in enumerate(my_list):
		if value_compare(e, element) == 0:
			return i
	return -1

def number_to_string(x):
	"""
	Convert a number into a string, make sure the number does not write like 0.1e-7
	"""

	if not isinstance(x, int) and not isinstance(x, float):
		return str(x)

	s = repr(float(x))
	e_loc = s.lower().find('e')
	if e_loc == -1:
		if re.match(r"^.*\.0*$", s):
			return str(int(x))
		return s

	mantissa = s[:e_loc].replace('.', '')
	exp = int(s[e_loc+1:])

	# assert s[1] == '.' or s[0] == '-' and s[2] == '.', "Unsupported format"
	sign = ''
	if mantissa[0] == '-':
		sign = '-'
		mantissa = mantissa[1:]
	digitsafter = len(mantissa) - 1 # num digits after the decimal point
	if exp >= digitsafter:
		return sign + mantissa + '0' * (exp - digitsafter)
	elif exp <= -1:
		return sign + '0.' + '0' * (-exp - 1) + mantissa
	ip = exp + 1 # insertion point
	if mantissa[ip:] == "0":
		return sign + mantissa[:ip]
	return sign + mantissa[:ip] + '.' + mantissa[ip:]

def clean_value(value):
	"""
	This function goes through a value and cleans it
	"""
	if isinstance(value, list):
		for i, v in enumerate(value):
			value[i] = clean_value(v)
	elif isinstance(value, str):
		if is_number(value):
			value = number_to_string((to_number(value)))
	else:
		raise error("This value `%s' is not supported." % (str(value)))
	return value

def clean_list(obj, options = {}):
	"""
	This function will apply a scheme for the list and fill the empty values
	if any by a specific value accoridng to the rules.
	"""
	# Make sure the options are up-to-date
	options = options_prepare(options)
	# Loop through the different rules if any
	for rule in options['list_rules']:
		result = {
			'match': False,
			'pattern': []
		}
		# Check if the rule matches
		if isinstance(rule['pattern'], str) or isinstance(rule['pattern'], re._pattern_type):
			result['match'] = True
			for v in obj:
				if not re.match(rule['pattern'], v):
					result['match'] = False
					break
				result['pattern'].append(True)
		elif isinstance(rule['pattern'], list):
			result['match'] = True
			for i, v in enumerate(obj):
				if len(rule['pattern']) <= i or rule['pattern'][i] == None:
					result['pattern'].append(False)
				elif not re.match(rule['pattern'][i], v):
					result['match'] = False
					break
				else:
					result['pattern'].append(True)
		# If it matches apply the fill pattern
		if result["match"]:
			obj = object_clone(obj)
			# If the fill pattern is a string apply it to all non-matched values
			if isinstance(rule['fill'], str):
				for i, v in enumerate(result["pattern"]):
					if not v:
						obj[i] = rule['fill']
			# If the fill pattern is a list, apply the non-None pattern
			elif isinstance(rule['fill'], list):
				for i, v in enumerate(rule['fill']):
					if v is not None:
						obj[i] = rule['fill'][i]

	return obj

def merge_strings(original, new, strategy = MERGE_STRATEGY_REPLACE | MERGE_STRING, options = {}):
	"""
	This function will merge 2 strings together. If the strings are different, it will
	merge both and separate them with the SEPARATOR character.
	"""
	# Make sure the options are up-to-date
	options = options_prepare(options)

	SEPARATOR = options['separator']
	NEWLINE = options['newline']

	# Make sure that the values are strings
	if not isinstance(original, str) or not isinstance(new, str):
		raise error("The values passed in argument are not strings.")

	# Handle multiline values
	if strategy & MERGE_MULTILINE:
		original = original.split(NEWLINE)
		new = new.split(NEWLINE)
		value = merge_values(original, new, strategy = (strategy & ~MERGE_MULTILINE) | MERGE_STRING, options = options)
		return NEWLINE.join(value)

	# If new is a empty string ""
	if new in EMPTY_VALUES:
		return str(original)
	if original in EMPTY_VALUES:
		return str(new)

	# Fill method strategy
	if (strategy & MERGE_STARTEGY_MASK) == MERGE_STRATEGY_FILL:
		return str(original)

	# If the original value is not null
	if original != new:
		if (strategy & MERGE_CONCATENATE):
			l1 = original.split(SEPARATOR)
			l2 = new.split(SEPARATOR)
			l = merge_lists(l1, l2, strategy = MERGE_KEEP_ORDER | MERGE_STRING, options = options)
			if not strategy & MERGE_KEEP_ORDER:
				l.sort()
			return SEPARATOR.join(l)

	return new

def merge_numbers(original, new, strategy = MERGE_STRATEGY_REPLACE, options = {}):
	"""
	Merge 2 numbers together. Different strategies can be adopted.
	"""

	# Make sure the options are up-to-date
	options = options_prepare(options)

	# Cast the input as a string and replace "no" with "0"
	p = re.compile("^(" + "|".join(NO_VALUES) + ")$")
	original = p.sub("0", str(original).lower())
	new = p.sub("0", str(new).lower())

	# If new is a empty string ""
	if new in EMPTY_VALUES:
		return number_to_string(original)
	if original in EMPTY_VALUES:
		return number_to_string(new)

	# Convert the argument to numbers, and consider "no" as "0"
	n1 = to_number(original)
	n2 = to_number(new)

	# If these 2 are numbers
	if n1 != None and n2 != None:
		if (strategy & MERGE_STARTEGY_MASK) == MERGE_STRATEGY_REPLACE:
			return number_to_string(n2)
		elif (strategy & MERGE_STARTEGY_MASK) == MERGE_STRATEGY_ADD:
			return number_to_string(n1 + n2)
		elif (strategy & MERGE_STARTEGY_MASK) == MERGE_STRATEGY_MIN:
			return number_to_string(min(n1, n2))
		elif (strategy & MERGE_STARTEGY_MASK) == MERGE_STRATEGY_MAX:
			return number_to_string(max(n1, n2))
		elif (strategy & MERGE_STARTEGY_MASK) == MERGE_STRATEGY_FILL:
			return number_to_string(n1)
		else:
			raise error("This strategy (%s) is not supported." % (str(strategy)))

	# If original == "yes" and new == "0" and stategry is MAX or ADD or FILL
	elif original in YES_VALUES and n2 == 0 and (strategy & MERGE_STARTEGY_MASK) in [MERGE_STRATEGY_MAX, MERGE_STRATEGY_ADD, MERGE_STRATEGY_FILL]:
		return "yes"

	# If original == "yes" and new > 0 and strategy is FILL
	elif original in YES_VALUES and n2 > 0 and (strategy & MERGE_STARTEGY_MASK) in [MERGE_STRATEGY_FILL]:
		return number_to_string(new)

	# If new == "yes" and strategy is MIN
	elif new in YES_VALUES and (strategy & MERGE_STARTEGY_MASK) == MERGE_STRATEGY_MIN:
		return number_to_string(original)

	# If new == "yes" and original is a number > 0
	elif new in YES_VALUES and n1 > 0:
		return number_to_string(original)

	elif (strategy & MERGE_STARTEGY_MASK) == MERGE_STRATEGY_FILL:
		return original

	return number_to_string(new)

def merge_values(original, new, strategy = MERGE_STRATEGY_REPLACE, options = {}):
	"""
	This function merges 2 values and returns the result.
	Values can be strings or list containing strings.
	"""

	# Make sure the options are up-to-date
	options = options_prepare(options)

	# Convert numbers to string
	if isinstance(original, int) or isinstance(original, float):
		original = str(original)
	if isinstance(new, int) or isinstance(new, float):
		new = str(new)

	# If None type
	if new is None:
		return original
	if original is None:
		return new
	# STRING & LIST are not compatible
	if isinstance(original, str) and isinstance(new, list):
		return merge_values([original], new, strategy = strategy, options = options)
	# LIST & STRING are also not compatible
	if isinstance(original, list) and isinstance(new, str):
		raise error("Incomaptible types! (list & str)")
	# STRING and STRING
	if isinstance(original, str) and isinstance(new, str):
		# If the 2 values are numbers
		if (not strategy & MERGE_STRING) and (is_number(original) or original in YES_VALUES + NO_VALUES) and (is_number(new) or new in YES_VALUES + NO_VALUES):
			return merge_numbers(original, new, strategy = strategy, options = options)
		return merge_strings(original, new, strategy = strategy, options = options)
	# LIST and LIST <- multi-value parameter
	if isinstance(original, list) and isinstance(new, list):
		result = []
		for i in range(max(len(original), len(new))):
			if len(original) <= i:
				result.append(new[i])
			elif len(new) <= i:
				result.append(original[i])
			else:
				result.append(merge_values(original[i], new[i], strategy = strategy, options = options))
		return result
	# Any other type... throw an error
	raise error("Type not supported: (%s, %s)!" % (str(original), str(new)))
