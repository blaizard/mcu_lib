function parametric_table_create_normal(container, data)
{
	var fct_active_data = function(voltage, code, data) {
		if (data["ccactive"]) {
			var current = "";
			var frequency = "";
			var comment = "";
			for (var i in data["ccactive"][0]) {
				/* Current, voltage, temperature, frequency, code type */
				var value = data["ccactive"][0][i];
				if (isNaN(parseFloat(value[0])) || !parseFloat(value[3]) || parseInt(value[1]) != voltage || value[4].toLowerCase() != code) {
					continue;
				}
				var temp = parseFloat(value[0]) / (parseFloat(value[3]) / 1000000);
				comment += ((comment)?"\n":"") + (temp*1000000).toFixed(0) + "µA/MHz @ " + (parseFloat(value[3])/1000000).toString() + "MHz";
				/* Keep only the best value */
				if (!current || parseFloat(current) > temp) {
					current = temp;
					frequency = parseFloat(value[3]);
				}
			}
			var new_value = parametric_data_create_value([current, ""]);
			new_value[4] = comment;
			return new_value;
		}
		return parametric_data_create_value(["", ""]);
	};

	var fct_sleep_data = function(param, temp_min, temp_max, data) {
		if (data[param]) {
			var current = "";
			var voltage = "";
			var comment = "";
			for (var i in data[param][0]) {
				/* Current, voltage, temperature */
				var value = data[param][0][i];
				/* Filter temperature data */
				if (isNaN(parseFloat(value[0])) || !parseFloat(value[2]) || parseFloat(value[2]) < temp_min || parseFloat(value[2]) > temp_max) {
					continue;
				}
				var temp = parseFloat(value[0]);
				comment += ((comment)?"\n":"") + (temp*1000000).toFixed(2) + "µA @ " + parseFloat(value[1]).toFixed(1) + "V";
				/* Keep only the best value */
				if (!current || parseFloat(current) > temp) {
					current = temp;
					voltage = parseFloat(value[1]);
				}
			}
			var new_value = parametric_data_create_value([current, ""]);
			new_value[4] = comment;

			return new_value;
		}
		return parametric_data_create_value(["", ""]);
	};

	var fct_active_submit = function(voltage, code, param, display_value, comment) {
		/* Parse the display value to extract the components */
		if (display_value) {
			param = "ccactive";
			display_value = display_value.replace(" @", ",") + ", " + voltage + "V, " + code;
		}
		return [param, display_value, comment];
	};

	var fct_sleep_submit = function(temperature, param, display_value, comment) {
		/* Parse the display value to extract the components */
		if (display_value) {
			display_value = display_value.replace(" @", ",") + ", " + temperature + "C";
		}
		return [param, display_value, comment];
	};

	var options = {
		'show_only': [
			'name', 'datasheet', 'manufacturer', 'topfamily', 'family',
			'cpu', 'cpu2', 'cpuspeed', 'cpuarch', 'dsp', 'fpu', 'hwmul', 'hwdiv', 'dma',
			'memflash', 'memfram', 'memsram', 'memeeprom', 'cache', 'dualbank',
			'reg', 'voltagescaling', 'por', 'bod', 'uniqueid',
			'wdt', 'rtc', 'pwm', '8bit', '16bit', '32bit',
			'tempsens',
			'io', 'crc', 'logic', 'usart', 'i2c', 'spi', 'qspi', 'lin', 'i2s', 'mci', 'ebi', 'can', 'usb', 'ethernet',
			'touchch', 'lcd', 'graph', 'camera',
			'crypto', 'rng', 'tamper',
			'ac', 'gain', 'adc', 'dac',
			'pin', 'io5v', 'iostrength', 'vmin', 'vmax', 'tmin', 'tmax', 'packages', 'launch',
		],
		'custom_category': [
		{
			"category": "Electrical",
			"name": "Deep Sleep<br/>@ 25&deg;C",
			"is_multi": true,
			"is_list": false,
			"nb_fields": 2,
			"param": "custom_deep_sleep",
			"units": ["A", "V"],
			"separator": {"multi": " @ "},
			"insert_after": "dac",
			"data": function(data) {
				return fct_sleep_data("ccdeepsleep", 20, 30, data);
			},
			"submit": function(param, display_value, comment) {
				return fct_sleep_submit("25", "ccdeepsleep", display_value, comment);
			},
		},
		{
			"category": "Electrical",
			"name": "Sleep w/RAM<br/>@ 85&deg;C<br/>(max)",
			"is_multi": true,
			"is_list": false,
			"nb_fields": 2,
			"param": "custom_sleep_ram85",
			"units": ["A", "V"],
			"info": "Maximal power consumption at 85&deg;C",
			"separator": {"multi": " @ "},
			"insert_after": "dac",
			"data": function(data) {
				return fct_sleep_data("ccsleepram", 80, 90, data);
			},
			"submit": function(param, display_value, comment) {
				return fct_sleep_submit("85", "ccsleepram", display_value, comment);
			},
		},
		{
			"category": "Electrical",
			"name": "Sleep w/RAM<br/>@ 25&deg;C",
			"is_multi": true,
			"is_list": false,
			"nb_fields": 2,
			"param": "custom_sleep_ram",
			"units": ["A", "V"],
			"separator": {"multi": " @ "},
			"insert_after": "dac",
			"data": function(data) {
				return fct_sleep_data("ccsleepram", 20, 30, data);
			},
			"submit": function(param, display_value, comment) {
				return fct_sleep_submit("25", "ccsleepram", display_value, comment);
			},
		},
		{
			"category": "Electrical",
			"name": "Sleep w/RTC<br/>@ 25&deg;C",
			"is_multi": true,
			"is_list": false,
			"nb_fields": 2,
			"param": "custom_sleep_rtc",
			"units": ["A", "V"],
			"separator": {"multi": " @ "},
			"insert_after": "dac",
			"data": function(data) {
				return fct_sleep_data("ccsleeprtc", 20, 30, data);
			},
			"submit": function(param, display_value, comment) {
				return fct_sleep_submit("25", "ccsleeprtc", display_value, comment);
			},
		},
		{
			"category": "Electrical",
			"name": "Sleep w/RTC+RAM<br/>@ 25&deg;C",
			"is_multi": true,
			"is_list": false,
			"nb_fields": 2,
			"param": "custom_sleep_rtcram",
			"units": ["A", "V"],
			"separator": {"multi": " @ "},
			"insert_after": "dac",
			"data": function(data) {
				return fct_sleep_data("ccsleepramrtc", 20, 30, data);
			},
			"submit": function(param, display_value, comment) {
				return fct_sleep_submit("25", "ccsleepramrtc", display_value, comment);
			},
		},
		{
			"category": "Electrical",
			"name": "Active ~while(1)<br/>@ 3V",
			"info": "Typical power consumption at room temperature, 3V and running a low processing code from non-volatile memory",
			"is_multi": true,
			"is_list": false,
			"nb_fields": 2,
			"param": "custom_active_while",
			"units": ["A/MHz", "Hz"],
			"separator": {"multi": " @ "},
			"insert_after": "dac",
			"data": function(data) {
				return fct_active_data(3, "while(1)", data);
			},
			"submit": function(param, display_value, comment) {
				return fct_active_submit("3", "while(1)", param, display_value, comment);
			},
		},
		{
			"category": "Electrical",
			"name": "Active ~CoreMark<br/>@ 3V",
			"info": "Typical power consumption at room temperature, 3V and running a high processing code from non-volatile memory",
			"is_multi": true,
			"is_list": false,
			"nb_fields": 2,
			"param": "custom_active_coremark",
			"units": ["A/MHz", "Hz"],
			"separator": {"multi": " @ "},
			"insert_after": "dac",
			"data": function(data) {
				return fct_active_data(3, "coremark", data);
			},
			"submit": function(param, display_value, comment) {
				return fct_active_submit("3", "coremark", param, display_value, comment);
			},
		}],
	};
	parametric_table_create(container, data, options);
}
