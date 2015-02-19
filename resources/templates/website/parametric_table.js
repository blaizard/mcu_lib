/* This assumes that category_list is global and filled */

/* Helper functions */
function parametric_table_get_container(object)
{
	if ($(object).hasClass("parametric_table")) {
		return $(object).get(0);
	}
	return $(object).parents(".parametric_table").get(0);
}
function parametric_table_get_real_table(object)
{
	return $(parametric_table_get_container(object)).find("table:not(.edit):last").get(0);
}
function parametric_table_get_header_table(object)
{
	return $(parametric_table_get_container(object)).find("table:nth(0)").get(0);
}
function parametric_table_get_filter_row(object)
{
	return $(parametric_table_get_header_table(object)).find("thead tr:nth-child(3)");
}
function parametric_table_get_filter_rows(object)
{
	return $(parametric_table_get_container(object)).find("thead tr:nth-child(3)");
}
function parametric_table_get_search_string(object)
{
	return $(parametric_table_get_container(object)).data('search_string');
}
function parametric_table_get_data(object)
{
	return $(parametric_table_get_container(object)).data('data');
}
function parametric_table_get_categories(object)
{
	return $(parametric_table_get_container(object)).data('categories');
}
function parametric_table_get_selection(object)
{
	return $(parametric_table_get_real_table(object)).children("tbody").find("tr.selected");
}

/* Selection */
function parametric_table_show_selection(selection)
{
	$(parametric_table_get_real_table(selection)).find("tbody tr").hide();
	$(selection).show();
	parametric_table_resize_columns(selection);
}

function parametric_table_selection_to_data(row_selector)
{
	var new_data = {};
	var data = parametric_table_get_data(row_selector);
	$(row_selector).each(function() {
		if (typeof data[$(this).attr("reference")] == "undefined") {
			alert("parametric_table_selection_to_data\nUnable to locate reference `" + $(this).attr("reference") + "' inside the data");
		}
		if ($(this).attr("reference")) {
			new_data[$(this).attr("reference")] = data[$(this).attr("reference")];
		}
	});
	return new_data;
}

/* parametric_data_get_xx_from_cell */
function parametric_table_get_category_from_cell(cell)
{
	cell = $(cell).get(0);
	var category_index = null;
	/* If this is a vertical table */
	if ($(cell).attr("vertical")) {
		category_index = $(cell).parent("tr").attr("category_index");
	}
	else {
		category_index = cell.cellIndex;
	}
	var categories = parametric_table_get_categories(cell);
	if (typeof categories[category_index] == "undefined") {
		alert("The index is out of bound, this should never happen.");
		return null;
	}
	return categories[category_index];
}
function parametric_table_get_reference_from_row(row)
{
	return parametric_table_get_reference_from_cell($(row).find("td").get(0));
}
function parametric_table_get_reference_from_cell(cell)
{
	cell = $(cell).get(0);
	var reference = null;
	if ($(cell).attr("vertical")) {
		/* If this is a vertical table */
		var index = cell.cellIndex;
		var elt = $(cell).parents("tbody:first").find("tr:first").find("td").get(index);
		reference = $(elt).attr("reference");
	}
	else {
		reference = $(cell).parent("tr").attr("reference");
	}
	if (!reference) {
		alert("Reference unidentifiable (parametric_table_get_reference_from_cell).");
		return;
	}
	return reference;
}
function parametric_table_get_display_value_from_cell(cell, temporary)
{
	/* temporary - if it will store this value in the temporary data */
	if (typeof temporary == "undefined") {
		alert("Temporary attribute must be defined"); return;
	}

	var value = parametric_table_get_value_from_cell(cell, temporary);
	var category = parametric_table_get_category_from_cell(cell);
	return parametric_table_format_cell("", value, category);
}
function parametric_table_get_comment_from_cell(cell, temporary)
{
	cell = $(cell).get(0);
	var reference = parametric_table_get_reference_from_cell(cell);
	var category = parametric_table_get_category_from_cell(cell);
	var param = category["param"];
	var comment = "";

	if (temporary) {
		/* Special case, if this is the edited cell */
		if ($(cell).hasClass("editmode")) {
			comment = $(cell).find("textarea.comment").val();
		}
		else if ($(cell).data("comment")) {
			comment = clone($(cell).data("comment"));
		}
	}
	else {
		var data = parametric_table_get_data(cell);
		if (typeof data[reference] == "undefined") {
			alert("Unknown device, this should never happend.");
		}
		else if (typeof data[reference][param] == "object" && data[reference][param][4]) {
			comment = clone(data[reference][param][4]);
		}
	}
	/* Encode the comment */
	return cdecode(comment);
}
function parametric_table_get_value_from_cell(cell, temporary)
{
	/* temporary - if it will store this value in the temporary data */
	if (typeof temporary == "undefined") {
		alert("Temporary attribute must be defined"); return;
	}

	cell = $(cell).get(0);
	var reference = parametric_table_get_reference_from_cell(cell);
	var category = parametric_table_get_category_from_cell(cell);
	var param = category["param"];

	if (temporary) {
		/* Special case, if this is the edited cell */
		if ($(cell).hasClass("editmode")) {
			/* re-build the value */
			var value = [];
			$(cell).find("tr.edit").each(function() {
				var sub_value = []
				$(this).find("input.edit").each(function() {
					sub_value.push($(this).val());
				});
				value.push(sub_value);
			});
			if (!category["is_list"] && value.length == 1) value = value[0];
			if (!category["is_multi"] && value.length == 1) value = value[0];
			return value;
		}
		else {
			return clone($(cell).data("value"));
		}
	}

	var data = parametric_table_get_data(cell);
	if (typeof data[reference] == "undefined") {
		alert("Unknown device, this should never happend.");
		return;
	}
	if (typeof data[reference][param] == "undefined") {
		return "";
	}
	return clone(data[reference][param][0]);
}

function parametric_table_contextmenu_init(object)
{
	parametric_table_contextmenu_init.same_action = function(object, title, body, param_id) {
		/* Create and open the dialog box */
		var selection = parametric_table_get_selection(object);
		if (selection.length < 2) {
			alert("You must select at least 2 devices.");
			return;
		}
		var device_list = new Array();
		$(selection).each(function() {
			device_list.push(parametric_table_get_reference_from_row(this));
		});
		prompt(title, body + "<br /><br />" + device_list.join(", "), function() {
			commit(null, param_id, null, null, null, device_list);
			/* Update the table dimensions */
			parametric_table_resize_columns(object);
		});
	};

	var menu = [
		{'Group': function(menuItem, menu) {
			parametric_table_group_selection(object);
		}},
		{'Display Similar Device(s)': function(menuItem, menu) {
			parametric_table_select_similar_selection(object);
		}},
		$.contextMenu.separator,
		{'Show All': function(menuItem, menu) {
			parametric_table_select_all(object);
			$(parametric_table_get_selection(object)).show();
			/* Update the table dimensions */
			parametric_table_resize_columns(object);
		}},
		{'Show Selected': function(menuItem, menu) {
			var selection = parametric_table_get_selection(object);
			parametric_table_select_all(object);
			$(parametric_table_get_selection(object)).hide();
			$(selection).show();
			/* Update the table dimensions */
			parametric_table_resize_columns(object);
		}},
		$.contextMenu.separator,
		{'Rename/Merge Device(s)': function(menuItem, menu) {
			/* Create and open the dialog box */
			var selection = parametric_table_get_selection(object);
			var desc = "Rename and merge the " + selection.length + " selected devices";
			var device_name = parametric_table_get_reference_from_row($(selection).get(0));
			if (selection.length == 1) {
				desc = "Rename `" + device_name + "'";
			}
			prompt("Rename/Merge Device(s)", desc + "<br/>New name: <input type=\"text\" value=\"" + device_name + "\"/>", function() {
				var new_name = $("#id_prompt input").val();
				$(selection).each(function() {
					var device_name = parametric_table_get_reference_from_row(this);
					parametric_table_set_reference_to_row(this, new_name, new_name);
					commit(device_name, null, null, null, new_name);
				});
				/* Update the table dimensions */
				parametric_table_resize_columns(object);
			});
		}},
		{'Same Die': function(menuItem, menu) {
			parametric_table_contextmenu_init.same_action(object, "Same Die", "Do you confirm that the following devices share the same die?", "dieid");

		}},
		{'Same CPU': function(menuItem, menu) {
			parametric_table_contextmenu_init.same_action(object, "Same CPU", "Do you confirm that the following devices share the same CPU?", "cpu");

		}},
		{'Delete': function(menuItem, menu) {
			/* Create and open the dialog box */
			var device_name = parametric_table_get_reference_from_cell(this);
			prompt("Delete", "Are you sure you want to delete this device `<b>" + device_name + "</b>' ?", function() {
				/* Update the table dimensions */
				parametric_table_resize_columns(object);
			});
		}},
		$.contextMenu.separator,
	];
	cmenu = $(parametric_table_get_real_table(object)).contextMenu(menu, {
		theme: 'vista',
		show: function(t, e) {
			if (parametric_table_get_selection(object).length < 2) {
				parametric_table_on_click(e);
			}
			$.contextMenu.show.call(this, t, e);
		},
	});
}

function parametric_table_select_similar_selection(object)
{
	var param_criteria = [
		{"param": "memflash", "pos": 0, "tolerance": "0.1"},
		{"param": "memsram", "pos": 0, "tolerance": "0.1"},
		{"param": "usart", "pos": 0, "tolerance": "0.9"},
		{"param": "i2c", "pos": 0, "tolerance": "0.9"},
		{"param": "spi", "pos": 0, "tolerance": "0.9"}
	];

	var data = parametric_table_selection_to_data(parametric_table_get_selection(object));
	for (var i in data) { data = data[i]; break; }
	var query = [];

	for (var i in param_criteria) {
		if (typeof data[param_criteria[i].param] == "undefined") {
			break;
		}
		var item = {
			'param': param_criteria[i].param + param_criteria[i].pos,
			'value': data[param_criteria[i].param][0],
			'tolerance': param_criteria[i].tolerance,
		};
		query.push(item);
	}

	/* Apply the range values */
	for (var i in query) {
		if (typeof query[i].tolerance != "undefined" && typeof query[i].value != "undefined") {
			query[i].min_value = parseFloat(query[i].value) - (parseFloat(query[i].value) * parseFloat(query[i].tolerance));
			query[i].max_value = parseFloat(query[i].value) + (parseFloat(query[i].value) * parseFloat(query[i].tolerance));
		}
		if (typeof query[i].min_value != "undefined" || typeof query[i].max_value != "undefined") {
			var value = [];
			var min_value = (typeof query[i].min_value == "undefined")?-9999999999:parseFloat(query[i].min_value);
			var max_value = (typeof query[i].max_value == "undefined")?9999999999:parseFloat(query[i].max_value);
			$(parametric_table_get_filter_row(object)).find("select[name=" + query[i].param + "] > option").each(function() {
				if (parseFloat($(this).val()) >= min_value) {
					if (parseFloat($(this).val()) > max_value) {
						return false;
					}
					value.push($(this).val());
				}
			});
			query[i].value = value;
		}
	}

	var selection = parametric_table_search_devices(object, query);
	parametric_table_show_selection(selection);
}

function parametric_table_group_selection(object)
{
	var data = parametric_table_selection_to_data(parametric_table_get_selection(object));
	var group_data = parametric_data_group(data);
	/* Merge the group to the parametric data */
	mcu_data = parametric_data_merge(mcu_data, group_data);

	/* Print the new group */
	for (var device_name in group_data) {
		parametric_table_add_entry(object, device_name, group_data[device_name],
				parametric_table_get_categories(object),
				$(parametric_table_get_selection(object)).first(),
				"group");
	}

	/* Update the table dimensions */
	parametric_table_resize_columns(object);
}

function parametric_table_generate_search_string(data, category)
{
	/* Search string has the following format:
	 * @MCU_NAME@|PARAM_NAME0|VALUE||PARAM_NAME1|VALUE|...
	 */
	var search_string = "";

	for (var mcu_name in data) {
		var mcu = data[mcu_name];
		/* Update the search string */
		search_string += "@" + mcu_name + "@";
		/* List all values order is important */
		for (var i in category) {
			var param = category[i].param;
			var value = mcu[param];
			if (typeof value == "undefined") {
				continue;
			}
			/* Read the value */
			value = value[0];
			value = ((category[i].is_list)?value:[value]);
			value = ((category[i].is_multi)?value:[value]);
			for (var j in value) {
				for (var k in value[j]) {
					if (value[j][k]) {
						search_string += "|" + param + k + "|" + value[j][k] + "|";
					}
				}
			}
		}
	}

	return search_string;
}

function parametric_table_tooltip(message, object, event)
{
	var x = 0;
	var y = 0;

	/* Initialize the container */
	if (typeof parametric_table_tooltip.container == "undefined") {
		parametric_table_tooltip.container = document.createElement("div");
		$(parametric_table_tooltip.container).css("position", "absolute");
		$(parametric_table_tooltip.container).css("white-space", "pre-wrap");
		$(parametric_table_tooltip.container).addClass("tooltip");
		$(parametric_table_tooltip.container).mouseover(function() {
			$(this).hide();
		});
		$('body').append(parametric_table_tooltip.container);
		$(parametric_table_tooltip.container).hide();
	}

	/* Bind the mouseout event to this object */
	$(object).on('mouseout', function() {
		if (parametric_table_tooltip.timeout) {
			clearTimeout(parametric_table_tooltip.timeout);
			parametric_table_tooltip.timeout = null;
		}
		$(parametric_table_tooltip.container).hide();
	});

	/* Show the message after a certain time of inactivity */
	if (parametric_table_tooltip.timeout) {
		clearTimeout(parametric_table_tooltip.timeout);
		parametric_table_tooltip.timeout = null;
	}
	parametric_table_tooltip.timeout = setTimeout(function() {
		parametric_table_tooltip.timeout = null;
		$(parametric_table_tooltip.container).show();
	}, 500);

	/* Position the container */
	if (typeof event != "undefined") {
		x = event.pageX;
		y = event.pageY + 10;
	}
	$(parametric_table_tooltip.container).css('top', y + "px");
	$(parametric_table_tooltip.container).css('left', x + "px");

	/* Update the message */
	$(parametric_table_tooltip.container).text(message);
}

function parametric_table_format_data(device_name, parametric, categories)
{
	if (typeof parametric_table_format_data.tooltip == "undefined") {
		parametric_table_format_data.tooltip = function(e, cell) {
			var event = e || window.event;
			var display_comment = parametric_table_get_comment_from_cell(cell, false);
			if ($(cell).attr("source")) {
				display_comment += ((display_comment)?"\n":"") + "Source: " + $(cell).attr("source");
			}
			if ($(cell).attr("updated")) {
				display_comment += ((display_comment)?"\n":"") + "Updated: " + $(cell).attr("updated");
			}
			parametric_table_tooltip(display_comment, cell, event);
		}
	}

	var data = [];
	for (var j in categories) {
		var param = categories[j].param;
		var item = {
			'class': "",
			'value': ""
		};
		var value = "";
		var options = undefined;
		if (parametric[param]) {
			if (typeof parametric[param][5] != "undefined") {
				options = parametric[param][5];
			}
			value = parametric[param][0];
			item['class'] += " trustabilty_" + parametric[param][1];
			if (parametric[param][2]) {
				item['source'] = parametric[param][2];
			}
			if (parametric[param][3]) {
				item['updated'] = parametric[param][3];
			}
			if (parametric[param][4]) {
				item['comment'] = parametric[param][4];
				item['class'] += " comment";
			}
			item['onmouseover'] = "javascript:parametric_table_format_data.tooltip(event, this);";
		}
		value = parametric_table_format_cell(device_name, value, categories[j], options);
		item["value"] = value;
		if (parametric_table_format_cell.original) {
			item["original"] = parametric_table_format_cell.original;
		}
		data.push(item);
	}
	return data;
}

function parametric_table_format_cell(device_name, value, category, options)
{
	var param = category.param;

	/* Unset the original value for this cell */
	parametric_table_format_cell.original = undefined;

	/* Merge category with the one passed in argument */
	if (typeof options != "undefined") {
		for (var k in options) {
			category[k] = options[k];
		}
	}

	/* Handle special formating for specific categories */
	switch (param) {
	case "name":
		if (!value) {
			value = device_name;
		}
		break;
	case "package":
		category.separator = {"list": "; ", "multi": "-", "range": " to "};
		break;
	case "ccactive":
		/* Find the min/max of the power consumption */
		if (value && value.length) {
			/* Create the original value */
			var original_value = parametric_table_format_value(value, category);
			parametric_table_format_cell.original = original_value;
			/* Create a display value */
			var min = Number.MAX_VALUE;
			var max = 0;
			for (var i in value) {
				/* Get the number of A / Mhz for each value */
				var v = value[i];
				var cc = parseFloat(v[0]);
				if (v[1] && parseFloat(v[1])) {
					cc = cc / (parseFloat(v[1]) / 1000000);
				}
				min = Math.min(min, cc);
				max = Math.max(max, cc);
			}
		//	value = min //[min, max];
		//	category = new Array();
		//	category['units'] = ["A/MHz"];
		}
		break;
	case "ccsleeprtc":
	case "ccsleepram":
	case "ccdeepsleep":
		/* Find the min/max of the power consumption */
		if (value && value.length) {
			/* Create the original value */
			var original_value = parametric_table_format_value(value, category);
			parametric_table_format_cell.original = original_value;
			/* Create a display value */
			var min = Number.MAX_VALUE;
			var max = 0;
			for (var i in value) {
				var v = value[i];
				var cc = parseFloat(v[0]);
				min = Math.min(min, cc);
				max = Math.max(max, cc);
			}
			value = min; //[min, max];
			category = new Array();
		//	category['range'] = [true];
			category['units'] = ["A"];
		}
		break;
	case "wakeupsleeprtc":
	case "wakeupsleepram":
	case "wakeupdeepsleep":
		/* Find the min/max of the power consumption */
		if (value && value.length) {
			/* Create the original value */
			var original_value = parametric_table_format_value(value, category);
			parametric_table_format_cell.original = original_value;
			/* Create a display value */
			var min = Number.MAX_VALUE;
			var max = 0;
			for (var i in value) {
				var time = parseFloat(value[i]);
				min = Math.min(min, time);
				max = Math.max(max, time);
			}
			value = min; //[min, max];
			category = new Array();
		//	category['range'] = [true];
			category['units'] = ["s"];
		}
		break;
	}

	value = parametric_table_format_value(value, category);

	/* Special case */
	switch (param) {
	case "datasheet":
		var url_pattern = new RegExp("(http|ftp|https)://");
		if (url_pattern.test(value)) {
			value = "<a href=\"" + value + "\" target=\"_blank\"><img src=\"datasheet.gif\"/></a>";
		}
		break;
	}

	if (typeof value != "undefined") {
		return value;
	}
	return "";
}

function parametric_table_format_value(value, options, counter, previous_state, multivalue_index)
{
	/* Declare formating functions */
	if (typeof parametric_table_format_value.value_type == "undefined") {
		parametric_table_format_value.value_type = function(value, options, counter) {
			if (counter == 0) {
				if (options.is_list) return "list";
				if (options.is_multi) return "multi";
				if (typeof value == "object") return "range";
			}
			if (counter == 1) {
				if (options.is_list && options.is_multi) return "multi";
				if (typeof value == "object") return "range";
			}
			if (counter == 2) {
				if (typeof value == "object") return "range";
			}
			return "value";
		}
		parametric_table_format_value.round = function(value) {
			if (value < 2048)
				return Math.round(value * 100) / 100;
			else
				return Math.round(value * 10) / 10;
		}
		parametric_table_format_value.get = function(type, options, multivalue_index) {
			if (typeof options[type] == "undefined")
				return "";
			if (typeof options[type][multivalue_index] == "undefined")
				return "";
			if (!options[type][multivalue_index])
				return "";
			return options[type][multivalue_index];
		}
	}

	/* 1rst time it has been called, counter is the recursion counter */
	if (typeof counter == "undefined") {
		counter = -1;
		value_level = false;
		previous_state = "";
		multivalue_index = 0;
		if (typeof options.separator == "undefined") {
			options.separator = {"list": "; ", "multi": ", ", "range": " to "};
		}
	}
	counter++;

	/* Main state machine */
	var string = "";
	var state = parametric_table_format_value.value_type(value, options, counter);
	switch (state) {
	case "list":
	case "multi":
		multivalue_index = 0;
	case "range":
		var sub_string = new Array();
		for (var i in value) {
			var new_value = parametric_table_format_value(value[i], options, counter, state, multivalue_index);
			if (new_value) {
				sub_string.push(new_value);
			}
			if (state == "multi") {
				multivalue_index++;
			}
		}
		string = sub_string.join(options.separator[state]);
		break;
	case "value":
		/* Check if the value is a number, if so format it if needed */
		var is_decimal_re = /^\s*(\+|-)?((\d+(\.\d+)?)|(\.\d+))\s*$/;
		if (typeof value == "number" || (typeof value == "string" && value.search(is_decimal_re) != -1)) {
			/* If there is a unit for this */
			if (parametric_table_format_value.get("units", options, multivalue_index)) {
				var number = parseFloat(value);
				var sign = ((number < 0)?"-":"");
				number = Math.abs(number);
				/* Handle specific cases, bytes */
				if (parametric_table_format_value.get("units", options, multivalue_index).match(/\b(b|byte|bytes)\b/i)) {
					if (number >= 512 * 1024)
						value = sign + parametric_table_format_value.round(number / (1024 * 1024)) + "M";
					else if (number >= 512)
						value = sign + parametric_table_format_value.round(number / 1024) + "k";
				}
				else {
					if (number >= 1000000)
						value = sign + parametric_table_format_value.round(number / 1000000) + "M";
					else if (number >= 1000)
						value = sign + parametric_table_format_value.round(number / 1000) + "k";
					else if (number && number < 0.000001)
						value = sign + parametric_table_format_value.round(number * 1000000000) + "n";
					else if (number && number < 0.0001)
						value = sign + parametric_table_format_value.round(number * 1000000) + "&micro;";
					else if (number && number < 1)
						value = sign + parametric_table_format_value.round(number * 1000) + "m";
				}
			}
		}
		string = value.toString();

		break;
	}

	/* Add the units */
	if (string && ((state == "value" && previous_state != "range") || (state == "range"))) {
		if (string != "0" && parametric_table_format_value.get("units", options, multivalue_index)) {
			string += parametric_table_format_value.get("units", options, multivalue_index);
		}
		if (parametric_table_format_value.get("prefix", options, multivalue_index)) {
			string = parametric_table_format_value.get("prefix", options, multivalue_index) + string;
		}
		if (parametric_table_format_value.get("suffix", options, multivalue_index)) {
			string += parametric_table_format_value.get("suffix", options, multivalue_index);
		}
	}

	return string;
}

function parametric_table_add_entry(object, name, raw_data, categories, extra_pos, extra_class)
{
	/* extra_pos is the position where this entry should be in the table
	 * extra_class is a class added to the entry
	 */
	var data = parametric_table_format_data(name, raw_data, categories);
	var tr = document.createElement("tr");
	for (var i in data) {
		var td = document.createElement("td");
		for (var attr_name in data[i]) {
			$(td).attr(attr_name, data[i][attr_name]);
		}
		$(td).html(data[i]["value"]);
		$(tr).append(td);
	}
	/* Store the reference of the object */
	$(tr).attr("reference", name);
	/* Add the class */
	if (typeof extra_class != "undefined") {
		$(tr).addClass(extra_class);
	}
	/* Add the entry to the table */
	if (typeof extra_pos != "undefined") {
		$(tr).insertBefore(extra_pos);
	}
	else {
		$(parametric_table_get_real_table(object)).append(tr);
	}
}

function parametric_table_create_filter(data, categories)
{
	/* Generate the filter row */
	row = "<tr><td class=\"header\"><a onclick=\"javascript:parametric_table_toggle_filters(this);\">[Hide]</a></td>";
	for (var j in categories) {
		/* Remove the first element (the devices) */
		if (j == 0) {
			continue;
		}
		/* Check the type of category */
		var category_is_list = false;
		if (typeof categories[j].is_list != "undefined") {
			category_is_list = categories[j].is_list;
		}
		var category_is_multi = false;
		if (typeof categories[j].is_multi != "undefined") {
			category_is_multi = categories[j].is_multi;
		}

		row += "<td class=\"header\">";

		var category = categories[j];
		var param = category.param;
		var values = new Array();
		/* List all the uniq values for the filtering */
		for (var i in data) {
			/* Read the value for this category */
			if (!data[i][param]) {
				continue;
			}
			value_list = data[i][param][0];
			/* Cast the value as a list, so that we can use the same code snippet */
			if (!category_is_list) {
				value_list = [value_list];
			}
			/* List all the values */
			for (var k in value_list) {
				/* Cast the value into a multi value element, for the same reason as above: re-use of the same code */
				value_multi = value_list[k];
				if (typeof value_multi != "object") {
					value_multi = [value_multi];
				}
				/* List all individual values */
				for (l in value_multi) {
					value = value_multi[l];
					if (typeof values[l] == "undefined") {
						values[l] = new Array();
					}
					if (value && values[l].indexOf(value) == -1) {
						values[l].push(value);
					}
				}
			}
		}

		/* Sort the arrays and print them */
		for (var l in values) {
			/* If this array is empty, pass */
			if (!values[l].length) {
				continue;
			}
			/* Sort the values */
			values[l].sort(function(a, b) {
				/* Convert the arguments to numbers if it can */
				var regexpr_n = /^-{0,1}\d+[\.,]{0,1}\d*/;
				var a_n = regexpr_n.exec(a.toString());
				a_n = ((a_n)?parseFloat(a_n):null);
				var b_n = regexpr_n.exec(b.toString());
				b_n = ((b_n)?parseFloat(b_n):null);

				if (typeof a_n == "number" && typeof b_n == "number") {
					return a_n - b_n;
				}
				if (typeof a_n == "number") {
					return 1;
				}
				if (typeof b_n == "number") {
					return -1;
				}
				a = a.toLowerCase();
				b = b.toLowerCase();
				return a < b ? -1 : a > b ? 1 : 0;
			});

			/* Build the options */
			var options = {};
			if (typeof category["units"] != "undefined" && typeof category["units"][l] != "undefined") {
				options["units"] = [category["units"][l]];
			}

			row += "<select class=\"loading_trigger\" multiple=\"multiple\" name=\"" + param + l + "\" onchange=\"javascript:parametric_table_apply_filters(this);\">";
			for (var i in values[l]) {
				display_value = parametric_table_format_value(values[l][i], options);
				row += "<option value=\"" + values[l][i] + "\">" + display_value + "</option>";
			}
			row += "</select>";
		}

		row += "</td>";
	}
	row += "</tr>";

	/* The filters show/hide row */
	row += "<tr>";
	row += "<td class=\"filter_toggle\" onclick=\"javascript:parametric_table_toggle_filters(this);\" colspan=\"" + categories.length + "\">&nbsp;</td>";
	row += "</tr>";

	return row;
}

function parametric_table_search_devices(object, query)
{
	/* Build the query string */
	var param_regexpr = "";
	for (var i in query) {
		if (query[i]["value"]) {
			var value_string = query[i]["value"].toString();
			value_string = value_string.replace("+", "\\+");
			param_regexpr += "[^@]*\\|";
			param_regexpr += query[i]["param"];
			param_regexpr += "\\|(";
			param_regexpr += value_string.split(",").join("|");
			param_regexpr += ")\\|";
		}
	};

	/* Parse a string with the following format:
	@reference@|paramindex|value||paramindex|value||paramindex|value|
	*/
	var rx = new RegExp("@([^@]*)@" + param_regexpr, "g");
	var selection = $();
	var search_string = parametric_table_get_search_string(object);
	var real_table = parametric_table_get_real_table(object);
	while (result = rx.exec(search_string)) {
		selection = $(selection).add($(real_table).find("tbody tr[reference=\"" + result[1] + "\"]"));
	}

	return selection;
}

function parametric_table_apply_filters(object)
{
	/* List all the active filters */
	var query = [];
	$(parametric_table_get_filter_row(object)).find("select").each(function() {
		if ($(this).val()) {
			query.push({
				'param': $(this).attr("name"),
				'value': $(this).val()
			});
		}
	});

	var selection = parametric_table_search_devices(object, query);
	parametric_table_show_selection(selection);
}

function parametric_table_toggle_filters(cell)
{
	var container = parametric_table_get_container(cell);
	var filter_rows = $(container).find("table thead tr:nth-child(3)");
	$(filter_rows).toggle(0, function() {
		parametric_table_resize_columns(container);
	});
}

function parametric_table_options_setup(options)
{
	default_options = {
		/* A list of the category params to be listed, if null, everything is displayed */
		'show_only': null,
		/* Filtering row */
		'enable_filtering': true,
		/* Selection */
		'enable_selection': true,
		/* Enable the context menu */
		'enable_contextmenu': true,
		/* Sorting method */
		'sort': ['manufacturer', 'topfamily', 'family', 'name'],
		/* Define custom categories */
		'custom_category': [],
	};
	for (var i in options) {
		default_options[i] = options[i];
	}
	return default_options;
}

function parametric_table_unselect_all(object)
{
	var real_table = parametric_table_get_real_table(object);
	$(real_table).children("tbody").find("tr").removeClass("selected");
}

function parametric_table_select_all(object)
{
	var real_table = parametric_table_get_real_table(object);
	$(real_table).children("tbody").find("tr").filter(':visible').addClass("selected");
}

function parametric_table_get_selection(object)
{
	var real_table = parametric_table_get_real_table(object);
	return $(real_table).children("tbody").find("tr.selected").filter(':visible');
}

function parametric_table_select_row(row)
{
	$(row).addClass("selected");
}

function parametric_table_toggle_row_selection(row)
{
	if ($(row).hasClass("selected")) {
		$(row).removeClass("selected");
	}
	else {
		$(row).addClass("selected");
	}
}

function parametric_table_enable_selection(container)
{
	if (typeof parametric_table_enable_selection.get_tr_row == "undefined") {
		parametric_table_enable_selection.get_tr_row = function(tr_selector) {
			return parseInt($(tr_selector).parent().children().index($(tr_selector)));
		}

		parametric_table_enable_selection.previous_selection_row = 0;
		parametric_table_enable_selection.timeout = null;

		parametric_table_enable_selection.click = function(cell, is_shift_key, is_ctrl_key) {
			var selector_list = $(cell);
			var container = parametric_table_get_container(cell);

			/* Remove all the similarities */
			//clear_similarities();

			/* Clear the previous selection unless shift or ctrl are pressed */
			if (!is_shift_key && !is_ctrl_key) {
				parametric_table_unselect_all(container);
			}

			if (is_shift_key) {
				var current_row = parametric_table_enable_selection.get_tr_row(cell);
				var current_selection = parametric_table_get_selection(container);
				/* If no previous selection - Select everything from the begining to the cursor */
				if (current_selection.length == 0) {
					selector_list = $(container).find("table").children("tbody").find("tr").slice(0, current_row + 1);
				}
				else {
					var min_selection_row = parametric_table_enable_selection.get_tr_row(current_selection[0]);
					var max_selection_row = parametric_table_enable_selection.get_tr_row(current_selection[current_selection.length - 1]);
					/* If the current selection is lower than any of the previous ones */
					if (current_row < min_selection_row) {
						selector_list = $(container).find("table").children("tbody").find("tr").slice(current_row, min_selection_row);
					}
					/* If the current selection is upper than any of the previous ones */
					else if (current_row > max_selection_row) {
						selector_list = $(container).find("table").children("tbody").find("tr").slice(max_selection_row + 1, current_row + 1);
					}
					/* If the selection is in the middle of the current one, use the previous selection */
					else {
						if (parametric_table_enable_selection.previous_selection_row < current_row) {
							selector_list = $(container).find("table").children("tbody").find("tr").slice(parametric_table_enable_selection.previous_selection_row + 1, current_row + 1);
						}
						else {
							selector_list = $(container).find("table").children("tbody").find("tr").slice(current_row, parametric_table_enable_selection.previous_selection_row);
						}
					}
				}
			}
			$(selector_list).each(function() {
				parametric_table_toggle_row_selection(this);
			});
			/* Store previous selection */
			parametric_table_enable_selection.previous_selection_row = parametric_table_enable_selection.get_tr_row(cell);

			/* If the selection is unique, fire specific actions if enabled */
		/*	if (selector_list.length == 1) {
				var parametric = selection_to_parametric(get_selection());
				for (var first in parametric) break;
				parametric = parametric[first];
				// Highlight similar groups
				if ($(id_highlight_similarities).is(':checked')) {
					for (var i in category_list) {
						if (!category_list[i]["is_group"]) {
							continue;
						}
						var param = category_list[i]["param"];
						if (!parametric[param] || !parametric[param][0]) {
							continue;
						}
						var value = parametric[param][0];
						var query = [{
							'param': param + "0",
							'value': value
						}];
						var selection = search_devices(query);
						add_similarity(selection, i);
					}
				}
			} */
		};

	}

	/* Enable selection */
	var real_table = parametric_table_get_real_table(container);
	$(real_table).click(parametric_table_on_click);
	parametric_table_on_click.enable_selection = true;
}

function parametric_table_on_click(e)
{
	var cell = e.target;

	if (cell.nodeName.toLowerCase() != "td") {
		return;
	}

	var row = $(cell).parent("tr");
	var is_shift_key = e.shiftKey;
	var is_ctrl_key = e.ctrlKey;

	/* Disable selection if the user pressed on the edit box */
	if ($(cell).hasClass("editmode")) {
		return;
	}

	/* Stop edit in case it was editing */
	if (typeof parametric_table_edit_stop == "function") {
		parametric_table_edit_stop(cell, false);
	}

	/* Remove selection in that case */
	if (is_shift_key) {
		window.getSelection().removeAllRanges();
	}

	if (typeof parametric_table_on_dblclick == "function" && parametric_table_enable_selection.timeout) {
		/* Double click detected */
		clearTimeout(parametric_table_enable_selection.timeout);
		parametric_table_enable_selection.timeout = null;
		parametric_table_on_dblclick(cell);
	}
	else {
		/* Fires a click after a timeout */
		parametric_table_enable_selection.timeout = setTimeout(function() {
			parametric_table_enable_selection.timeout = null;
			if (typeof parametric_table_on_click.enable_selection != "undefined") {
				parametric_table_enable_selection.click(row, is_shift_key, is_ctrl_key);
			}
		}, 200);
	}
}

function parametric_table_create(container, data, options)
{
	/* Setup the options */
	options = parametric_table_options_setup(options);

	/* Start loading animation */
	var loading_elt = document.createElement("div");
	$(loading_elt).addClass("loading");
	var position = $(container).offset();
	$(loading_elt).css({
		position: "absolute",
		left: position.left,
		top: position.top,
		width: $(container).width(),
		height: $(container).height(),
	});
	$(loading_elt).appendTo(document.body);

	$(".loading_trigger").addClass("disabled");
	$("input.loading_trigger").attr("disabled", "disabled");
	$("select.loading_trigger").attr("disabled", "disabled");

	setTimeout(function() {
		parametric_table_create_async(container, data, options, loading_elt);
	}, 100);
}

function parametric_table_create_async(container, data, options, loading_elt)
{
	/* Handle options */
	var categories = category_list;
	/* show_only option */
	if (options["show_only"]) {
		var new_categories = [];
		for (var i in categories) {
			if (options["show_only"].indexOf(categories[i].param) != -1) {
				new_categories.push(categories[i]);
			}
		}
		categories = new_categories;
	}
	/* custom_category option */
	if (options["custom_category"].length) {
		for (var i in options["custom_category"]) {
			var new_category = options["custom_category"][i];
			var param = new_category["param"];
			/* Insert the category */
			if (new_category["insert_after"]) {
				for (var j in categories) {
					if (categories[j].param == new_category["insert_after"]) {
						break;
					}
				}
				categories.splice(parseInt(j)+1, 0, new_category);
			}
			else {
				categories.push(new_category);
			}
			/* Add the data */
			for (var j in data) {
				data[j][param] = new_category["data"](data[j]);
			}
		}
	}

	/* Clear the inside of the container */
	$(container).empty();
	/* Create the basic structure of the table */
	$(container).html("<table class=\"tablesorter scrollableFixedHeaderTable\"><thead></thead><tbody></tbody></table>");
	/* Add a new class to the container to be easily identifiable */
	$(container).addClass("parametric_table");

	/* Header ----------------------------------------------------------- */

	/* Fill the header category of the table */
	var row = "<tr>";
	var previous_category = "";
	var colspan_nb = 0;
	for (var j in categories) {
		var param = categories[j];
		if (colspan_nb && (typeof param.category == "undefined" || !param.category || param.category != previous_category)) {
			row += "<td class=\"header\" colspan=\"" + colspan_nb + "\">" + previous_category + "</td>";
			colspan_nb = 0;
		}
		previous_category = (typeof param.category == "string" && param.category)?param.category:"";
		colspan_nb++;
	}
	row += "<th class=\"header\" colspan=\"" + colspan_nb + "\">" + previous_category + "</th>";
	row += "</tr>";
	$(container).find("table > thead").append(row);

	/* Fill the header of the table */
	var row = "<tr>";
	for (var j in categories) {
		var param = categories[j];
		row += "<th class=\"header\">";
		row += param.name;
		row += "</th>";
		/* Identify the parameter ID */
		if (param.param == parameter_id_name) {
			parameter_id = j;
		}
	}
	row += "</tr>";
	$(container).find("table > thead").append(row);

	/* FILTER ----------------------------------------------------------- */

	if (options["enable_filtering"]) {
		/* Create the filter row */
		var row = parametric_table_create_filter(data, categories);
		$(container).find("table > thead").append(row);
		/* Generate the search string */
		var search_string = parametric_table_generate_search_string(data, categories);
		/* Attach the search string to the container */
		$(container).data('search_string', search_string);
	}

	/* Fill the body of the table */
	for (var mcu_name in data) {
		parametric_table_add_entry(container, mcu_name, data[mcu_name], categories);
	}

	/* SORT ------------------------------------------------------------- */
	var tablesorter_options = {
		widthFixed: true
	};
	/* Hack to bypass a IE bug */
	if (navigator.appName != 'Microsoft Internet Explorer') {
		/* Assign custom sorting method if any */
		tablesorter_options['sortList'] = [];
		for (var i in options["sort"]) {
			var sort_cat = options["sort"][i];
			for (var j in categories) {
				if (categories[j].param == sort_cat) {
					tablesorter_options['sortList'].push([parseInt(j), 0]);
					break;
				}
			}
		}
	}
	/* Sort the table */
	$(parametric_table_get_real_table(container)).tablesorter(tablesorter_options);

	/* FREEZE PAN ------------------------------------------------------- */

	var jq_table_selection = $(container).find("table");

	/* MAIN CONTAINER */
	/* Create a container and move the table inside */
	var paramtab_container = document.createElement("div");
	$(paramtab_container).css("position", "relative");
	$(paramtab_container).css("overflow", "hidden");
	$(paramtab_container).insertBefore(jq_table_selection);
	jq_table_selection.detach().prependTo(paramtab_container);

	/* HEADER */
	/* Create the header div and create a blank table inside */
	var paramtab_container_header = document.createElement("div");
	var paramtab_div_header = document.createElement("div");
	var paramtab_table_header = document.createElement("table");
	$(paramtab_table_header).addClass("tablesorter");
	$(paramtab_div_header).css("position", "relative");
	$(paramtab_div_header).append(paramtab_table_header);
	$(paramtab_container_header).css("position", "absolute");
	$(paramtab_container_header).css("overflow", "hidden");
	$(paramtab_container_header).css("z-index", "1");
	$(paramtab_container_header).append(paramtab_div_header);
	/* Copy and paste the table header to the header div */
	var original_header = jq_table_selection.find("thead").detach();
	jq_table_selection.prepend($(original_header).clone());
	$(original_header).appendTo($(paramtab_div_header).find("table"));
	$(paramtab_container).prepend($(paramtab_container_header));

	/* DATA */
	/* Create the table data div and paste the table inside */
	var paramtab_div_table = document.createElement("div");
	$(paramtab_div_table).css("overflow", "auto");
	jq_table_selection.detach().prependTo(paramtab_div_table);
	$(paramtab_container).append($(paramtab_div_table));

	/* EVENTS */
	/* Add events to freeze the header vertically */
	$(paramtab_div_table).scroll(function() {
		$(this).prev("div").children("div").css('left', (parseInt($(this).scrollLeft()) * -1) + "px");
	});

	/* Calculate scrollbar width for later use */
	var parent = $('<div style="width:50px;height:50px;overflow:auto"><div/></div>').appendTo('body');
	var child = parent.children();
	var width = child.innerWidth() - child.height(99).innerWidth();
	parent.remove();
	var paramtab_scrollbar_width = width;
	/* Fix width and height of the container */
	$(paramtab_div_table).css("width", $(container).width() + "px");
	$(paramtab_div_table).css("height", $(container).height() + "px");
	$(paramtab_container_header).css("width", ($(container).width() - paramtab_scrollbar_width) + "px");

	/* CONTENT ---------------------------------------------------------- */

	/* Resize the column sizes */
	parametric_table_resize_columns(container);

	/* SELECTION -------------------------------------------------------- */
	if (options["enable_selection"]) {
		parametric_table_enable_selection($(container));
	}

	/* ASSIGN DATA ------------------------------------------------------ */
	/* Assign the parametric data to this table */
	$(parametric_table_get_container(container)).data('data', data);
	$(parametric_table_get_container(container)).data('categories', categories);

	/* CONTEXT MENU ----------------------------------------------------- */
	if (options["enable_contextmenu"]) {
		parametric_table_contextmenu_init(container);
	}

	/* DELETE LOADING --------------------------------------------------- */
	$(loading_elt).remove();
	$(".loading_trigger").removeClass("disabled");
	$("input.loading_trigger").removeAttr("disabled");
	$("select.loading_trigger").removeAttr("disabled");
}

function parametric_table_resize_columns(container)
{
	var real_table = parametric_table_get_real_table(container);
	var header_table = parametric_table_get_header_table(container);
	$(header_table).css('width', $(real_table).width());
	$(real_table).find("thead").find("th,td").each(function(index) {
		var elt = $(header_table).find("thead").find("th,td").get(index);
		var width = $(this).width();
		$(elt).css('min-width', width + "px");
	});
}
