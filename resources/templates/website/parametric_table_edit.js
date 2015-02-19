function parametric_table_edit_update(object, type, index, match_value, value, other_values)
{
	/* This lists the different kind of values:
	 * - match_value is the original value of the edited cell, used to find a match
	 * - value is the new value of the edited cell. If the category is a list, it contains only the element of the list
	 * - other_values is the other values (if a list).
	 */
	var cell = parametric_table_get_edit_cell(object);
	var category = parametric_table_get_category_from_cell(object);

	/* Update the content of all selected cells */
	$(parametric_table_get_selected_cells(object, false)).each(function() {
		/* Identify similarity with others values */
		var original_values = parametric_table_get_value_from_cell(this, true);

		/* LIST and MULTI */
		if (category['is_list'] && category['is_multi']) {
			/* Loop through the original value and try to find a match */
			var is_match_value = false
			for (var j in original_values) {
				var original_value = original_values[j];

				/* Do not consider values which matches the other_values */
				var is_match_in_original = false;
				for (var k in other_values) {
					var other_value = other_values[k];
					is_match_in_original = true;
					for (var i in original_value) {
						if (other_value[i] != "" && original_value[i] != "" && other_value[i] != original_value[i]) {
							is_match_in_original = false; break;
						}
					}
					if (is_match_in_original) break;
				}
				if (is_match_in_original) continue;

				is_match_value = true;
				/* Loop through the values of an item from the list */
				for (var i in original_value) {
					try {
						/* If a value is different and it is not the one that is going to be modified */
						if (original_value[i] != "" && match_value[i] != "" && original_value[i] != match_value[i]) {
							is_match_value = false;
							break;
						}
					} catch (e) {
						break;
					}
				}
				if (is_match_value) break;
			}
			/* If there is a match, update the value */
			if (is_match_value) {
				if (type == "edit") {
					for (var i in value) {
						if (value[i] != "") {
							original_values[j][i] = value[i];
						}
					}
				}
				else if (type == "delete") {
					original_values.splice(j, 1);
				}
			}
			/* If there are no matches, add a new element */
			else if (type == "edit") {
				if (!original_values) {
					original_values = new Array();
				}
				original_values.push(value);
			}
		}
		/* MULTI only */
		else if (category['is_multi'] && type == "edit") {
			original_values[index] = value[index];
		}
		/* LIST only */
		else if (category['is_list']) {
			if (type == "edit") {
				if (!original_values) {
					original_values = new Array();
				}
				original_values.push(value[0]);
			}
			else if (type == "delete") {
				if (original_values.indexOf(match_value[0]) != -1) {
					original_values.splice(original_values.indexOf(match_value[0]), 1);
				}
			}
		}
		/* NORMAL */
		else if (type == "edit") {
			original_values = value[0];
		}

		parametric_table_set_value_to_cell(this, original_values, true);
	});
}

function parametric_table_generate_input_fields(cell)
{
	var category = parametric_table_get_category_from_cell(cell);
	var container = document.createElement("div");
	$(container).addClass("edit");
	var table = document.createElement("table");
	$(table).addClass("edit");
	var nb_fields = 1;

	if (category['is_multi'] && typeof category['nb_fields'] != "undefined") {
		nb_fields = category['nb_fields'];
	}

	/* Create the one-line input fields */
	var input_line = document.createElement("tr");
	$(input_line).addClass("edit");
	$(input_line).addClass(category['param']);
	for (var i = 0; i < nb_fields; i++) {
		var input_field = document.createElement("td");
		var category_type = TYPE_ANY;
		if (category['type'] && category['type'].length > i)
			category_type = category['type'][i];

		/* Create the input box */
		var input = document.createElement("input");
		$(input).addClass("edit");
		$(input).keyup(function(e) {
			code = (e.keyCode ? e.keyCode : e.which);
			/* Detect a press on ENTER */
			if (code == 13) {
				parametric_table_edit_stop(cell, true);
				e.preventDefault();
			}
			/* Detect a press on ESCAPE */
			else if (code == 27) {
				parametric_table_edit_stop(cell, false);
				e.preventDefault();
			}
		});
		$(input).attr("index", i);
		/* Update the content of all selected cell as well */
		$(input).change(function() {
			/* Get the modified values of the cell */
			var is_modified = $(this).parents("tr.edit").first().data("is_modified");
			var match_value = [];
			$(this).parents("tr.edit").first().find("td input.edit").each(function(i) {
				match_value.push((is_modified[i])?$(this).val():"");
			});
			/* Create the value for the match value */
			var value = clone(match_value);
			value[$(this).attr("index")] = $(this).val();
			/* Get the other values (if any and in case of a list) */
			var other_values = [];
			if (category['is_list']) {
				var current_row_index = $(this).parents("tr.edit").first().get(0).rowIndex;
				other_values = parametric_table_get_value_from_cell($("td.editmode"), true);
				other_values.splice(current_row_index, 1);
			}
			/* Update the other elements selected */
			parametric_table_edit_update(cell, "edit", $(this).attr("index"), match_value, value, other_values);
			/* Update the original value */
			is_modified[$(this).attr("index")] = [true];
			$(this).parents("tr.edit").first().data("is_modified", is_modified);

		});

		/* Create the input box according to the category type */
		if (typeof category_type == "object") {
			input = create_editable_dropbox(input, category_type);
		}
		else if ((category_type & TYPE_MASK) == TYPE_DATE) {
			$(input).click(function() {
				$(this).datepicker({dateFormat: 'yy-mm-dd'});
			});
		}

		$(input_field).append(input);

		if (typeof category['units'] == "object" && category['units'][i]) {
			var span = document.createElement("span");
			$(span).html(category['units'][i]);
			$(input_field).append(span);
		}
		$(input_line).append(input_field);
	}
	/* Add helper buttons */
	var button_container = document.createElement("td");
	/* Clear button */
	var button = document.createElement("input");
	$(button).attr("type", "button");
	$(button).addClass("clear");
	$(button).val("clear");
	$(button).click(function() {
		$(this).parents("tr.edit").first().find("input.edit").val("");
	});
	$(button_container).append(button);
	/* Delete */
	if (category['is_list']) {
		var button = document.createElement("input");
		$(button).attr("type", "button");
		$(button).addClass("delete");
		$(button).val("delete");
		$(button).click(function() {
			/* Get the modified values of the cell */
			var is_modified = $(this).parents("tr.edit").first().data("is_modified");
			var match_value = [];
			$(this).parents("tr.edit").first().find("td input.edit").each(function(i) {
				match_value.push((is_modified[i])?$(this).val():"");
			});
			parametric_table_edit_update(cell, "delete", nb_fields, match_value);
			$(this).parents("tr.edit").first().remove();
		});
		$(button_container).append(button);
	}
	/* Add the buttons to the line */
	$(input_line).append(button_container);

	/* Update the fields */
	var value = parametric_table_get_value_from_cell(cell, false);
	if (!category['is_multi']) {
		value = [value];
	}
	if (!category['is_list']) {
		value = [value];
	}
	/* Update the values */
	for (var j in value) {
		var sub_container = $(input_line).clone(true);
		if (typeof value[j] == "undefined")
			continue;
		var is_modified = [];
		for (var i in value[j]) {
			if (!$(sub_container).find("input").get(i))
				continue;
			if (typeof value[j][i] == "undefined")
				continue;
			$($(sub_container).find("input.edit").get(i)).val(value[j][i]);
			is_modified.push(false);
		}
		$(sub_container).data("is_modified", is_modified);
		$(table).append(sub_container);
	}
	$(container).append(table);

	/* Add comment field */
	var comment = document.createElement("div");
	var textarea = document.createElement("textarea");
	$(textarea).addClass("comment");
	$(textarea).change(function() {
		var comment = $(this).val();
		$(parametric_table_get_selected_cells(cell, false)).each(function() {
			parametric_table_set_comment_to_cell(this, comment, true);
		});
	});
	$(comment).append(textarea);
	$(container).append(comment);
	if (!parametric_table_get_comment_from_cell(cell, false)) {
		$(comment).hide();
		var button = document.createElement("input");
		$(button).attr("type", "button");
		$(button).addClass("comment");
		$(button).val("comment");
		$(button).click(function() {
			$(comment).show();
			$(this).hide();
		});
		$(container).append(button);
	}
	else {
		$(textarea).val(parametric_table_get_comment_from_cell(cell, false));
	}

	/* Add extra buttons */
	if (category['is_list']) {
		var button = document.createElement("input");
		$(button).attr("type", "button");
		$(button).addClass("add");
		$(button).val("add");
		$(button).click(function() {
			var sub_container = $(input_line).clone(true);
			var is_modified = [];
			for (var i=0; i<nb_fields; i++) {
				is_modified.push(false);
			}
			$(sub_container).data("is_modified", is_modified);
			$(table).append(sub_container);
		});
		$(container).append(button);
	}
	var button = document.createElement("input");
	$(button).attr("type", "button");
	$(button).addClass("valid");
	$(button).val("ok");
	$(button).click(function() {
		parametric_table_edit_stop(cell, true);
	});
	$(container).append(button);
	var button = document.createElement("input");
	$(button).attr("type", "button");
	$(button).addClass("cancel");
	$(button).val("cancel");
	$(button).click(function() {
		parametric_table_edit_stop(cell, false);
	});
	$(container).append(button);
	var button = document.createElement("input");
	$(button).attr("type", "button");
	$(button).addClass("clearall");
	$(button).val("clear all");
	$(button).click(function() {
		$(parametric_table_get_selected_cells(cell, true)).each(function() {
			parametric_table_set_value_to_cell(this, "", true);
			parametric_table_set_comment_to_cell(this, "", true);
		});
	});
	$(container).append(button);

	return container;
}

function parametric_table_on_dblclick(cell)
{
	if (!$(cell).hasClass("editmode")) {
		parametric_table_edit_stop(cell, false);

		/* Set global edit mode */
		parametric_table_set_edit_mode(cell);

		/* Generate the input fields */
		var input_fields = parametric_table_generate_input_fields(cell);
		$(cell).html(input_fields);

		/* Retrieve and save the original values of the cells */
		$(parametric_table_get_selected_cells(cell, false)).each(function() {
			var value = parametric_table_get_value_from_cell(this, false);
			var comment = parametric_table_get_comment_from_cell(this, false);
			parametric_table_set_value_to_cell(this, value, true);
			parametric_table_set_comment_to_cell(this, comment, true);
		});

		/* Update table size */
		parametric_table_resize_columns(cell);
	}
}

function parametric_table_edit_stop(object, submit)
{
	/* By default nothing is submit */
	if (typeof submit == "undefined") {
		submit = false;
	}
	/* If the table is not in edit mode, return */
	if (!parametric_table_is_edit_mode(object)) {
		return;
	}

	if (submit) {
		/* Loop through all selected cells */
		$(parametric_table_get_selected_cells(object, true)).each(function() {
			/* Update the value */
			$(this).addClass("modified");
			/* Post the value */
			parametric_table_submit_temporary_value_from_cell(this);
		});
	}
	else {
		/* Loop through all selected cells */
		$(parametric_table_get_selected_cells(object, true)).each(function() {
			parametric_table_discard_temporary_value_from_cell(this);
			parametric_table_discard_temporary_comment_from_cell(this);
		});
	}
	/* Leave the edit mode */
	parametric_table_clear_edit_mode(object);
	parametric_table_resize_columns(object);
}

/* Return the edited cells */
function parametric_table_get_selected_cells(object, include_editmode)
{
	if (typeof include_editmode == "undefined") {
		include_editmode = false;
	}

	/* Retrieve the selected cells from the table. It excludes the cell with the input box unless "include_editmode" is set to true */
	selected_cell = parametric_table_get_edit_cell(object);
	var col_number = $(selected_cell).parent().children().index($(selected_cell));
	cell_list = new Array();
	$(parametric_table_get_selection(object)).each(function() {
		if ($(this).get(0) !== $(selected_cell).parent("tr").get(0)) {
			cell_list.push($(this).children("td:nth(" + col_number + ")"));
		}
	});
	if (include_editmode) {
		cell_list.push(selected_cell);
	}
	return cell_list;
}

/* Return the edited cell */
function parametric_table_get_edit_cell(object)
{
	return $(parametric_table_get_real_table(object)).find("td.editmode").get(0);
}

/* Return true if the table is in edit mode */
function parametric_table_is_edit_mode(object)
{
	return ($(parametric_table_get_container(object)).data('editmode') == true);
}
/* set edit mode */
function parametric_table_set_edit_mode(cell)
{
	$(parametric_table_get_container(cell)).data('editmode', true);
	$(cell).addClass("editmode");
}
/* clear edit mode */
function parametric_table_clear_edit_mode(object)
{
	$(parametric_table_get_container(object)).data('editmode', false);
	$(parametric_table_get_real_table(object)).find("td").removeClass("editmode");
}

function prompt(title, body, action)
{
	var dialog = document.createElement("div");
	$(dialog).attr("id", "id_prompt");
	$(dialog).attr("title", title);
	$(dialog).html(body);
	$(dialog).dialog({
		closeText: "X",
		resizable: false,
		modal: true,
		buttons: [{
				text: "Ok",
				click: function() {
					action();
					$(this).dialog("close");
					$(this).remove();
				}
			},
			{
				text: "Cancel",
				click: function() {
					$(this).dialog("close");
					$(this).remove();
				}
			},
		]
	});
}

/* Editable combo box */
function create_editable_dropbox(object, list)
{
	var container = document.createElement("div");
	var select = document.createElement("select");
	var max_length = 0;
	for (var i in list) {
		var option = document.createElement("option");
		$(option).attr("value", list[i]);
		$(option).text(list[i]);
		$(select).append(option);
		max_length = Math.max(max_length, list[i].length);
	}
	$(select).change(function() {
		var input = $(this).next("input");
		$(input).val($(this).val());
		$(input).change();
		$(input).focus();
	});

	var width = max_length * 10;
	$(object).css("width", width + "px");
	$(object).css("border", "0px");
	$(object).css("margin-left", "-" + (width + 20) + "px");
	$(select).css("width", (width + 20) + "px");

	$(container).append(select);
	$(container).append(object);

	return container;
}

function parametric_table_set_reference_to_row(row, value, temporary)
{
	parametric_table_set_value_to_cell($(row).find("td").get(0), value, temporary);
}
function parametric_table_discard_temporary_value_from_cell(cell)
{
	var value = parametric_table_get_value_from_cell(cell, false);
	parametric_table_set_value_to_cell(cell, value, false);
}
function parametric_table_discard_temporary_comment_from_cell(cell)
{
	var comment = parametric_table_get_comment_from_cell(cell, false);
	parametric_table_set_comment_to_cell(cell, comment, false);
}
function parametric_table_submit_temporary_value_from_cell(cell)
{
	var reference = parametric_table_get_reference_from_cell(cell);
	var value = parametric_table_get_value_from_cell(cell, true);
	var category = parametric_table_get_category_from_cell(cell);
	var param = category['param'];

	var comment = undefined;
	var display_value = undefined;

	if (parametric_table_get_comment_from_cell(cell, true) != parametric_table_get_comment_from_cell(cell, false)) {
		comment = parametric_table_get_comment_from_cell(cell, true);
		parametric_table_set_comment_to_cell(cell, comment, false);
	}
	if (parametric_table_get_display_value_from_cell(cell, true) != parametric_table_get_display_value_from_cell(cell, false)) {
		display_value = parametric_table_get_display_value_from_cell(cell, true);
		display_value = $("<div/>").html(display_value).text();
	}
	parametric_table_set_value_to_cell(cell, value, false);

	/* Call the custom submit function if defined */
	if (category.submit) {
		result = category.submit(param, display_value, comment);
		param = result[0];
		display_value = result[1];
		comment = result[2];
	}

	/* Commit the change */
	commit(reference, param, display_value, comment);
}
function parametric_table_set_value_to_cell(cell, value, temporary)
{
	/* temporary - if it will store this value in the temporary data */
	if (typeof temporary == "undefined") {
		alert("Temporary attribute must be defined");
		return;
	}

	cell = $(cell).get(0);
	var reference = parametric_table_get_reference_from_cell(cell);
	var category = parametric_table_get_category_from_cell(cell);
	var param = category["param"];

	if (temporary) {
		/* Special case, if this is the edited cell */
		if ($(cell).hasClass("editmode")) {
			$(cell).find("input.edit").each(function() {
				$(this).val("");
			});
		}
		else {
			$(cell).data("value", value);
		}
	}
	else {
		var data = parametric_table_get_data(cell);
		if (typeof data[reference] == "undefined") {
			alert("Unknown device, this should never happend.");
			return;
		}
		if (typeof data[reference][param] == "undefined") {
			data[reference][param] = ["", "", "", "", ""];
		}
		data[reference][param][0] = value;
	}

	if (!$(cell).hasClass("editmode") || !temporary) {
		/* Update the display value as well */
		var display_value = parametric_table_format_cell("", value, category);
		$(cell).html(display_value);
	}
}
function parametric_table_set_comment_to_cell(cell, comment, temporary)
{
	/* temporary - if it will store this value in the temporary data */
	if (typeof temporary == "undefined") {
		alert("Temporary attribute must be defined"); return;
	}

	cell = $(cell).get(0);

	/* Encode the comment */
	comment = cencode(comment);

	if (temporary) {
		/* Special case, if this is the edited cell */
		if ($(cell).hasClass("editmode")) {
			$(cell).find("textarea.comment").val(comment);
		}
		else {
			$(cell).data("comment", comment);
		}
	}
	else {
		var reference = parametric_table_get_reference_from_cell(cell);
		var category = parametric_table_get_category_from_cell(cell);
		var param = category["param"];
		var data = parametric_table_get_data(cell);

		if (typeof data[reference] == "undefined") {
			alert("Unknown device, this should never happend.");
			return;
		}
		if (typeof data[reference][param] == "undefined") {
			data[reference][param] = ["", "", "", "", ""];
		}
		data[reference][param][4] = comment;
	}

	if (comment) {
		$(cell).addClass("comment");
	}
	else {
		$(cell).removeClass("comment");
	}
	$(cell).attr("comment", comment);
}

function clone(object)
{
	if (typeof object == "undefined" || typeof object == "string") {
		 return object;
	}
	if (jQuery.isArray(object)) {
		return jQuery.makeArray(clone($(object)));
	}
	return jQuery.extend(true, {}, object);
}

function cencode(string)
{
	return string.replace("\n", "\\n").replace("\"", "\\\"");
}

function cdecode(string)
{
	return string.replace("\\n", "\n").replace("\\\"", "\"");
}

