#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from generic import *
from mculib.log import *
import re

class CategoryCPUCore(GenericCategory):
	config_group_master = True
	config_group_path = "common/cpu"
	config_translation_table = [
		[ r".*\b(cortex.*m0\+|cm0\+).*", "cortexm0+" ],
		[ r".*\b(cortex.*m0|cm0)\b.*", "cortexm0" ],
		[ r".*\b(cortex.*m3|cm3)\b.*", "cortexm3" ],
		[ r".*\b(cortex.*m4f|cm4f)\b.*", "cortexm4f" ],
		[ r".*\b(cortex.*m4|cm4)\b.*", "cortexm4" ],
		[ r".*\b(cortex.*m7|cm7)\b.*", "cortexm7" ],
		[ r".*\b(cortex.*r4|cr4)\b.*", "cortexr4" ],
		[ r".*\b(cortex.*r4f|cr4f)\b.*", "cortexr4f" ],
		[ r".*\b(cortex.*r5f|cr5f)\b.*", "cortexr5f" ],
		[ r".*\b(cortex.*a5|ca5)\b.*", "cortexa5" ],
		[ r".*\b(cortex.*a7|ca7)\b.*", "cortexa7" ],
		[ r".*\b(cortex.*a8|ca8)\b.*", "cortexa8" ],
		[ r".*\b(cortex.*a9|ca9)\b.*", "cortexa9" ],
		[ r".*\b(cortex.*a12|ca12)\b.*", "cortexa12" ],
		[ r".*\b(cortex.*a15|ca15)\b.*", "cortexa15" ],
		[ r".*\b(cortex.*a17|ca17)\b.*", "cortexa17" ],
		[ r".*\b(mips32.*m4k)\b.*", "mips32m4k" ],
		[ r".*\b(mips32.*m14k)\b.*", "mips32m14k" ],
		[ r".*\b(arm7tdmi)\b.*", "arm7tdmi" ],
		[ r".*\b(arm7ej)\b.*", "arm7ej" ],
		[ r".*\b(arm720t)\b.*", "arm720t" ],
		[ r".*\b(arm9tdmi)\b.*", "arm9tdmi" ],
		[ r".*\b(arm920)\b.*", "arm920" ],
		[ r".*\b(arm926ej)\b.*", "arm926ej" ],
		[ r".*\b(arm946e)\b.*", "arm946e" ],
		[ r".*\b(arm966e)\b.*", "arm966e" ],
		[ r".*\b(arm968e)\b.*", "arm968e" ],
		[ r".*\b(arm1136j)\b.*", "arm1136j" ],
		[ r".*\b(arm1156t2)\b.*", "arm1156t2" ],
		[ r".*\b(arm1176jz)\b.*", "arm1176jz" ],
		[ r".*\b(arm11mp)\b.*", "arm11mp" ],
		[ r".*\b(8032)\b.*", "8032" ],
		[ r".*\b(8051)\b.*", "8051" ],
		# Anything else is null
		[ r".*", "" ]
	]

	def get_category_regexpr(self):
		return r".*\b(core|cpu)\b.*"

	def get_category_regexpr_exclude(self):
		return [r".*\b(frequency|mhz|mips|speed|supply|volt|size|secondary)\b.*"]

class CategoryCPUCoreSecondary(GenericListCategory):
	config_translation_table = [[r"(-|n/a|0|none|no)", "-"]] + CategoryCPUCore.config_translation_table
	def get_category_regexpr(self):
		return r".*\b(secondary.*core)\b.*"

class CategoryFPU(GenericBinaryFeatureCategory):
	def get_category_regexpr(self):
		return r".*\b(fpu|floating\s*point\s*unit)\b.*"
	def get_feature_regexpr(self):
		return [[""]]

class CategoryDSP(GenericBinaryFeatureCategory):
	def get_category_regexpr(self):
		return r".*\b(dsp|digital\s*signal\s*processing)\b.*"
	def get_feature_regexpr(self):
		return [[""]]

class CategoryHWMul(GenericBinaryFeatureCategory):
	def get_category_regexpr(self):
		return r".*\b(hardware)\b\s+\b(multiplier)\b.*"
	def get_feature_regexpr(self):
		return [[""]]

class CategoryHWDiv(GenericBinaryFeatureCategory):
	def get_category_regexpr(self):
		return r".*\b(hardware)\b\s+\b(divider)\b.*"
	def get_feature_regexpr(self):
		return [[""]]

class CategoryCPUArchitecture(GenericMultiCategory):
	config_nb_values = 2
	config_group = CategoryCPUCore

	@classmethod
	def get_type(cls):
		return [
			cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE, # bits
			cls.TYPE_STRING                           # Architecture type
		]

	def parse(self, string):
		nb_bits = ""
		arch = ""

		nb_bits = self.parse_feature(string, ["bits", "bit", ""])

		if re.match(".*von.*neumann.*", string.lower()):
			arch = "von neumann"
		elif re.match(".*harvard.*", string.lower()):
			arch = "harvard"

		self.set_value(self.format_value([nb_bits, arch]))

class CategoryCPUSpeed(GenericCategory):

	@classmethod
	def get_type(cls):
		return [cls.TYPE_INTEGER | cls.TYPE_EXT_POSITIVE]

	def get_category_regexpr(self):
		return [r".*(cpu.*speed)(?!.*mips).*", r".*(operating.*frequency).*", r".*max.*speed", r".*fmax.*", r"^mhz$", r"^\s*(frequency)([\s\(\)]|mhz)*$"]

	def parse(self, string):
		cpuspeed = ""
		values = self.parse_format(string, ["@n0{x}"])
		if len(values) == 1:
			cpuspeed = values[0][0]
		self.set_value(self.format_value(cpuspeed))

class CategoryCPUPipeline(GenericFeatureCategory):
	config_group = CategoryCPUCore

	def get_feature_regexpr(self):
		return [["stage.*"]]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 30:
			return GenericCategory.ERROR
		return GenericCategory.PASS

class CategoryCPUInterruptLatency(GenericFeatureCategory):
	config_group = CategoryCPUCore

	def get_feature_regexpr(self):
		return [["cycle", "cy"]]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 10000:
			return GenericCategory.ERROR
		return GenericCategory.PASS

class CategoryCPUInterruptJitter(GenericFeatureCategory):
	config_group = CategoryCPUCore

	def get_feature_regexpr(self):
		return [["cycle", "cy"]]

	def sanity_check(self, value):
		nb = to_number(value)
		if nb and nb > 1000:
			return GenericCategory.ERROR
		return GenericCategory.PASS

class CategoryCPUBenchmark(GenericMultiListCategory):
	"""
	Record benchmarking data for this sepcific CPU
	"""
	config_nb_values = 4
	config_group = CategoryCPUCore

	@classmethod
	def get_type(cls):
		return [
			cls.TYPE_DECIMAL,                           # Score of this benchmark
			CategoryCPUBenchmarkUnit.get_type()[0],     # Bechmark score unit (cycles, dmips, coremark/mhz, ...)
			CategoryCPUBenchmarkType.get_type()[0],     # Bechmark type (coremark, aes encryption, ...)
			CategoryCPUBenchmarkCompiler.get_type()[0], # Compiler used to compile the code (iar v6.4, ...)
		]

	def parse(self, string):
		# Parse the string using a classic pattern
		(value_list, left_string) = self.parse_list(string, [ "@n0\s+", CategoryCPUBenchmarkUnit.config_translation_table, CategoryCPUBenchmarkType.config_translation_table, CategoryCPUBenchmarkCompiler.config_translation_table ])
		self.set_value(value_list)

class CategoryCPUBenchmarkUnit(GenericCategory):
	"""
	Define the unit of the benchmark
	"""
	config_translation_table = [
		[ r".*\b(cy).*(block)", "cycles/block" ],
		[ r".*\b(cy).*", "cycles" ],
		[ r".*\b(coremark.*mhz)\b", "coremark/mhz" ],
		[ r".*\b(dmips|dhrystone).*mhz.*", "dmips/mhz" ],
		[ r".*", "" ],
	]

class CategoryCPUBenchmarkType(GenericCategory):
	"""
	Define the benchmark used
	"""
	config_translation_table = [
		[ r".*(coremark).*", "coremark 1.0" ],
		[ r".*(dhrystone).*", "dhrystone" ],
		[ r".*(whetstone).*", "whetstone" ],
		[ r".*(128.*aes)|(aes.*128).*encrypt.*", "best software 128-bit aes encryption" ],
		[ r".*", "" ],
	]

class CategoryCPUBenchmarkCompiler(GenericCategory):
	"""
	Define the compiler used
	"""
	config_translation_table = [
		[ r".*(iar).*(arm).*(6.5).*", "iar ewarm v6.50" ],
		[ r".*(iar).*(arm).*(6.4).*", "iar ewarm v6.40" ],
		[ r".*(iar).*(arm).*(6.3).*", "iar ewarm v6.30" ],
		[ r".*(iar).*(arm).*(6.21).*", "iar ewarm v6.21" ],
		[ r".*(iar).*(arm).*(6.2).*", "iar ewarm v6.20" ],
		[ r".*(iar).*(arm).*(6.1).*", "iar ewarm v6.10" ],
		[ r".*(iar).*(arm).*(5.5).*", "iar ewarm v5.50" ],
		[ r".*(iar).*(arm).*(5.41).*", "iar ewarm v5.41" ],
		[ r".*(iar).*(arm).*(5.4).*", "iar ewarm v5.40" ],
		[ r".*(iar).*(arm).*(5.3).*", "iar ewarm v5.30" ],
		[ r".*(iar).*(avr32).*(3.31).*", "iar ewavr32 v3.31" ],
		[ r".*(iar).*(avr32).*(4.1).*", "iar ewavr32 v4.10" ],
		[ r".*(gcc).*(4.5.2).*", "gcc v4.5.2" ],
		[ r".*", "" ],
	]
