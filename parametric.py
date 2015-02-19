#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

# This file will generate the parametric table

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

SHEET_NAME = "Parametric Table"

PRESET_BASIC = {
	'orderingCodes': False,
	'categories': [ 'device', 'manufacturer', 'topfamily', 'family', 'status', 'cpu', 'cpuspeed', 'arch', 'archtype', 'dsp', 'fpu', 'hwmul', 'hwdiv', 'dma', 'memflash', 'memfram', 'memsram', 'memeeprom', 'cache', 'dualbank', 'wdt', 'rtc', 'pwm', '8bit', '16bit', '32bit', 'usart', 'i2c', 'spi', 'qspi', 'lin', 'can', 'i2s', 'crc', 'mci', 'ebi', 'usb', 'usbtype', 'usbspeed', 'ethernet', 'lcd', 'graph', 'camera', 'crypto', 'rng', 'tamper', 'tempsens', 'ac', 'gain', 'adc1', 'adc1ch', 'adc1res', 'adc1speed', 'adc2', 'adc2ch', 'adc2res', 'adc2speed', 'dac1', 'dac1res', 'dac2', 'dac2res', 'vmin', 'vmax', 'tmin', 'tmax', 'io', 'io5v', 'iostrength', 'launch', 'pin', 'packages' ]
}

PRESET_PRICING = {
	'orderingCodes': True,
	'categories': [ 'device', 'manufacturer', 'topfamily', 'family', 'status', 'cpu', 'cpuspeed', 'arch', 'archtype', 'dsp', 'fpu', 'hwmul', 'hwdiv', 'dma', 'memflash', 'memfram', 'memsram', 'memeeprom', 'cache', 'dualbank', 'wdt', 'rtc', 'pwm', '8bit', '16bit', '32bit', 'usart', 'i2c', 'spi', 'qspi', 'lin', 'can', 'i2s', 'crc', 'mci', 'ebi', 'usb', 'usbtype', 'usbspeed', 'ethernet', 'lcd', 'graph', 'camera', 'crypto', 'rng', 'tamper', 'tempsens', 'ac', 'gain', 'adc1', 'adc1ch', 'adc1res', 'adc1speed', 'adc2', 'adc2ch', 'adc2res', 'adc2speed', 'dac1', 'dac1res', 'dac2', 'dac2res', 'vmin', 'vmax', 'tmin', 'tmax', 'io', 'io5v', 'iostrength', 'launch', 'price', 'pricevolume', 'pricedk1', 'pricedk1k', 'pricedk10k', 'packaging', 'pin', 'packages' ]
}

# Atmel preset
PRESET_ATMEL = object_clone(PRESET_PRICING)
PRESET_ATMEL.update({
	'orderingCodes': False,
	'style': 'Table Style Medium 2',
	'x': 0,
	'y': 1,
	'write': [{
		'x': 0,
		'y': 0,
		'data': 'This document is strictly Atmel confidential and must not be shared with any individual outside this organization.'
	}]
})

# When the data starts
COLSTART = 2

# Handle numerical values
def num(data, ratio = 1):
	if data:
		if is_number(data):
			return float(data) / ratio
		return str(data)
	else:
		return ""

def generate_row(db, mcu, col_data, preset):

	# Handle GenericFeatureExtendedCategory categories
	def fe(data):
		if data:
			if len(data) > 1 and data[1]:
				return str(data[1])
			return str(data[0])
		else:
			return ""

	# This MCU data
	item = []

	# MCU object
	item.append(mcu)

	# First column is the URL
	doc = db.get_item_param_value(mcu, "CategoryDatasheet")
	if doc:
		item.append(doc)
	else:
		item.append(db.get_item_param_value(mcu, "CategoryWebPage"))

	# Next look into the identifiers
	for identifier in preset['categories']:
		# Normal Categories
		if identifier in ["device", "manufacturer", "topfamily", "family", "status", "cpu", "dsp", "fpu", "hwmul", "hwdiv", "cache", "dualbank", "wdt", "rtc", "graph", "camera", "rng", "tempsens", "launch", "packaging"]:
			item.append(db.get_item_param_value(mcu, col_data[identifier]['class'].to_param()))
		# Number Categories
		elif identifier in ["dma", "memeeprom", "pwm", "8bit", "16bit", "32bit", "usart", "i2c", "spi", "qspi", "lin", "can", "i2s", "mci", "crc", "cpuspeed", "memflash", "memfram", "memsram", "lcd", "tamper", "ac", "gain", "vmin", "vmax", "tmin", "tmax", "io", "io5v", "iostrength", "pin"]:
			item.append(num(db.get_item_param_value(mcu, col_data[identifier]['class'].to_param()), col_data[identifier]['ratio']))
		# Feature categories
		elif identifier in ["ebi", "crypto"]:
			item.append(fe(db.get_item_param_value(mcu, col_data[identifier]['class'].to_param())))
		# Architecture
		elif identifier in ["arch", "archtype"]:
			arch = db.get_item_param_value(mcu, "CategoryCPUArchitecture")
			if arch and len(arch) and identifier == "arch":
				item.append(num(arch[0]))
			elif arch and len(arch) > 1 and identifier == "archtype":
				item.append(arch[1])
			else:
				item.append("")
		# USB
		elif identifier in ["usb", "usbtype", "usbspeed"]:
			usb = db.get_item_param_value(mcu, "CategoryUSB")
			if usb and len(usb) > 0 and usb[0] and identifier == "usb":
				item.append(num(usb[0]))
			elif usb and len(usb) > 0 and usb[0] and identifier == "usbtype":
				item.append(usb[3])
			elif usb and len(usb) > 0 and usb[0] and identifier == "usbspeed":
				item.append(usb[1])
			else:
				item.append("")
		# Ethernet
		elif identifier in ["ethernet"]:
			ethernet = db.get_item_param_value(mcu, "CategoryEthernet")
			if ethernet and len(ethernet) > 0 and ethernet[0]:
				item.append(num(ethernet[0]))
			else:
				item.append("")
		# ADC / DAC
		elif identifier in ["adc1", "adc1ch", "adc1res", "adc1speed", "adc2", "adc2ch", "adc2res", "adc2speed", "dac1", "dac1ch", "dac1res", "dac1speed", "dac2", "dac2ch", "dac2res", "dac2speed"]:
			if identifier in ["adc1", "adc1ch", "adc1res", "adc1speed", "adc2", "adc2ch", "adc2res", "adc2speed"]:
				analog = db.get_item_param_value(mcu, "CategoryADC")
			else:
				analog = db.get_item_param_value(mcu, "CategoryDAC")

			if analog and len(analog) > 0 and identifier in ["adc1", "adc1ch", "adc1res", "adc1speed", "dac1", "dac1ch", "dac1res", "dac1speed"]:
				analog = analog[0]
			elif analog and len(analog) > 0 and identifier in ["adc2", "adc2ch", "adc2res", "adc2speed", "dac2", "dac2ch", "dac2res", "dac2speed"]:
				if len(analog) == 1:
					analog = ["-", "-", "-", "-"]
				else:
					analog = analog[1]
			else:
				analog = None
			if analog and len(analog) > 0 and identifier in ["adc1", "adc2", "dac1", "dac2"]:
				item.append(num(analog[0]))
			elif analog and len(analog) > 1 and identifier in ["adc1ch", "adc2ch", "dac1ch", "dac2ch"]:
				item.append(num(analog[1]))
			elif analog and len(analog) > 2 and identifier in ["adc1res", "adc2res", "dac1res", "dac2res"]:
				item.append(num(analog[2]))
			elif analog and len(analog) > 3 and identifier in ["adc1speed", "adc2speed", "dac1speed", "dac2speed"]:
				item.append(num(analog[3], 1000))
			else:
				item.append("")
		# Packages
		elif identifier in ["packages"]:
			package = db.get_item_param_value(mcu, "CategoryPackage")
			display = []
			for p in package:
				s = ""
				if len(p) > 0 and p[0]:
					s = p[0]
				if len(p) > 1 and p[1]:
					if p[0] != "":
						s = s + "-" + p[1]
					else:
						s = p[1]
				extra = ""
				if len(p) > 2 and p[2]:
					extra = "x".join(p[2:])
					if extra != "":
						s = s + " " + extra + "mm"
				display.append(s)
			item.append(" / ".join(display))
		# Pricing
		elif identifier in ["price", "pricevolume"]:
			price = db.get_item_param_value(mcu, "CategoryPricing")
			if price and len(price) and len(price[0]) > 1 and price[0][1] == "$" and identifier == "price":
				item.append(num(price[0][0]))
			elif price and len(price) and len(price[0]) > 1 and price[0][1] == "$" and identifier == "pricevolume":
				item.append(num(price[0][2]))
			else:
				item.append("n/a")
		# DK Pricing
		elif identifier in ["pricedk1", "pricedk1k", "pricedk10k"]:
			# DigiKey Pricing
			price_list = db.get_item_param_value(mcu, "CategoryPricingDigiKey")
			# DigiKey Price 1
			price = ""
			if price_list:
				for p in price_list:
					if len(p) == 3 and to_number(p[2]) <= 1 and identifier == "pricedk1":
						price = min(price, to_number(p[0]))
					elif len(p) == 3 and to_number(p[2]) <= 1000 and identifier == "pricedk1k":
						price = min(price, to_number(p[0]))
					elif len(p) == 3 and to_number(p[2]) <= 10000 and identifier == "pricedk10k":
						price = min(price, to_number(p[0]))
			item.append(num(price))
		# Any other identifier is not supported
		else:
			raise error("This category identifier `%s' is not supported." % (identifier))

	return item

def generate(env, args, preset_data):

	# Current timestamp
	t = int(time.time())
	d = datetime.datetime.fromtimestamp(t)

	# Update the preset variable
	preset = {
		'orderingCodes': False,
		'categories': [],
		'style': 'Table Style Medium 21',
		'x': 1,
		'y': 1,
		'filename': "%.4i.%.2i Microcontrollers Parametric Table.xlsx" % (d.year, d.month),
		'write': []
	}
	preset.update(preset_data)

	# Select devices/parameters
	db = env.get_db()

	# Output
	if not os.path.exists("output/parametric"):
		os.makedirs("output/parametric")
	output = "output/parametric/%s" % (str(preset['filename']))

	# Create an new Excel file and add a worksheet.
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet(SHEET_NAME)

	# Default format
	format = workbook.add_format()
	format.set_align('center')
	format_left = workbook.add_format()
	format_bold = workbook.add_format({'bold': True})
	format_bold.set_align('center')
	format_url = workbook.add_format({'bold': True, 'underline': 1})
	format_url.set_align('center')
	format_mhz = workbook.add_format({'num_format': '#,##0" MHz"'})
	format_mhz.set_align('center')
	format_kilobytes = workbook.add_format({'num_format': '#,##0.0" KB"'})
	format_kilobytes.set_align('center')
	format_bytes = workbook.add_format({'num_format': '#,##0" B"'})
	format_bytes.set_align('center')
	format_ksps = workbook.add_format({'num_format': '0.0" Ksps"'})
	format_ksps.set_align('center')
	format_channels = workbook.add_format({'num_format': '0"-ch"'})
	format_channels.set_align('center')
	format_bits = workbook.add_format({'num_format': '0"-bit"'})
	format_bits.set_align('center')
	format_ma = workbook.add_format({'num_format': '0"mA"'})
	format_ma.set_align('center')
	format_v = workbook.add_format({'num_format': '0.0"V"'})
	format_v.set_align('center')
	format_c = workbook.add_format({'num_format': '0"C"'})
	format_c.set_align('center')
	format_dollar = workbook.add_format({'num_format': '"$"0.00'})
	format_dollar.set_align('center')
	format_k = workbook.add_format({'num_format': '0.###"K"'})
	format_k.set_align('center')

	# Select all MCUs
	selected_mcu = DatabaseSelector(db).select("!CategoryHidden=yes;!CategoryDeviceStatus=mature;!CategoryLegacy=yes").get()
#	selected_mcu = DatabaseSelector(db).select("!CategoryHidden=yes;!CategoryDeviceStatus=mature;!CategoryLegacy=yes;CategoryDeviceName=at32uc3a364").get()
	# Print a message
	env.info("Identified %i device(s)." % (len(selected_mcu)), 1)

	# Column description
	col_data = {
		'device': { 'header': 'Device', 'format': format_bold, 'width': 25, 'class': CategoryDeviceName},
		'manufacturer': {'header': 'Manufacturer', 'format': format, 'width': 15},
		'topfamily': {'header': 'Family', 'format': format, 'width': 15},
		'family': {'header': 'Sub-Family', 'format': format, 'width': 15},
		'status': {'header': 'Status', 'format': format, 'width': 15},
		'cpu': {'header': 'Core', 'format': format, 'width': 15},
		'cpuspeed': {'header': 'Max Speed', 'format': format_mhz, 'width': 15, 'ratio': 1000000},
		'arch': {'header': 'Arch.', 'format': format_bits, 'width': 10},
		'archtype': {'header': 'Arch. Type', 'format': format, 'width': 10},
		'dsp': {'header': 'DSP', 'format': format, 'width': 5},
		'fpu': {'header': 'FPU', 'format': format, 'width': 5},
		'hwmul': {'header': 'HW Mul', 'format': format, 'width': 10},
		'hwdiv': {'header': 'HW Div', 'format': format, 'width': 10},
		'dma': {'header': 'DMA', 'format': format_channels, 'width': 7},
		'memflash': {'header': 'Flash', 'format': format_kilobytes, 'width': 10, 'ratio': 1024},
		'memfram': {'header': 'FRAM', 'format': format_kilobytes, 'width': 10, 'ratio': 1024},
		'memsram': {'header': 'SRAM', 'format': format_kilobytes, 'width': 10, 'ratio': 1024},
		'memeeprom': {'header': 'EEPROM', 'format': format_bytes, 'width': 10},
		'cache': {'header': 'Cache', 'format': format, 'width': 10},
		'dualbank': {'header': 'Dual-Bank', 'format': format, 'width': 12},
		# Timers
		'wdt': {'header': 'WDG', 'format': format, 'width': 7},
		'rtc': {'header': 'RTC', 'format': format, 'width': 7},
		'pwm': {'header': 'PWM', 'format': format, 'width': 7},
		'8bit': {'header': '8-bit Timer', 'format': format, 'width': 12},
		'16bit': {'header': '16-bit Timer', 'format': format, 'width': 12},
		'32bit': {'header': '32-bit Timer', 'format': format, 'width': 12},
		# Digital
		'usart': {'header': 'UART', 'format': format, 'width': 7},
		'i2c': {'header': 'I2C', 'format': format, 'width': 7},
		'spi': {'header': 'SPI', 'format': format, 'width': 7},
		'qspi': {'header': 'Quad-SPI', 'format': format, 'width': 11},
		'lin': {'header': 'LIN', 'format': format, 'width': 7},
		'can': {'header': 'CAN', 'format': format, 'width': 7},
		'i2s': {'header': 'I2S', 'format': format, 'width': 7},
		'crc': {'header': 'CRC', 'format': format, 'width': 7},
		'mci': {'header': 'MCI', 'format': format, 'width': 7},
		'ebi': {'header': 'EBI', 'format': format, 'width': 10},
		# USB
		'usb': {'header': 'USB', 'format': format, 'width': 7},
		'usbtype': {'header': 'USB Type', 'format': format, 'width': 11},
		'usbspeed': {'header': 'USB Speed', 'format': format, 'width': 11},
		# Ethernet
		'ethernet': {'header': 'Ethernet', 'format': format, 'width': 10},
		# HMI
		'lcd': {'header': 'Segment LCD', 'format': format, 'width': 15},
		'graph': {'header': 'Gfx LCD', 'format': format, 'width': 10},
		'camera': {'header': 'Camera', 'format': format, 'width': 10},
		# Security
		'crypto': {'header': 'Cryptography', 'format': format, 'width': 15},
		'rng': {'header': 'RNG', 'format': format, 'width': 10},
		'tamper': {'header': 'Tamper', 'format': format, 'width': 10},
		# Analog
		'tempsens': {'header': 'Temp Sensor', 'format': format, 'width': 15},
		'ac': {'header': 'AC', 'format': format, 'width': 5},
		'gain': {'header': 'Gain Stage', 'format': format, 'width': 12},
		'adc1': {'header': 'ADC1', 'format': format, 'width': 7},
		'adc1ch': {'header': 'ADC1 Ch.', 'format': format_channels, 'width': 11},
		'adc1res': {'header': 'ADC1 Res.', 'format': format_bits, 'width': 11},
		'adc1speed': {'header': 'ADC1 Speed', 'format': format_ksps, 'width': 15},
		'adc2': {'header': 'ADC2', 'format': format, 'width': 7},
		'adc2ch': {'header': 'ADC2 Ch.', 'format': format_channels, 'width': 11},
		'adc2res': {'header': 'ADC2 Res.', 'format': format_bits, 'width': 11},
		'adc2speed': {'header': 'ADC2 Speed', 'format': format_ksps, 'width': 15},
		'dac1': {'header': 'DAC1', 'format': format, 'width': 7},
		'dac1ch': {'header': 'DAC1 Ch.', 'format': format_channels, 'width': 11},
		'dac1res': {'header': 'DAC1 Res.', 'format': format_bits, 'width': 11},
		'dac1speed': {'header': 'DAC1 Speed', 'format': format_ksps, 'width': 15},
		'dac2': {'header': 'DAC2', 'format': format, 'width': 7},
		'dac2ch': {'header': 'DAC2 Ch.', 'format': format_channels, 'width': 11},
		'dac2res': {'header': 'DAC2 Res.', 'format': format_bits, 'width': 11},
		'dac2speed': {'header': 'DAC2 Speed', 'format': format_ksps, 'width': 15},
		# Electrical
		'vmin': {'header': 'Vmin', 'format': format_v, 'width': 10},
		'vmax': {'header': 'Vmax', 'format': format_v, 'width': 10},
		'tmin': {'header': 'Tmin', 'format': format_c, 'width': 10},
		'tmax': {'header': 'Tmax', 'format': format_c, 'width': 10},
		# Pins
		'io': {'header': 'I/Os', 'format': format, 'width': 5},
		'io5v': {'header': '5V Tolerant', 'format': format, 'width': 12},
		'iostrength': {'header': 'I/O Strength', 'format': format_ma, 'width': 12, 'ratio': 0.001},
		# Launch Date
		'launch': {'header': 'Launch', 'format': format, 'width': 10},
		# Price
		'price': {'header': 'Price', 'format': format_dollar, 'width': 10},
		'pricevolume': {'header': 'Volume', 'format': format, 'width': 10},
		'pricedk1': {'header': 'DK Price (1U)', 'format': format_dollar, 'width': 15, 'collapsed': 'min'},
		'pricedk1k': {'header': 'DK Price (1KU)', 'format': format_dollar, 'width': 15, 'collapsed': 'min'},
		'pricedk10k': {'header': 'DK Price (10KU)', 'format': format_dollar, 'width': 16, 'collapsed': 'min'},
		# Packages
		'packaging': {'header': 'Packaging', 'format': format, 'width': 20, 'collapsed': 'concat'},
		'pin': {'header': 'Pin Count', 'format': format, 'width': 12},
		'packages': {'header': 'Packages', 'format': format_left, 'width': 80}
	}
	# Merge the categories with the known ones
	for identifier in col_data:
		temp_data = {
			'width': 10,
			'format': format,
			'ratio': 1
		}
		# Merge the default data with the predefined ones
		if get_parametric_categories(identifier, False) != None:
			object_merge(temp_data, get_parametric_categories(identifier))
		object_merge(temp_data, col_data[identifier])
		col_data[identifier] = temp_data

	# Empty table to contain the data
	data = []
	# Loop through the new devices
	for i, mcu in enumerate(selected_mcu):
		item = generate_row(db, mcu, col_data, preset)
		# Add the device data to the main data array
		data.append(item)

	# Sort the data
	def getDevice(item):
		return item[COLSTART]
	data = sorted(data, key = getDevice)
	def getSubFamily(item):
		return item[COLSTART + 3]
	data = sorted(data, key = getSubFamily)
	def getFamily(item):
		return item[COLSTART + 2]
	data = sorted(data, key = getFamily)
	def getManufacturer(item):
		return item[COLSTART + 1]
	data = sorted(data, key = getManufacturer)

	# Insert aliases
	new_data = []
	collapsed = []
	for d in data:
		# Append the data
		new_data.append(d)
		# Append the level
		collapsed.append(True)
		# Add the MCU to the list
		alias_list = db.get_alias_list(d[0])
		# Loop through the aliases
		alias_items = []
		for alias in alias_list:
			item = generate_row(db, alias, col_data, preset)
			if preset['orderingCodes']:
				new_data.append(item)
				collapsed.append(False)
			alias_items.append(item)
		# Check if any of the categories has collapsed data
		for i, identifier in enumerate(preset['categories']):
			if col_data[identifier].has_key("collapsed"):
				if col_data[identifier]["collapsed"] == "min":
					v = ""
					for item in alias_items:
						v = min(v, item[COLSTART + i])
					d[COLSTART + i] = num(v)
				elif col_data[identifier]["collapsed"] == "concat":
					v = []
					for item in alias_items:
						v.append(item[COLSTART + i])
					d[COLSTART + i] = "/".join(list(set(v)))
		# d[12] = "dsdsd" <- IT WORKS
	data = new_data

	# Extract the URL entry from the table (this is the first entry)
	url = []
	for i, item in enumerate(data):
		url.append(item[1])
		# Delete the saved MCU instance
		del data[i][0]
		# Delete the URL
		del data[i][0]

	# Build the column data
	columns = []
	for i, identifier in enumerate(preset['categories']):
		# Resize the columns
		worksheet.set_column(i + preset['x'], i + preset['x'], col_data[identifier]["width"])
		# Add category comment if applicable
		if col_data[identifier].has_key("description"):
			worksheet.write_comment(0 + preset['y'], i + preset['x'], col_data[identifier]["description"], {'visible': False, 'width': 200, 'height': 400})
		# Set the headers
		columns.append({
			'header': col_data[identifier]['header'],
			'format': col_data[identifier]['format']
		})

	# Draw the full table
	worksheet.add_table(preset['y'], preset['x'], len(data) + preset['y'], len(data[0]) - 1 + preset['x'], {
		'data': data,
		'name': "parametric",
		'columns': columns,
		'style': preset['style']
	})
	# Set the URLs
	for i, address in enumerate(url):
		if address:
			worksheet.write_url(i + 1 + preset['y'], preset['x'], address, format_url, data[i][0])
	# Groups the aliases
	worksheet.outline_settings(True, False, True, False)
	for i, col in enumerate(collapsed):
		if col:
			worksheet.set_row(i + 1 + preset['y'], None, None, {'collapsed': True})
		else:
			worksheet.set_row(i + 1 + preset['y'], None, None, {'level': 1, 'hidden': True})

	# Write data
	for item in preset['write']:
		worksheet.write(item['y'], item['x'], item['data'])

	workbook.close()

if __name__ == "__main__":

	args_parser = OptionParser(usage="""""")

	env = Env(args_parser = args_parser, enable_write_db = False)

	# Deal with the options
	generate(env, args_parser, PRESET_ATMEL)

	# Close the environment
	env.close()
