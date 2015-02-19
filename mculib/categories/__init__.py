#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from system import *
from memory import *
from digital import *
from analog import *
from cpu import *
from die import *

# To enable the debug trace capability
from mculib.config import *

def get_category_list():
	return [
		CategoryAlias,
		CategoryDiscovered,
		CategoryHidden,
		CategoryDeviceName,
		CategoryWebPage,
		CategoryDatasheet,
		CategoryOrderPage,
		CategoryDeviceManufacturer,
		CategoryDeviceTopFamily,
		CategoryDeviceFamily,
		CategoryDeviceStatus,
		CategoryProcess,
		CategoryBus,
		CategoryLegacy,
		CategoryMinVoltage,
		CategoryMaxVoltage,
		CategoryMinTemperature,
		CategoryMaxTemperature,
		CategoryPricing,
		CategoryPricingDigiKey,
		CategoryInternalOscillator,
		CategoryInternalOscillatorFrequency,
		CategoryInternalOscillatorAccuracy,
		CategoryBrownOutDetector,
		CategoryPowerOnReset,
		CategoryCRC,
		CategoryMemoryFlash,
		CategoryMemorySRAM,
		CategoryMemoryFRAM,
		CategoryMemoryEEPROM,
		CategoryMemorySelfWrite,
		CategoryMemoryCache,
		CategoryMemoryDualBank,
		CategoryWatchdog,
		CategoryRealTimeClock,
		CategoryTempSensor,
		CategoryIO,
		CategoryIOStrength,
		CategoryIO5VTolerant,
		CategoryPackage,
		CategoryPin,
		CategoryPackaging,
		CategoryCPUCore,
		CategoryCPUCoreSecondary,
		CategoryCPUSpeed,
		CategoryCPUArchitecture,
		CategoryCPUBenchmark,
		CategoryCPUInterruptLatency,
		CategoryHWMul,
		CategoryHWDiv,
		CategoryDMA,
		CategoryPWM,
		CategoryTimer8bit,
		CategoryTimer16bit,
		CategoryTimer32bit,
		CategoryTouchChannel,
		CategoryLaunchDate,
		CategoryCustomLogic,
		CategoryUSART,
		CategoryI2C,
		CategorySPI,
		CategoryQSPI,
		CategoryLIN,
		CategoryCAN,
		CategoryI2S,
		CategoryQEI,
		CategoryMCI,
		CategoryHDMICEC,
		CategorySegmentLCD,
		CategoryGraphicsController,
		CategoryCamera,
		CategoryEBI,
		CategoryUSB,
		CategoryUSBPeripheral,
		CategoryEthernet,
		CategoryEthernetPeripheral,
		CategoryCrypto,
		CategoryRNG,
		CategoryTamper,
		CategoryComparator,
		CategoryOpAmp,
		CategoryADC,
		CategoryADCSpeed,
		CategoryADCChannel,
		CategoryADCPeripheral,
		CategoryADCResolution,
		CategoryADCResolutionBis,
		CategoryDAC,
		CategoryDACSpeed,
		CategoryDACChannel,
		CategoryDACPeripheral,
		CategoryDACResolution,
		CategoryFPU,
		CategoryDSP,
		CategoryHWMul,
		CategoryHWDiv,
		CategoryRegulator,
		CategoryRegulatorVoltageScaling,
		CategoryUniqueID
	] + CategoryCryptoType.extended_classes()

def get_parametric_categories(param = None, strict = True):
	"""
	Return parametric categories.
	A category must have the following properties:
		'id': A uniq identifier corresponding to this category
		'display': The display name (readable name)
		'class': Category class(es) associated with this entry
	In addition it can have any of the following properties:
		'category': The categroy where this category belongs to. A category
			    is a readable string.
		'units': A table containing the units to be suffixed to the value.
			 Each entry in the table is associated with each entry in the multi-value value.
		'compare': A table defining the importance of its values. Each entry
		           in the table is associated with each entry in the multi-value value.
			   A positive value will tell that the greater value is most important while
			   a negative value will tell that the lowest value has more imprtance. The
			   higher the number is, the most important it is. This is used to defined
			   in a multi-value category the importance of the value.
	"""
	parametric_categories = [
		{
				'id': 'alias',
				'class': CategoryAlias
		},
		{
				'id': 'webpage',
				'category': 'Documentation',
				'display': 'WebPage',
				'class': CategoryWebPage
		},
		{
				'id': 'datasheet',
				'category': 'Documentation',
				'display': 'Datasheet',
				'class': CategoryDatasheet
		},
		{
				'id': 'manufacturer',
				'category': 'ID',
				'display': 'Manufacturer',
				'class': CategoryDeviceManufacturer
		},
		{
				'id': 'topfamily',
				'category': 'ID',
				'display': 'Family',
				'class': CategoryDeviceTopFamily
		},
		{
				'id': 'family',
				'category': 'ID',
				'display': 'Sub-Family',
				'class': CategoryDeviceFamily
		},
		{
				'id': 'status',
				'display': 'Status',
				'class': CategoryDeviceStatus
		},
		{
				'id': 'cpu',
				'category': 'CPU',
				'display': 'Core',
				'class': CategoryCPUCore
		},
		{
				'id': 'cpu2',
				'category': 'CPU',
				'display': 'Secondary Core / Processing Unit',
				'class': CategoryCPUCoreSecondary
		},
		{
				'id': 'cpuspeed',
				'category': 'CPU',
				'display': 'Max. Speed',
				'class': CategoryCPUSpeed,
				'units': ["Hz"],
				'compare': [1]
		},
		{
				'id': 'cpuarch',
				'category': 'CPU',
				'display': 'Arch.',
				'class': CategoryCPUArchitecture,
				'units': ["-bit", ""],
				'compare': [1, [["harvard", 10], ["von neumann", 0]]]
		},
		{
				'id': 'cpupipe',
				'category': 'CPU',
				'display': 'Pipeline',
				'class': CategoryCPUPipeline,
				'units': ["stage(s)"]
		},
		{
				'id': 'cpuintlat',
				'category': 'Interrupt',
				'display': 'Min. Latency',
				'description': 'The interrupt latency is the number of cycles from the time the interrupt is asserted to the start of the execution of the interrupt handler',
				'class': CategoryCPUInterruptLatency,
				'units': ["cy"]
		},
		{
				'id': 'cpuintjit',
				'category': 'Interrupt',
				'display': 'Jitter',
				'class': CategoryCPUInterruptJitter,
				'units': ["cy"]
		},
		{
				'id': 'cpubench',
				'category': 'CPU',
				'display': 'Benchmark',
				'class': CategoryCPUBenchmark,
				'units': ["", "", "", ""],
		},
		{
				'id': 'cpubus',
				'category': 'CPU',
				'display': 'Bus Arch.',
				'class': CategoryBus,
				'units': ["x", "", "-bit", ""],
		},
		{
				'id': 'dsp',
				'category': 'CPU',
				'display': 'DSP',
				'class': CategoryDSP,
		},
		{
				'id': 'fpu',
				'category': 'CPU',
				'display': 'FPU',
				'class': CategoryFPU,
		},
		{
				'id': 'hwmul',
				'category': 'CPU',
				'display': 'Hardware Multiplier',
				'class': CategoryHWMul,
		},
		{
				'id': 'hwdiv',
				'category': 'CPU',
				'display': 'Hardware Divider',
				'class': CategoryHWDiv,
		},
		{
				'id': 'dma',
				'category': 'CPU',
				'display': 'DMA',
				'class': CategoryDMA,
				'units': ["-ch"],
				'compare': [1]
		},
		{
				'id': 'memflash',
				'category': 'Memory',
				'display': 'Flash',
				'class': CategoryMemoryFlash,
				'units': ["B"],
				'compare': [1]
		},
		{
				'id': 'memfram',
				'category': 'Memory',
				'display': 'FRAM',
				'class': CategoryMemoryFRAM,
				'units': ["B"],
				'compare': [1]
		},
		{
				'id': 'memsram',
				'category': 'Memory',
				'display': 'SRAM',
				'class': CategoryMemorySRAM,
				'units': ["B"],
				'compare': [1]
		},
		{
				'id': 'memeeprom',
				'category': 'Memory',
				'display': 'EEPROM',
				'class': CategoryMemoryEEPROM,
				'units': ["B"],
				'compare': [1]
		},
		{
				'id': 'selfwrite',
				'category': 'Memory',
				'display': 'Self Write',
				'class': CategoryMemorySelfWrite,
				'compare': [1]
		},
		{
				'id': 'cache',
				'category': 'Memory',
				'display': 'Cache',
				'class': CategoryMemoryCache,
				'compare': [1]
		},
		{
				'id': 'dualbank',
				'category': 'Memory',
				'display': 'Dual-Bank',
				'description': "Independent flash banks allow concurrent code execution and firmware updating with no performance degradation or complex coding routines",
				'class': CategoryMemoryDualBank,
				'compare': [1]
		},
		{
				'id': 'intosc',
				'category': 'System',
				'display': 'Internal Osc.',
				'class': CategoryInternalOscillator,
				'units': ["Hz", "%"],
				'compare': [0, 1]
		},
		{
				'id': 'reg',
				'category': 'System',
				'display': 'Regulator',
				'class': CategoryRegulator,
		},
		{
				'id': 'voltagescaling',
				'category': 'System',
				'display': 'Voltage Scaling',
				'class': CategoryRegulatorVoltageScaling,
		},
		{
				'id': 'por',
				'category': 'System',
				'display': 'POR',
				'class': CategoryPowerOnReset,
				'compare': [1]
		},
		{
				'id': 'bod',
				'category': 'System',
				'display': 'BOD',
				'class': CategoryBrownOutDetector,
				'compare': [1]
		},
		{
				'id': 'uniqueid',
				'category': 'System',
				'display': 'Unique ID',
				'class': CategoryUniqueID,
				'compare': [1]
		},
		{
				'id': 'tempsens',
				'category': 'System',
				'display': 'Temp. Sensor',
				'class': CategoryTempSensor,
				'compare': [1]
		},
		{
				'id': 'special',
				'display': 'Special Features',
				'class': CategorySpecialFeature
		},
		{
				'id': 'wdt',
				'category': 'Timers',
				'display': 'WDT',
				'class': CategoryWatchdog,
				'compare': [1]
		},
		{
				'id': 'rtc',
				'category': 'Timers',
				'display': 'RTC',
				'class': CategoryRealTimeClock,
				'compare': [1]
		},
		{
				'id': 'pwm',
				'category': 'Timers',
				'display': 'PWM',
				'class': CategoryPWM,
				'compare': [1]
		},
		{
				'id': '8bit',
				'category': 'Timers',
				'display': '8-bit',
				'class': CategoryTimer8bit,
				'compare': [1]
		},
		{
				'id': '16bit',
				'category': 'Timers',
				'display': '16-bit',
				'class': CategoryTimer16bit,
				'compare': [1]
		},
		{
				'id': '32bit',
				'category': 'Timers',
				'display': '32-bit',
				'class': CategoryTimer32bit,
				'compare': [1]
		},
		{
				'id': 'io',
				'category': 'Digital',
				'display': 'I/Os',
				'class': CategoryIO,
				'compare': [1]
		},
		{
				'id': 'logic',
				'category': 'Digital',
				'display': 'Custom Logic',
				'class': CategoryCustomLogic,
				'compare': [1]
		},
		{
				'id': 'usart',
				'category': 'Digital',
				'display': 'USART',
				'class': CategoryUSART,
				'compare': [1]
		},
		{
				'id': 'i2c',
				'category': 'Digital',
				'display': 'I&#178;C',
				'class': CategoryI2C,
				'compare': [1]
		},
		{
				'id': 'spi',
				'category': 'Digital',
				'display': 'SPI',
				'class': CategorySPI,
				'compare': [1]
		},
		{
				'id': 'qspi',
				'category': 'Digital',
				'display': 'Quad-SPI',
				'class': CategoryQSPI,
				'compare': [1]
		},
		{
				'id': 'lin',
				'category': 'Digital',
				'display': 'LIN',
				'class': CategoryLIN,
				'compare': [1]
		},
		{
				'id': 'can',
				'category': 'Digital',
				'display': 'CAN',
				'class': CategoryCAN,
				'compare': [1]
		},
		{
				'id': 'i2s',
				'category': 'Digital',
				'display': 'I&#178;S',
				'class': CategoryI2S,
				'compare': [1]
		},
		{
				'id': 'crc',
				'category': 'Digital',
				'display': 'CRC',
				'class': CategoryCRC,
				'compare': [1]
		},
		{
				'id': 'qei',
				'category': 'Digital',
				'display': 'QEI',
				'class': CategoryQEI,
				'compare': [1]
		},
		{
				'id': 'cec',
				'category': 'Digital',
				'display': 'HDMI-CEC',
				'class': CategoryHDMICEC,
				'compare': [1]
		},
		{
				'id': 'mci',
				'category': 'Digital',
				'display': 'Memory Card Interface',
				'class': CategoryMCI,
				'compare': [1]
		},
		{
				'id': 'ebi',
				'category': 'Digital',
				'display': 'EBI',
				'class': CategoryEBI,
				'compare': [1]
		},
		{
				'id': 'usb',
				'category': 'Digital',
				'display': 'USB',
				'class': CategoryUSB,
				'compare': [1]
		},
		{
				'id': 'ethernet',
				'category': 'Digital',
				'display': 'Ethernet',
				'class': CategoryEthernet,
				'compare': [1, 2]
		},
		{
				'id': 'touchch',
				'category': 'HMI',
				'display': 'Touch Channels',
				'class': CategoryTouchChannel,
				'compare': [1]
		},
		{
				'id': 'lcd',
				'category': 'HMI',
				'display': 'Segment LCD',
				'class': CategorySegmentLCD,
				'compare': [1]
		},
		{
				'id': 'graph',
				'category': 'HMI',
				'display': 'Graphics Controller',
				'class': CategoryGraphicsController,
				'compare': [1]
		},
		{
				'id': 'camera',
				'category': 'HMI',
				'display': 'Camera',
				'class': CategoryCamera,
				'compare': [1]
		},
		{
				'id': 'crypto',
				'category': 'Security',
				'display': 'Cryptography',
				'class': CategoryCrypto,
				'compare': [1]
		},
		{
				'id': 'rng',
				'category': 'Security',
				'display': 'Random Number Gen.',
				'class': CategoryRNG,
				'compare': [1]
		},
		{
				'id': 'tamper',
				'category': 'Security',
				'display': 'Tamper',
				'class': CategoryTamper,
				'compare': [1]
		},
		{
				'id': 'ac',
				'category': 'Analog',
				'display': 'AC',
				'class': CategoryComparator,
				'compare': [1]
		},
		{
				'id': 'gain',
				'category': 'Analog',
				'display': 'Gain Stage',
				'class': CategoryOpAmp,
				'compare': [1]
		},
		{
				'id': 'adc',
				'category': 'Analog',
				'display': 'A/D',
				'class': CategoryADC,
				'units': ["xADC", "-ch", "-bit", "sps"],
				'compare': [500, 0, 1000, 0.1]
		},
		{
				'id': 'dac',
				'category': 'Analog',
				'display': 'D/A',
				'class': CategoryDAC,
				'units': ["xDAC", "-ch", "-bit", "sps"],
				'compare': [500, 0, 1000, 0.1]
		},
		{
				'id': 'io5v',
				'category': 'Supply',
				'display': '5V Tolerant I/O',
				'class': CategoryIO5VTolerant,
				'compare': [1]
		},
		{
				'id': 'iostrength',
				'category': 'Supply',
				'display': 'I/O Drive Strength',
				'description': 'Low level output current (usually noted IOL) until the low level output voltage reachs ~0.5V',
				'class': CategoryIOStrength,
				'units': ["A"],
				'compare': [1]
		},
		{
				'id': 'vmin',
				'category': 'Supply',
				'display': 'Vmin',
				'class': CategoryMinVoltage,
				'units': ["V"],
				'compare': [-1]
		},
		{
				'id': 'vmax',
				'category': 'Supply',
				'display': 'Vmax',
				'class': CategoryMaxVoltage,
				'units': ["V"],
				'compare': [1]
		},
		{
				'id': 'tmin',
				'category': 'Temperature',
				'display': 'Tmin',
				'class': CategoryMinTemperature,
				'units': ["&#8451;"],
				'compare': [-1]
		},
		{
				'id': 'tmax',
				'category': 'Temperature',
				'display': 'Tmax',
				'class': CategoryMaxTemperature,
				'units': ["&#8451;"],
				'compare': [1]
		},
		{
				'id': 'ccactive',
				'category': 'Active Mode',
				'display': 'Power Consumption',
				'class': CategoryCurrentActive,
				'units': ["A", "V", "&#8451;", "Hz", ""],
				'compare': [-1],
				'hide': True,
		},
		{
				'id': 'namesleepramrtc',
				'category': 'Sleep w/RAM+RTC',
				'display': 'Name',
				'class': CategoryNameSleepRAMRTC,
				'compare': [0],
				'hide': True,
		},
		{
				'id': 'wakeupsleepramrtc',
				'category': 'Sleep w/RAM+RTC',
				'display': 'Wake-up Time',
				'class': CategoryWakeUpTimeSleepRAMRTC,
				'units': ["s", "s"],
				'compare': [-1],
				'hide': True,
		},
		{
				'id': 'ccsleepramrtc',
				'category': 'Sleep w/RAM+RTC',
				'display': 'Power Consumption',
				'class': CategoryCurrentSleepRAMRTC,
				'units': ["A", "V", "&#8451;"],
				'compare': [-1],
				'hide': True,
		},
		{
				'id': 'namesleeprtc',
				'category': 'Sleep w/RTC',
				'display': 'Name',
				'class': CategoryNameSleepRTC,
				'compare': [0],
				'hide': True,
		},
		{
				'id': 'wakeupsleeprtc',
				'category': 'Sleep w/RTC',
				'display': 'Wake-up Time',
				'class': CategoryWakeUpTimeSleepRTC,
				'units': ["s", "s"],
				'compare': [-1],
				'hide': True,
		},
		{
				'id': 'ccsleeprtc',
				'category': 'Sleep w/RTC',
				'display': 'Power Consumption',
				'class': CategoryCurrentSleepRTC,
				'units': ["A", "V", "&#8451;"],
				'compare': [-1],
				'hide': True,
		},
		{
				'id': 'namesleepram',
				'category': 'Sleep w/RAM',
				'display': 'Name',
				'class': CategoryNameSleepRAM,
				'compare': [0],
				'hide': True,
		},
		{
				'id': 'wakeupsleepram',
				'category': 'Sleep w/RAM',
				'display': 'Wake-up Time',
				'class': CategoryWakeUpTimeSleepRAM,
				'units': ["s", "s"],
				'compare': [-1],
				'hide': True,
		},
		{
				'id': 'ccsleepram',
				'category': 'Sleep w/RAM',
				'display': 'Power Consumption',
				'class': CategoryCurrentSleepRAM,
				'units': ["A", "V", "&#8451;"],
				'compare': [-1],
				'hide': True,
		},
		{
				'id': 'namedeepsleep',
				'category': 'Deep Sleep',
				'display': 'Name',
				'class': CategoryNameDeepsleep,
				'compare': [0],
				'hide': True,
		},
		{
				'id': 'wakeupdeepsleep',
				'category': 'Deep Sleep',
				'display': 'Wake-up Time',
				'class': CategoryWakeUpTimeDeepsleep,
				'units': ["s", "s"],
				'compare': [-1],
				'hide': True,
		},
		{
				'id': 'ccdeepsleep',
				'category': 'Deep Sleep',
				'display': 'Power Consumption',
				'class': CategoryCurrentDeepsleep,
				'units': ["A", "V", "&#8451;"],
				'compare': [-1],
				'hide': True,
		},
		{
				'id': 'process',
				'display': 'Process',
				'class': CategoryProcess,
				'units': ["m"],
				'compare': [-1]
		},
		{
				'id': 'launch',
				'display': 'Launch Date',
				'class': CategoryLaunchDate,
				'compare': [1]
		},
		{
				'id': 'price',
				'display': 'Volume Price',
				'class': CategoryPricing,
				'units': ['', '', "U"],
				'compare': [-1, 0, 0]
		},
		{
				'id': 'packaging',
				'display': 'Packaging',
				'class': CategoryPackaging,
				'compare': [1]
		},
		{
				'id': 'pin',
				'display': 'Pin Count',
				'class': CategoryPin,
				'units': ['-pin']
		},
		{
				'id': 'packages',
				'display': 'Package(s)',
				'class': CategoryPackage,
				'units': ['', '', 'mm', 'mm', 'mm'],
				'compare': [-1, 0]
		},
		{
				'id': 'discovered',
				'display': 'Discovered',
				'class': CategoryDiscovered,
				'hide': True,
		},
		{
				'id': 'hidden',
				'display': 'Hidden',
				'class': CategoryHidden,
				'hide': True,
		},
	]
	if param == None:
		return parametric_categories
	for category in parametric_categories:
		if category["id"] == param:
			return category
	if strict:
		raise error("This key does not exists")
	return None

class Device(MCULibClass):
	category_device_name = "CategoryDeviceName"
	category_device_manufacturer = "CategoryDeviceManufacturer"
	category_device_family = "CategoryDeviceFamily"

	def __init__(self):
		self.categories = []

	def add_category(self, category, value = "", index = -1):
		"""
		Add a new category to a device and parse it.
		If the category already exists for this device, update only the
		value.
		"""
		if isinstance(category, str):
			category = eval(category)
		elif isinstance(category, GenericCategory):
			category = category.to_class()
		c = category(index)
		c.parse_string(value)
		if debug_trace_category and debug_trace_match(category.to_param()):
			self.debug("Value Identified: '%s' -> '%s'" % (str(value), str(c.get_value())), 0)
		self.categories.append(c)

	def merge_categories(self):
		"""
		This function will merge the sub-categories with their parents
		and remove them from the list.
		It will also merge multi-instance categories together.
		It will also create new categories if the parent category does
		not exist.
		"""
		for c in self.categories:

			# Ignore the category if it has the ignore attribute
			if getattr(c, "ignore", False):
				continue

			# Find the sub-categories
			if c.is_sub_category():
				is_match = False
				# Look for the parent category
				for parent_c in self.categories:
					if parent_c.__class__ == c.get_parent_category():
						c.merge_with_parent(parent_c)
						is_match = True
				# If there is no match, create a new category
				if not is_match:
					parent_class = c.get_parent_category()
					parent_c = parent_class()
					c.merge_with_parent(parent_c)
					self.categories.append(parent_c)
				# Delete the sub-category
				setattr(c, "ignore", True)

			# Find multi-instance categories
			if c.is_multi_instance():
				# Look if it can find multiple instances
				is_first = True
				for c_extra in self.categories:
					# Ignore the category if it has the ignore attribute
					if getattr(c_extra, "ignore", False):
						continue
					if c.to_param() == c_extra.to_param():
						# Skip the first one since it is same a 'c'
						if is_first:
							is_first = False
							continue
						c.merge(c_extra)
						setattr(c_extra, "ignore", True)

		# Clean the category list by removing the ingore attributes
		self.categories = [x for x in self.categories if not getattr(x, "ignore", False)]

	def get_device_name(self, strict = True, fullname = False):
		"""
		Return the name of the device
		"""
		c = self.get_device_category(self.category_device_name, strict)
		if c == None or c.get_value() == "":
			if strict:
				raise error("The device name is empty.")
			return None

		# If not the cullname is requested
		if fullname == False:
			return c.get_value()

		# Set the name
		name = [c.get_value()]

		# If the device has a CategoryAlias category, read it and append it to the name
		alias = self.get_device_category("CategoryAlias", strict = False)
		if alias:
			# Read the alias value
			alias_name = alias.get_value()
			# Update the name
			name = [alias_name, name[0]]

		return name

	def force_device_category(self, category_name, value):
		"""
		Force the value of a device category by erasing the exisitng ones and adding this new one
		"""
		# Erase the exisiting categories if any
		self.categories = [c for c in self.categories if c.__class__.__name__ != category_name]
		# Add the new one
		self.add_category(category_name, value)

	def get_device_manufacturer(self, strict = False):
		"""
		Return the manufacturer of the device
		"""
		c = self.get_device_category(self.category_device_manufacturer, strict)
		if c == None:
			return None
		return c.get_value()

	def get_device_family(self, strict = False):
		"""
		Return the family of the device
		"""
		c = self.get_device_category(self.category_device_family, strict)
		if c == None:
			return None
		return c.get_value()

	def get_device_category(self, category_name, strict = True):
		"""
		Return the category specified in parameter.
		If the "strict" is True and the category does not exists,
		the function will raise an error. It will return None otherwise.
		"""
		for category in self.get_device_categories():
			if category.__class__.__name__ == category_name:
				return category
		if strict:
			raise error("The category " + str(category_name) + " does not exists or its value is null.")
		return None

	def remove_device_category(self, category_name):
		"""
		This function removes a category from a device
		"""
		new_categories = []
		for category in self.categories:
			if category.__class__.__name__ != category_name:
				new_categories.append(category)
		self.categories = new_categories

	def get_device_categories(self):
		"""
		Return the category
		"""
		return self.categories

	def print_categories(self):
		"""
		Print the categories and the values that have changed for a specific
		device
		"""
		for c in self.categories:
			self.info(str(c.__class__.__name__) + ": " + str(c.get_value()), 3)
