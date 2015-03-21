#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


import os
import os.path
import shutil
import sys
import shlex
import xlsxwriter

from optparse import OptionParser, OptionGroup

from mculib import *
from mculib.database import *
from mculib.parser import *
from mculib.categories import *

PARAMETERS = {
	'must': [
		{'id': "CategoryMemoryFlash", 'tolerance': 0.1},
		{'id': "CategoryPin", 'tolerance': 0},
		{'id': 'CategoryCPUArchitecture', 'index': 0, 'tolerance': 0, 'match': '>='}
	],
	'select': [
		{'id': 'CategoryCAN', 'match': 'boolean'},
		{'id': 'CategoryUSB', 'index': 0, 'match': 'boolean'},
		{'id': 'CategorySegmentLCD', 'match': 'boolean'},
		{'id': 'CategoryEthernet', 'match': 'boolean'},
		{'id': 'CategoryMaxVoltage', 'tolerance': 0.2},
		{'id': 'CategoryCPUSpeed', 'tolerance': 0.2},
		{'id': 'CategoryQSPI', 'match': 'boolean'},
		{'id': 'CategoryUSART', 'tolerance': 0.3},
		{'id': 'CategoryI2C', 'tolerance': 0.3},
		{'id': 'CategorySPI', 'tolerance': 0.3}
	]
}

NB_ALTERNATIVES = 2

def readValue(db, device, p, mustHave = False):
	value = db.get_item_param_value(device, p["id"])
	if value == "" and mustHave:
		error("The device `%s' is missing `%s'" % (db.get_item_param_value(device, "CategoryDeviceName"), p["id"]))
		return None
	# Get the value if index is set
	if p.has_key("index"):
		value = value[p["index"]]
	# Store the value
	return value

def read(db, device, parameters, mustHave = False):
	"""
	Get the values of this device
	"""
	valueList = []
	# Get the must have parameters
	for p in parameters:
		valueList.append(readValue(db, device, p, mustHave))
	return valueList

def checkValue(valueA, valueB, p):
	# Read the ID
	identifier = p["id"]
	# Read the tolerance
	if p.has_key("tolerance"):
		tolerance = p["tolerance"]
	else:
		tolerance = 0
	# Read the match type
	if p.has_key("match"):
		match = p["match"]
	else:
		match = "normal"
	# If one value or the other is not set, return false
	if valueA == "" or valueB == "" or valueA == None or valueB == None:
		return False
	# Check
	if match == "normal":
		a = to_number(valueA)
		b = to_number(valueB)
		# Handle the special case when a == 0
		if a == 0:
			if b == 0:
				return True
			return False
		# If a or b are "None", means the value is "yes"
		if a == None or b == None:
			return False
		if abs((a - b) * 1. / a) > tolerance:
			return False
	elif match == ">=":
		a = to_number(valueA)
		b = to_number(valueB)
		# If a or b are "None", means the value is "yes"
		if a == None or b == None:
			return False
		if a > b:
			return False
	elif match == "boolean":
		a = to_boolean(valueA)
		b = to_boolean(valueB)
		if a != b:
			return False
	else:
		raise error("Unknown match type")
	return True

def check(valuesA, valuesB, parameters):
	"""
	Check the values
	"""
	result = True
	for index, p in enumerate(parameters):
		result = result and checkValue(valuesA[index], valuesB[index], p)
	return result

def generate(env, args):

	# Select devices/parameters
	db = env.get_db()

	# Output
	if not os.path.exists("output/cross_reference"):
		os.makedirs("output/cross_reference")
	output = "output/cross_reference/cross_reference.xlsx"

	# Create an new Excel file and add a worksheet
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet("Cross Reference")

	# Select all MCUs
	crossA = DatabaseSelector(db).select("!CategoryHidden=yes;!CategoryDeviceStatus=mature;!CategoryLegacy=yes;CategoryDeviceManufacturer=microchip").get()
	crossB = DatabaseSelector(db).select("!CategoryHidden=yes;!CategoryDeviceStatus=mature;!CategoryLegacy=yes;CategoryDeviceManufacturer=atmel;!CategoryDeviceName=(at89|at83|at32uc3).*;!CategoryDeviceName=.*automotive.*").get()

	for y, deviceA in enumerate(crossA):

		valuesA = read(db, deviceA, PARAMETERS['must'], mustHave = True)
		if valuesA == None:
			error("Ignoring device `%s'" % (db.get_item_param_value(deviceA, "CategoryDeviceName")))
			continue
		selectA = read(db, deviceA, PARAMETERS['select'])

		mustObj = object_clone(PARAMETERS['must'])

		# Make sure
		while True:

			matchList = []
			for deviceB in crossB:

				valuesB = read(db, deviceB, mustObj, mustHave = True)
				if valuesB == None:
					error("Ignoring device `%s'" % (db.get_item_param_value(deviceB, "CategoryDeviceName")))
					continue

				# Check
				if check(valuesA, valuesB, mustObj):
					matchList.append(deviceB)

			# Exit the loop only if there is more than an item found
			if len(matchList) > 0:
				break

			# Else update the tolerance
			for i, p in enumerate(mustObj):
				mustObj[i]["tolerance"] = mustObj[i]["tolerance"] + 0.1

		# If too many options
		if len(matchList) > 0:
			sortedMatchList = []
			# Loop through the devices
			for deviceB in matchList:
				# Get the values
				selectB = read(db, deviceB, PARAMETERS['select'])
				# Initialize the score
				score = 0
				# The max score for this round
				iterScore = len(selectB)
				# Loop through the values
				for index, valueB in enumerate(selectB):
					# Check the value
					if checkValue(selectA[index], valueB, PARAMETERS['select'][index]):
						# Update the score
						score = score + iterScore
					# Update the iterscore
					iterScore = iterScore * 1. / 2.
				sortedMatchList.append({
					'score': score,
					'device': deviceB
				})
#				print "score %s %f" % (str(db.get_item_param_value(deviceB, "CategoryDeviceName")), score)
			matchList = sorted(sortedMatchList, key=lambda s: -s['score'])

		# If there are no match
		else:
			print "No match"

		# Match
		print db.get_item_param_value(deviceA, "CategoryDeviceName")
		print "Match %i device(s): %s" % (len(matchList), ", ".join(["%s (%f)" % (db.get_item_param_value(d["device"], "CategoryDeviceName"), d["score"]) for d in matchList]))

		# Write the data to the worksheet
		worksheet.write(y, 0, db.get_item_param_value(deviceA, "CategoryDeviceName"))
		worksheet.write(y, 1, db.get_item_param_value(deviceA, "CategoryMemoryFlash"))
		worksheet.write(y, 2, db.get_item_param_value(deviceA, "CategoryMemorySRAM"))
		worksheet.write(y, 3, db.get_item_param_value(deviceA, "CategoryIO"))
		offset = 4

		for index, d in enumerate(matchList):
			worksheet.write(y, offset + index*4, db.get_item_param_value(d["device"], "CategoryDeviceName"))
			worksheet.write(y, offset + index*4 + 1, db.get_item_param_value(d["device"], "CategoryMemoryFlash"))
			worksheet.write(y, offset + index*4 + 2, db.get_item_param_value(d["device"], "CategoryMemorySRAM"))
			worksheet.write(y, offset + index*4 + 3, db.get_item_param_value(d["device"], "CategoryIO"))

	# Close the Workbook
	workbook.close()

if __name__ == "__main__":

	args_parser = OptionParser(usage="""""")

	env = Env(args_parser = args_parser, enable_write_db = False)

	# Deal with the options
	generate(env, args_parser)

	# Close the environment
	env.close()
