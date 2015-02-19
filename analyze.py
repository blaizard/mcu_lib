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

import xlsxwriter

def analyze(env, args):
	NB_WEEKS = 52
	SUMMARY_SHEET = "Summary"

	def record_add(record, cat, item):
		if not record.has_key(cat):
			record[cat] = {}
		if not record[cat].has_key(item):
			record[cat][item] = 0
		record[cat][item] = record[cat][item] + 1
		return record

	def record_draw(record, cat, y1, x1):
		# Construct data for the table
		t_data = [[]]
		t_columns = []
		if record.has_key(cat):
			for key in record[cat].keys():
				if key == "":
					t_columns.append({'header': "Unknown", 'format': format})
				else:
					t_columns.append({'header': key, 'format': format})
				t_data[0].append(record[cat][key])
		# Draw the table
		if len(t_columns) > 0:
			worksheet.add_table(y1, x1, y1 + 1, x1 + len(t_columns) - 1, {
				'data': t_data,
				'columns': t_columns,
				'autofilter': False
			})
		# Returns the width of the table
		return len(t_columns)

	def record_draw_pie(sheet, y, x, record_y1, record_x1, record_width, title):
		chart = workbook.add_chart({'type': 'pie'})
		chart.add_series({
			'categories': [manufacturer, record_y1, record_x1, record_y1, record_x1 + record_width - 1],
			'values': [manufacturer, record_y1 + 1, record_x1, record_y1 + 1, record_x1 + record_width - 1]
		})
		chart.set_title({'name': title})
		chart.set_size({'width': 300, 'height': 200})
		worksheet.insert_chart(x, y, chart)

	# Select devices/parameters
	db = env.get_db()

	# Current timestamp
	t = int(time.time())
	d = datetime.datetime.fromtimestamp(t)
	iso = d.isocalendar()

	# Output
	if not os.path.exists("output/analysis"):
		os.makedirs("output/analysis")
	output = "output/analysis/%.4iW%.2i Analysis.xlsx" % (d.year, iso[1])

	# Create an new Excel file and add a worksheet.
	workbook = xlsxwriter.Workbook(output)
	summary = workbook.add_worksheet(SUMMARY_SHEET)

	# Default format
	format = workbook.add_format()
	format.set_align('center')
	format_right = workbook.add_format()
	format_right.set_align('right')
	format_bold = workbook.add_format({'bold': True})

	summary_data = []
	summary_columns = [
		{'header': 'Week', 'total_string': 'Total', 'format': format}
	]
	# Set the week numbers
	for w in range(NB_WEEKS):
		iso = datetime.datetime.fromtimestamp(t - 7*24*3600*w).isocalendar()
		summary_data.append(["%i - W%.2i" % (iso[0], iso[1])])

	# Record
	record = {}

	# Look for all microchip devices released this month
	for i, parser_port in enumerate(parser_ports_list):
		# Identify the manufacturer name
		manufacturer = parser_port["common"].get_manufacturer()
		# Create a new worksheet
		worksheet = workbook.add_worksheet(manufacturer)

		# Select all MCUs per manufacturer
		selected_mcu = DatabaseSelector(db).select("!CategoryHidden=yes;!CategoryDeviceStatus=mature;!CategoryLegacy=yes;!CategoryDeviceStatus=announced;CategoryDeviceManufacturer=" + manufacturer).get()

		# Add tbe manufacturer name to the summary
		summary_columns.append({'header': manufacturer, 'total_function': 'sum', 'format': format})

		# Create the column headers
		format_mhz = workbook.add_format({'num_format': '#,##0" MHz"'})
		format_mhz.set_align('center')
		format_kilobytes = workbook.add_format({'num_format': '#,##0.0" KB"'})
		format_kilobytes.set_align('center')
		format_bytes = workbook.add_format({'num_format': '#,##0" B"'})
		format_bytes.set_align('center')

		# Current line number
		line = 1

		# This records the new devices
		record[manufacturer] = {
			"count": len(selected_mcu)
		}

		# Data for this table
		data = []

		# Loop through the new devices
		for i, mcu in enumerate(selected_mcu):

			timestamp = None

			# Find out the released date of the MCU
			param = db.get_parameter(mcu, "CategoryDeviceName")
			timestamp = db.get_param_date(param)

			#lauch_date_param = db.get_item_param_value(mcu, "CategoryLaunchDate")
			#if lauch_date_param != "":
			#	timestamp = CategoryLaunchDate.parse_date(lauch_date_param)
			#	timestamp = time.mktime(timestamp)

			# Data item for this mcu
			data_item = []

			# TOP FAMILY
			top_family = db.get_item_param_value(mcu, "CategoryDeviceTopFamily")

			# FAMILY
			family = db.get_item_param_value(mcu, "CategoryDeviceFamily")

			# CPU
			cpu = db.get_item_param_value(mcu, "CategoryCPUCore")

			# ARCHITECTURE
			arch = db.get_item_param_value(mcu, "CategoryCPUArchitecture")
			if arch and len(arch) and is_number(arch[0]):
				arch = "%s-bit" % (arch[0])
			else:
				arch = ""

			# Record
			record[manufacturer] = record_add(record[manufacturer], "architecture", arch)
			record[manufacturer] = record_add(record[manufacturer], "cpu", cpu)
			record[manufacturer] = record_add(record[manufacturer], "top_family", top_family)
			record[manufacturer] = record_add(record[manufacturer], "family", family)
			if timestamp and timestamp > t-7*24*3600*NB_WEEKS:
				record[manufacturer] = record_add(record[manufacturer], "architecturey", arch)
				record[manufacturer] = record_add(record[manufacturer], "cpuy", cpu)
				record[manufacturer] = record_add(record[manufacturer], "top_familyy", top_family)
				record[manufacturer] = record_add(record[manufacturer], "familyy", family)
			if timestamp and timestamp > t-7*24*3600:
				record[manufacturer] = record_add(record[manufacturer], "architecturew", arch)
				record[manufacturer] = record_add(record[manufacturer], "cpuw", cpu)
				record[manufacturer] = record_add(record[manufacturer], "top_familyw", top_family)
				record[manufacturer] = record_add(record[manufacturer], "familyw", family)

			# Only keep the recent ones
			if timestamp == None or timestamp < t-7*24*3600*NB_WEEKS: #(NB_WEEKS week ago)
				continue

			# Store relevant data
			data_item.append(db.get_name(mcu))
			data_item.append(top_family)
			data_item.append(family)
			data_item.append(cpu)
			data_item.append(arch)

			# Speed
			speed = db.get_item_param_value(mcu, "CategoryCPUSpeed")
			if speed:
				data_item.append(float(speed) / 1000000)
			else:
				data_item.append("")

			# Flash
			flash = db.get_item_param_value(mcu, "CategoryMemoryFlash")
			if flash:
				data_item.append(float(flash) / 1024)
			else:
				data_item.append("")

			# SRAM
			sram = db.get_item_param_value(mcu, "CategoryMemorySRAM")
			if sram:
				data_item.append(float(sram) / 1024)
			else:
				data_item.append("")

			# EEPROM
			eeprom = db.get_item_param_value(mcu, "CategoryMemoryEEPROM")
			if eeprom:
				data_item.append(int(eeprom))
			else:
				data_item.append("")

			package = db.get_item_param_value(mcu, "CategoryPackage")
			string = ""
			if package:
				package = [int(p[0]) for p in package if is_number(p[0])]
				# Keep only unique values
				package = list(set(package))
				if len(package) == 1:
					string = str(package[0])
				elif len(package) > 1:
					string = "%i - %i" % (min(package), max(package))
			data_item.append(string)

			# Released week
			date = datetime.datetime.fromtimestamp(timestamp)
			week_number = date.isocalendar()[1]
			year = date.isocalendar()[0]
			data_item.append("%i - W%.2i" % (year, week_number))

			# Record key
			record_key = "%i%.2i" % (year, week_number)

			# Increase the device count
			if not record[manufacturer].has_key(record_key):
				record[manufacturer][record_key] = {
					'count': 0
				}
			record[manufacturer][record_key]['count'] = record[manufacturer][record_key]['count'] + 1

			# Add the line
			data.append(data_item)
			# Increase the line count
			line = line + 1

		# Adjust the column width
		for index, width in enumerate([25, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]):
			worksheet.set_column(index, index, width)

		y = 0

		# This week report
		worksheet.write(y, 0, "This Week", format_bold)
		# Construct data for the first table
		worksheet.write(y + 1, 0, "By Family", format_right)
		record_draw(record[manufacturer], "top_familyw", y + 1, 1)
		# Construct data for the first table
		worksheet.write(y + 3, 0, "By Sub-Family", format_right)
		record_draw(record[manufacturer], "familyw", y + 3, 1)
		# Construct data for the first table
		worksheet.write(y + 5, 0, "By CPU", format_right)
		record_draw(record[manufacturer], "cpuw", y + 5, 1)
		# Construct data for the first table
		worksheet.write(y + 7, 0, "By Architecture", format_right)
		width = record_draw(record[manufacturer], "architecturew", y + 7, 1)
		y = y + 10

		# This year report
		worksheet.write(y, 0, "The last %i weeks" % (NB_WEEKS), format_bold)
		# Construct data for the first table
		worksheet.write(y + 12, 0, "By Family", format_right)
		width = record_draw(record[manufacturer], "top_familyy", y + 12, 1)
		record_draw_pie(manufacturer, 0, y + 1, y + 12, 1, width, "By Family")
		# Construct data for the first table
		worksheet.write(y + 14, 0, "By Sub-Family", format_right)
		width = record_draw(record[manufacturer], "familyy", y + 14, 1)
		# Construct data for the first table
		worksheet.write(y + 16, 0, "By CPU", format_right)
		width = record_draw(record[manufacturer], "cpuy", y + 16, 1)
		record_draw_pie(manufacturer, 3, y + 1, y + 16, 1, width, "By CPU")
		# Construct data for the first table
		worksheet.write(y + 18, 0, "By Architecture", format_right)
		width = record_draw(record[manufacturer], "architecturey", y + 18, 1)
		record_draw_pie(manufacturer, 6, y + 1, y + 18, 1, width, "By Architecture")
		y = y + 21

		# In total
		worksheet.write(y, 0, "Complete Portfolio", format_bold)
		# Construct data for the first table
		worksheet.write(y + 12, 0, "By Family", format_right)
		width = record_draw(record[manufacturer], "top_family", y + 12, 1)
		record_draw_pie(manufacturer, 0, y + 1, y + 12, 1, width, "By Family")
		# Construct data for the first table
		worksheet.write(y + 14, 0, "By Sub-Family", format_right)
		width = record_draw(record[manufacturer], "family", y + 14, 1)
		# Construct data for the first table
		worksheet.write(y + 16, 0, "By CPU", format_right)
		width = record_draw(record[manufacturer], "cpu", y + 16, 1)
		record_draw_pie(manufacturer, 3, y + 1, y + 16, 1, width, "By CPU")
		# Construct data for the first table
		worksheet.write(y + 18, 0, "By Architecture", format_right)
		width = record_draw(record[manufacturer], "architecture", y + 18, 1)
		record_draw_pie(manufacturer, 6, y + 1, y + 18, 1, width, "By Architecture")
		y = y + 21

		# Newly released / announced products
		worksheet.write(y, 0, "Newly Released / Announced Products in the last %i weeks" % (NB_WEEKS), format_bold)
		# Draw the full table
		worksheet.add_table(y + 1, 0, y + 1 + len(data), len(data[0]) - 1, {
			'data': data,
			'name': manufacturer,
           		'columns': [
				{'header': 'PCN', 'format': format},
				{'header': 'Family', 'format': format},
				{'header': 'Sub-Family', 'format': format},
				{'header': 'CPU', 'format': format},
				{'header': 'Architecture', 'format': format},
				{'header': 'Speed', 'format': format_mhz},
				{'header': 'Flash', 'format': format_kilobytes},
				{'header': 'SRAM', 'format': format_kilobytes},
				{'header': 'EEPROM', 'format': format_bytes},
				{'header': 'Pin Count', 'format': format},
				{'header': 'Week', 'format': format}
			]}
		)

		# Text with formatting.
		format = workbook.add_format()
		format.set_align('center')
		for w in range(NB_WEEKS):
			iso = datetime.datetime.fromtimestamp(t - 7*24*3600*w).isocalendar()
			# Record key
			record_key = "%i%.2i" % (iso[0], iso[1])
			if record[manufacturer].has_key(record_key):
				summary_data[w].append(record[manufacturer][record_key]['count'])
			else:
				summary_data[w].append(0)

	# SUMMARY TABLE

	# Adjust the column width
	for index in range(len(summary_columns) + 1):
		summary.set_column(index, index, 15)

	y = 41

	# Cumulative summary
	summary.write(y, 0, "Newly Released Products in the last %i weeks" % (NB_WEEKS), format_bold)
	y = y + 1
	# Draw the summary table
	summary.add_table(y, 0, y + len(summary_data) + 1, len(summary_data[0]) - 1, {
		'data': summary_data,
		'name': "summary",
		'total_row': True,
		'columns': summary_columns
	})
	y = y + len(summary_data) + 3


	# Cumulative summary
	summary.write(y, 0, "Cumulative Summary (used to generate the chart)", format_bold)
	y = y + 1
	# Create the cumulative table
	summary_data.reverse()
	# Cumulate the data
	# Loop through the manufacturer (exclude the first column then)
	for manufacturer in range(1, len(summary_data[0])):
		sum = 0
		for i, count in enumerate(summary_data):
			sum = sum + count[manufacturer]
			summary_data[i][manufacturer] = sum
	# Draw the new table
	summary.add_table(y, 0, y + len(summary_data), len(summary_data[0]) - 1, {
		'data': summary_data,
		'name': "summary_cumul",
		'autofilter': False,
		'columns': summary_columns
	})
	# Add a chart
	chart = workbook.add_chart({'type': 'line'})
	chart_col = workbook.add_chart({'type': 'column'})
	# Add the various series
	for i in range(1, len(summary_data[0])):
		chart.add_series({
			'name': [SUMMARY_SHEET, y, i],
			'categories': [SUMMARY_SHEET, y + 1, 0, y + len(summary_data), 0],
			'values': [SUMMARY_SHEET, y + 1, i, y + len(summary_data), i]
		})
		chart_col.add_series({
			'name': [SUMMARY_SHEET, y, i],
			'values': [SUMMARY_SHEET, y + len(summary_data), i, y + len(summary_data), i]
		})
	iso = datetime.datetime.fromtimestamp(t - 7*24*3600*NB_WEEKS).isocalendar()
	chart.set_title({'name': "Cumulative New Product Count Since %iW%.i" % (iso[0], iso[1])})
	chart.set_size({'width': 1000, 'height': 400})
	chart_col.set_size({'width': 400, 'height': 400})
	chart_col.set_x_axis({'name': "Total New Product Count Since %iW%.i" % (iso[0], iso[1]), 'visible': False})
	summary.insert_chart(21, 0, chart)
	summary.insert_chart(21, 10, chart_col)

	y = y + len(summary_data) + 2

	# Total Count
	data = [
		["8-bit"],
		["16-bit"],
		["ARM Cortex-M0"],
		["ARM Cortex-M0+"],
		["ARM Cortex-M3"],
		["ARM Cortex-M4(F)"],
		["ARM Cortex-M7"],
		["Other 32-bit"]
	]
	data_columns = [
		{'header': " ", 'total_string': 'Total'}
	]
	for manufacturer in record:
		r = record[manufacturer]
		total = 0
		if "8-bit" in r["architecture"]:
			data[0].append(r["architecture"]["8-bit"])
			total = total + r["architecture"]["8-bit"]
		else:
			data[0].append(0)
		if "16-bit" in r["architecture"]:
			data[1].append(r["architecture"]["16-bit"])
			total = total + r["architecture"]["16-bit"]
		else:
			data[1].append(0)
		if "cortexm0" in r["cpu"]:
			data[2].append(r["cpu"]["cortexm0"])
			total = total + r["cpu"]["cortexm0"]
		else:
			data[2].append(0)
		if "cortexm0+" in r["cpu"]:
			data[3].append(r["cpu"]["cortexm0+"])
			total = total + r["cpu"]["cortexm0+"]
		else:
			data[3].append(0)
		if "cortexm3" in r["cpu"]:
			data[4].append(r["cpu"]["cortexm3"])
			total = total + r["cpu"]["cortexm3"]
		else:
			data[4].append(0)
		cm4 = 0
		if "cortexm4" in r["cpu"]:
			cm4 = cm4 + r["cpu"]["cortexm4"]
		if "cortexm4f" in r["cpu"]:
			cm4 = cm4 + r["cpu"]["cortexm4f"]
		data[5].append(cm4)
		total = total + cm4
		if "cortexm7" in r["cpu"]:
			data[6].append(r["cpu"]["cortexm7"])
			total = total + r["cpu"]["cortexm7"]
		else:
			data[6].append(0)
		data[7].append(r["count"] - total)
		data_columns.append({'header': manufacturer, 'total_function': 'sum'})
	summary.write(y, 0, "Manufacturer's Portfolio Split", format_bold)
	y = y + 1
	summary.add_table(y, 0, y + len(data) + 1, len(data[0]) - 1, {
		'data': data,
		'columns': data_columns,
		'autofilter': False,
		'total_row': True
	})

	# Add a chart
	chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
	# Add the various series
	for i in range(1, len(data[0])):
		chart.add_series({
			'name': [SUMMARY_SHEET, y, i],
			'categories': [SUMMARY_SHEET, y + 1, 0, y + len(data), 0],
			'values': [SUMMARY_SHEET, y + 1, i, y + len(data), i]
		})
	iso = datetime.datetime.fromtimestamp(t).isocalendar()
	chart.set_title({'name': "Manufacturer's Portfolio Split - %iW%.i" % (iso[0], iso[1])})
	chart.set_size({'width': 1000, 'height': 400})
	summary.insert_chart(0, 0, chart)

	y = y + len(data) + 2

	workbook.close()

if __name__ == "__main__":

	args_parser = OptionParser(usage="""""")

	env = Env(args_parser = args_parser, enable_write_db = False)

	# Deal with the options
	analyze(env, args_parser)

	# Close the environment
	env.close()
