var category_list = [];

/* Format of data
 *	data = {
 *              'mcu_name1': {
 *                      'param_name1': [value, trustability, source, date, comment, options],
 *                      'param_name2': [value, trustability, source, date, comment, options],
 *                      ...
 *                      },
 *              'mcu_name2': {
 *                      ...
 *              },
 *              ...
 *      }
 */

/* Generate the value of the data with pre-filled arguments */
function parametric_data_create_value(value)
{
	var today = new Date();
	var dd = today.getDate();
	dd = (dd<10)?"0"+dd:dd;
	var mm = today.getMonth() + 1;
	mm = (mm<10)?"0"+mm:mm;
	var yyyy = today.getFullYear();
	return [value, 5, "custom", yyyy + "-" + mm + "-" + dd, ""];
}

/* This function is generating the mcu_data variable and the category_list */
function parametric_data_merge(data, new_data, new_category_list)
{
	mcu_data = {};

	/* Merge data */
	jQuery.extend(data, new_data);

	if (typeof new_category_list != "undefined") {
		/* Merge categories */
		for (var i in new_category_list) {
			param = new_category_list[i]["param"];
			/* Test if this param already exists in the current list */
			param_exists = false;
			for (var j in category_list) {
				if (category_list[j]["param"] == param) {
					param_exists = true;
					break;
				}
			}
			/* If it does not exists, add it */
			if (!param_exists) {
				category_list.splice(i, 0, new_category_list[i]);
			}
		}
	}

	return data;
}

function parametric_data_group(data)
{
	/* This function will be fed with a bunch of data and will group them */
	group_values = function(value_list) {
		/* Test if we are dealing with a multi-value */
		var stats = {
			'range': null, /* Value range, min and max*/
			'unquantified': 0, /* Number of unquantified values (yes) */
			'unknown': 0, /* Number of unknown values */
			'string_list': []
		};
		/* Make statistics about the values */
		for (var i in value_list) {
			var value = value_list[i];
			if (value == "no") {
				value = "0";
			}
			if (value == "") {
				stats['unknown']++;
			}
			else if (value == "yes") {
				stats['unquantified']++;
			}
			else if (!isNaN(value)) {
				value = parseFloat(value);
				if (!stats['range'])
					stats['range'] = [value, value];
				else if (stats['range'][0] > value)
					stats['range'][0] = value;
				else if (stats['range'][1] < value)
					stats['range'][1] = value;
			}
			else if (stats['string_list'].indexOf(value) == -1) {
				stats['string_list'].push(value);
			}
		}
		/* Process the columns */
		var value = "";
		var extra_options = { "prefix": "", "suffix": "", "range": false };
		/* If there is a string */
		if (stats['string_list'].length > 0) {
			if (stats['string_list'].length == 1 && !stats['range']) {
				value = stats['string_list'][0];
			}
			else {
				value = stats['string_list'].join("/");
				if (value.length > 24)
					value = value.substring(0, 23) + "&#8230;";
			}
		}
		/* If there is a number */
		else if (stats['range']) {
			if (stats['range'][0] == stats['range'][1]) {
				if (stats['range'][0] == "0" && (stats['unquantified']))
					value = "on some";
				else
					value = stats['range'][0].toString();
			}
			else {
				value = [ stats['range'][0].toString(), stats['range'][1].toString() ];
				extra_options["range"] = true;
			}
			if (stats['unquantified'] && value != "on some") {
				extra_options["suffix"] = " ?";
			}
		}
		/* If it is undefined and unquantified */
		else if (stats['unquantified']) {
			value = "yes";
		}

		if (stats['unknown'] && value != "" && value != "on some") {
			extra_options["suffix"] = " ?";
		}

		return [value, extra_options];
	}

	var group_data = {};
	var options = [];
	for (var j in category_list) {
		var param = category_list[j].param;
		var is_multi = category_list[j]['is_multi'];
		var is_list = category_list[j]['is_list'];
		var value_list = [[]];
		var output = [null, null];

		for (var i in data) {
			var value = "";
			if (data[i][param]) {
				value = data[i][param][0];
			}
			if (typeof value == "string") {
				/* Handle single value lists */
				value_list[0].push(value);
			}
			else if (typeof value == "object") {
				for (var k in value) {
					/* If it is a string */
					if (typeof value[k] == "string") {
						if (is_list)
							value_list[0].push(value[k]);
						else if (is_multi) {
							if (typeof value_list[k] == "undefined")
								value_list[k] = [];
							value_list[k].push(value[k]);
						}
					}
					/* We are handling a multi-value list */
					else {
						for (var l in value[k]) {
							if (typeof value_list[l] == "undefined")
								value_list[l] = [];
							value_list[l].push(value[k][l]);
						}
					}
				}
			}
		}
		value = [];
		options[j] = {};
		options[j]['range'] = [];
		options[j]['prefix'] = [];
		options[j]['suffix'] = [];
		for (var i in value_list) {
			output = group_values(value_list[i]);
			value.push(output[0]);
			options[j]['range'][i] = output[1]['range'];
			options[j]['prefix'][i] = output[1]['prefix'];
			options[j]['suffix'][i] = output[1]['suffix'];
			options[j].separator = {"list": "\n", "multi": "\n", "range": " to "};
		}

		/* Handle special cases for special formating */
		switch (param) {
		case 'name':
			var is_first = true;
			for (var device_name in data) {
				if (is_first) {
					value = device_name;
					is_first = false;
					continue;
				}
				for (var k in device_name) {
					k = parseInt(k);
					if (typeof value[k] == "undefined")
						continue;
					if (value[k] != device_name[k] && value[k] != "x")
						value = value.substr(0, k) + "x" + value.substr(k + 1);
				}
				value = value.substr(0, device_name.length);
			}
			value = (typeof value == "string")?value.replace(/[x]+$/, "x"):"";
			break;
		case 'package':
			options[j]['units'] = [" pins", ""];
			break;
		}
		/* If the value is mono value, then pop it from the array */
		if (value.length == 1) {
			value = value[0];
		}
		/* If the value is a list, add an array arround it */
		if (is_list) {
			value = [value];
		}
		/* Store the value */
		group_data[param] = [value, 5, "", "", "", options[j]];
	}

	/* Device name */
	var device_name = group_data["name"][0];
	var group = {};
	group[device_name] = group_data;

	return group;
}
