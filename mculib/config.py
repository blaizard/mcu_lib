#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

# Global variable used to trace a value
debug_trace_category = None #"CategoryADC"

# --- Do not touch ----

import re

def debug_trace_match(category):
	if debug_trace_category == None:
		return False
	return re.match(debug_trace_category, str(category))
