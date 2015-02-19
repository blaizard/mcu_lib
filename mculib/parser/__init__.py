#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

# Import the different parsers
from mculib.parser.generic import *
from mculib.parser.string import *
from mculib.parser.csv_parser import *

# Import the parser ports
from mculib.parser.port.microchip import *
from mculib.parser.port.st import *
from mculib.parser.port.freescale import *
from mculib.parser.port.ti import *
from mculib.parser.port.nxp import *
from mculib.parser.port.atmel import *
from mculib.parser.port.siliconlabs import *
from mculib.parser.port.renesas import *

# Imports the device parser ports
from mculib.parser.port.digikey import *
from mculib.parser.port.digikey_api import *

parser_ports_list = [
	{
		'common': MicrochipCommon,
		'specific': [MicrochipHTML] # Not maintained? , MicrochipProductSelectionTool]
	},
	{
		'common': STCommon,
		'specific': [ST]
	},
	{
		'common': FreescaleCommon,
		'specific': [FreescaleNewParametricSearch] #, FreescaleParametricSearch]
	},
	{
		'common': TICommon,
		'specific': [TI]
	},
	{
		'common': NXPCommon,
		'specific': [NXP]
	},
	{
		'common': AtmelCommon,
		'specific': [Atmel]
	},
	{
		'common': SiliconLabsCommon,
		'specific': [SiliconLabs]
	},
#	{
#		'common': RenesasCommon,
#		'specific': [Renesas]
#	},
]

device_parser_ports_list = [
	{
		'common': DigikeyCommon,
		'specific': [Digikey]
	}
]
