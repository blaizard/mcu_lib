/* Selector of the table */
var jq_table_selector = "#id_table";
var jq_comp_table_selector = "#id_comparison_table"
/* Selector of the table header */
var jq_nb_devices = "#id_nb_devices";
var jq_nb_selected = "#id_nb_selected";
var jq_textarea_selector = "#submit textarea";
var jq_source_selector = "#submit #id_source";
var jq_trustability_selector = "#submit input[name=trustability]:checked";
var jq_packs_container_selector = "div.group_packs";
/* Selector of the table header */
var jq_table_header = "table.tablesorter:first";
/* Selector of the filter row */
var jq_filter_row = jq_table_header + " thead tr:nth-child(3)";
var jq_filter_rows = "table thead tr:nth-child(3)";
/* Default sorting method */
var sorting_method = [[1, 0], [2, 0], [3, 0], [0, 0]];
/* Index of the parameter ID */
var parameter_id = undefined;
/* The name of the parameter ID */
var parameter_id_name = "name";
/* List containing all changes to be submitted */
var change_list = [];
/* Current MCU list */
var mcu_data = {}
/* Search string for the current MCU list */
var search_string = "";
/* Flag to tell if we are in edit mode or not */
var cell_edit_mode = null;

/* Type constants */
var TYPE_ANY = 0; // data, 0, yes, -5.2, ...
var TYPE_INTEGER = 1; // -2, -1, 0, 1, yes, ...
var TYPE_DECIMAL = 2; // -1.05, 0.45, 10 ...
var TYPE_BINARY = 3; // yes, 0
var TYPE_STRING = 4; // data, hello, ...
var TYPE_DATE = 5; // [DD-][MM-]YYYY
var TYPE_MASK = 7; // Mask tho retrieve the data type
var TYPE_EXT_POSITIVE = 8;
var TYPE_EXT_NEGATIVE = 16;
var TYPE_EXT_NOT_NULL = 32;
var TYPE_EXT_BINARY = 64;

function script_init()
{
	/* Print a list of the avalable packs */
	$(jq_packs_container_selector).empty();
	for (var i in pack_list) {
		var pack = document.createElement("div");
		$(pack).addClass("pack");
		$(pack).click(function() {
			$(this).toggleClass("enable");
		});
		$(pack).html(pretty_print(pack_list[i]));
		$(pack).attr("reference", pack_list[i]);
		$(jq_packs_container_selector).append($(pack));
	}
}

function pretty_print(string)
{
	string = string.replace("_", " ");
	string = string.replace(/(^|\s)([a-z])/g, function(m, p1, p2){ return p1+p2.toUpperCase(); });
	return string;
}

function on_tab_change(event, ui)
{
	switch (ui['panel'].id) {
	case 'parametric':
		break;
	case 'comparison':
		compare_view();
		break;
	case 'submit':
		break;
	}
}

function create_and_format_vertical_tbody(parametric_list, extra_options)
{
	var data_list = [];
	for (var device_name in parametric_list) {
		data_list.push(create_and_format(device_name, parametric_list[device_name], extra_options));
	}

	var tbody = document.createElement("tbody");
	var reference_row = true;
	for (var j in category_list) {

		if (extra_options && extra_options["hide_empty_rows"]) {
			/* Do not process empty rows */
			var is_empty = true;
			for (var i in data_list) {
				if (data_list[i][j]["value"]) {
					is_empty = false;
					break;
				}
			}
			if (is_empty) {
				continue;
			}
		}

		var tr = document.createElement("tr");
		$(tr).append("<td class=\"header\">" + category_list[j].name + "</td>");
		$(tr).attr("category_index", j);
		for (var i in data_list) {
			var td = document.createElement("td");
			var data = data_list[i][j];
			/* If this is the 1rst row */
			if (reference_row) {
				$(td).attr("reference", data["value"]);
			}
			for (var attr_name in data) {
				$(td).attr(attr_name, data[attr_name]);
			}
			$(td).attr("vertical", "1");
			$(td).html(data["value"]);
			$(tr).append(td);
		}
		$(tbody).append(tr);
		reference_row = false;
	}
	return tbody;
}

function compare_view()
{
	/* Reset the table */
	$(jq_comp_table_selector).empty();
	/* Get the devices selected */
	var parametric = parametric_table_selection_to_data(get_selection());

	var tbody = create_and_format_vertical_tbody(parametric, {'hide_empty_rows': $("#id_hide_empty_rows").is(':checked')});
	$(jq_comp_table_selector).append(tbody);

	/* Highlight the comparison */
	compare_highlight();
}

function compare_highlight()
{
	/* Remove classes */
	$(jq_comp_table_selector).find("td").removeClass("strength").removeClass("weakness");

	var compare_threshold = $("#id_compare_threshold").slider("value");
	$(jq_comp_table_selector).find("tr").each(function() {
		var weight_list = [];
		var min = 999999999;
		var max = -999999999;
		var avg = 0;
		$(this).find("td:not(:first-child)").each(function() {
			var weight = get_weight_from_cell(this);
			weight_list.push(weight);
			/* Discard no weight data */
			if (weight == "") {
				return true;
			}
			min = Math.min(min, weight);
			max = Math.max(max, weight);
			avg += weight;
		//	$(this).html(get_weight_from_cell(this));
		});
		avg = avg / weight_list.length;
		$(this).find("td:not(:first-child)").each(function(index) {
			var weight = weight_list[index];
			/* Discard no weight data */
			if (weight == "") {
				return true;
			}
			var diff = Math.abs(avg - weight) / avg;
			if (weight == max && diff > compare_threshold) {
				$(this).addClass("strength");
			}
			else if (weight == min && diff > compare_threshold) {
				$(this).addClass("weakness");
			}
		});
	});
}

function get_weight_from_cell(cell)
{
	var NO_WEIGHT = "";
	var category = get_category_from_cell(cell);
	var value = get_value_from_cell(cell, false);

	get_weight_from_cell.merge = function(weight1, weight2) {
		if (weight1 == NO_WEIGHT) {
			return weight2;
		}
		if (weight2 == NO_WEIGHT) {
			return weight1;
		}
		return Math.max(weight1, weight2);
	}

	get_weight_from_cell.weight = function(value, ratio) {
		/* If the ratio or the value is empty */
		if (!ratio || !value) {
			return NO_WEIGHT;
		}
		/* Both the ratio and the value are numbers */
		else if (typeof ratio == "number" && Number(value) != NaN) {
			return ratio * value;
		}
		else if (typeof value == "object") {
			var weight = NO_WEIGHT;
			for (var i in value) {
				var sub_weight = get_weight_from_cell.weight(value[i], ratio);
				weight = get_weight_from_cell.merge(weight, sub_weight);
			}
			return weight;
		}
		/* [["harvard", 10], ["von neumann", 0]] */
		else if (typeof ratio == "object") {
			for (var j in ratio) {
				if (ratio[j][0] == value) {
					return ratio[j][1];
				}
			}
		}
		return NO_WEIGHT;
	}

	/* Cast the values to a list/multi type in order to re-use the same code */
	if (!category['is_list']) {
		value = [value];
	}
	if (!category['is_multi']) {
		value = [value];
	}

	var weight = NO_WEIGHT;
	var ratio = category['compare'];

	if (typeof ratio == "object") {
		for (var i in value) {
			var sub_weight = 0;
			for (var i_multi in value[i]) {
				var temp = get_weight_from_cell.weight(value[i][i_multi], ratio[i_multi]);
				if (temp != NO_WEIGHT) {
					sub_weight += temp;
				}
			}
			weight = get_weight_from_cell.merge(weight, sub_weight);
		}
	}

	return weight;
}

function group_by(category)
{
	var index = -1;
	/* Identify the row number of the category */
	for (var i in category_list) {
		if (category_list[i].param == category) {
			index = i;
			break;
		}
	}
	/* If nothing was found, cancel */
	if (index == -1) {
		return;
	}
	/* Sort the table */
        var sorting = [[index, 0]];
        $(parametric_table_get_real_table("#id_table")).trigger("sorton", [sorting]);
	parametric_table_unselect_all('#id_table');
	/* Loop through the columns */
	$(parametric_table_get_real_table("#id_table")).find("tr:visible").each(function(i) {
		category_value = $(this).find("td:nth(" + index + ")").text();
		if (i && previous_category_value != category_value) {
			/* If the current row value is different, then we have a group */
			parametric_table_group_selection('#id_table');
			parametric_table_unselect_all('#id_table');
		}
		/* Select the current row */
		parametric_table_select_row(this);
		previous_category_value = category_value;
	});
	/* The last group is not done, proceed */
	parametric_table_group_selection('#id_table');
	parametric_table_unselect_all('#id_table');
}

function add_similarity(selection, col_number)
{
	$(selection).find("td:nth-child(" + (parseInt(col_number) + 1) + ")").addClass("similarity");
}

function clear_similarities()
{
	$(jq_table_selector).children("tbody").find("td").removeClass("similarity");
}

function commit(id, param, value, comment, merge, group)
{
	var change = {
		'id': id,
		'param': param,
		'value': value
	};
	if (typeof value == "string") {
		change["value"] = value;
	}
	if (typeof comment == "string") {
		change["comment"] = comment;
	}
	if (typeof merge == "string") {
		change["merge"] = merge;
	}
	if (typeof group == "object") {
		change["group"] = group;
	}
	change_list.push(change);
	/* Enable the submit button */
	update_changes();
}

function update_changes()
{
	trustability = $(jq_trustability_selector).val();
	source = $(jq_source_selector).val();

	command = "python update.py --trust \"" + trustability + "\"";
	if (source) {
		command += " --source \"" + source + "\"";
	}
	command += " --verbose 1 --force --write <<EOF";
	/* Go through all the changes and submit them 1 by 1 */
	for (var i in change_list) {
		var item = change_list[i];
		if (typeof item["value"] == "string") {
			var value = item["value"];
			/* Replace special characters that might not print on the terminal */
			value = value.replace(new RegExp("\u2103", 'g'), "C");
			value = value.replace(new RegExp("\u00b5", 'g'), "u");
			command += "\n";
			command += "-- string \"" + item.param + "\" \"" +  cencode(value) + "\" \"" + item.id + "\"";
		}
		if (typeof item["comment"] == "string") {
			command += "\n";
			command += "-- comment \"" + item.param + "\" \"" +  cencode(item["comment"]) + "\" \"" + item.id + "\"";
		}
		if (typeof item["merge"] == "string") {
			command += "\n";
			command += "-- merge \"" + item.merge + "\" \"" + item.id + "\"";
		}
		if (typeof item["group"] == "object") {
			command += "\n";
			command += "-- group \"" + item.param + "\"";
			for (var i in item["group"]) {
				command += " \"" + item["group"][i] + "\"";
			}
		}
	}
	command += "\nEOF";
	$(jq_textarea_selector).val(command);
}

function info_update()
{
	$(jq_nb_devices).text($(jq_table_selector).children("tbody").find("tr:visible").length);
	$(jq_nb_selected).text(get_selection().length);
}

/* Load dynamically a javascript script */
function load_script(url, callback)
{
	$.getScript(url).done(callback).fail(function(jqxhr, settings, exception) {
		alert("Cannot retrieve the script at `" + url + "' (" + jqxhr.status + ", " + jqxhr.statusText + ")");
	});
}

/* This function is generating the mcu_data variable and the category_list */
function generate_mcu_list(pack_list, callback)
{
	mcu_data = {};
	category_list = [];

	for (var i in pack_list) {

		var pack_name = pack_list[i];
		try {
			var specific_mcu_list = eval(pack_name + "_mcu_list");
			var specific_category_list = eval(pack_name + "_category_list");
		}
		catch(err) {
			load_script("data_" + pack_name + ".js", callback);
			return false;
		}

		mcu_data = parametric_data_merge(mcu_data, specific_mcu_list, specific_category_list);
	}

	return true;
}

function process(name)
{
	/* Arguments */
	var args = [];
	/* Handle arguments if any */
	for (var i=1; i < arguments.length; i++) {
		args.push(arguments[i]);
	}
	setTimeout(function() {
		window[name].apply(this, args);
	}, 100);
}

function table_setup()
{
	/* Generate mcu_data, category_list */
	/* get the active pack list */
	var active_pack_list = [];
	$(jq_packs_container_selector).find("div.pack.enable").each(function() {
		active_pack_list.push($(this).attr("reference"));
	});
	if (!generate_mcu_list(active_pack_list, table_setup)) {
		return;
	}

	/* Adjust size of the main table */
	var offset = $("#id_table").offset();
	var width = $(window).width() - offset.left * 2;
	var height = $(window).height() - offset.top - 40;
	$("#id_table").css("width", width + "px");
	$("#id_table").css("height", height + "px");

	switch ($("#id_table_profile").val()) {
	case "normal":
		parametric_table_create_normal($("#id_table"), mcu_data);
		break;
	case "full":
		parametric_table_create($("#id_table"), mcu_data);
		break;
	}
}
