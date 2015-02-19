/* Create a panel
 * A panel is a container which contains a HMI.
 */
function panel(options) {
	/* Set-up default options */
	var defaults = {
		class: "panel",
		type: "ok",
		position: "right",
		width: 200,
		close: function() {},
		title: ""
	};
	var options = $.extend({}, defaults, options);

	/* Create the panel */
	var p = document.createElement('div');
	$(p).data("width", options.width);
	$(p).addClass(options.class);

	/* Associate methods */
	for (var fn in panel.fn) {
		p[fn] = panel.fn[fn];
	}
	p.position(options.position);

	/* Create the header of the panel */
	var header = document.createElement('div');
	$(header).addClass("panel_header");
	$(p).append(header);
	p.panel_title(options.title);

	/* Create the body of the panel */
	var body = document.createElement('div');
	$(body).addClass("panel_body");
	$(body).html("<div class=\"panel_body_container\"></div>");
	$(body).resize(function() {
		$(this).scrollbar();
	});
	$(p).append(body);

	/* Create the close handle */
	var close_handle = document.createElement('div');
	$(close_handle).addClass("panel_close");
	$(close_handle).click(function() {
		options.close();
		$(p).remove();
	});
	$(p).append(close_handle);

	/* Create the move handle */
	var move_handle = document.createElement('div');
	$(move_handle).addClass("panel_move");
	$(p).draggable({
		handle: $(move_handle),
		snap: "html",
		snapMode: "inner",
		revert: "invalid",
		cursor: "move",
		start: function(event, ui) {
			/* Read the various profiles available */
			var profiles = this.panel_profiles();
			for (var position in profiles) {
				/* Display and create the droppables */
				var droppable = document.createElement('div');
				$(droppable).addClass("panel_drop");
				$(droppable).css({
					position: "fixed",
					zIndex: 100
				});
				$(droppable).css(profiles[position].css);
				$(droppable).data("position", position);
				$(droppable).droppable({
				        tolerance: "pointer",
					hoverClass: "panel_drop_hover",
					addClasses: false,
					accept: $(p),
					greedy: true,
					drop: function(event, ui) {
						$(ui.draggable).get(0).position($(this).data("position"));
					}
				});
				$(document.body).append(droppable);
			}
		},
		stop: function(event, ui) {
			$(".panel_drop").remove();
		}
	});
	$(p).append(move_handle);

	/* Add the panel to the DOM */
	$(document.body).append(p);

	return p;
};
/* List of functions */
panel.fn = {};

/* Set or read the title
 */
panel.fn.panel_title = function(text) {
	if (typeof text == "undefined") {
		return $(this).find(".panel_header:first").text();
	}
	$(this).find(".panel_header:first").text(text);
}

/* Returns the list of available profiles for the panels
 */
panel.fn.panel_profiles = function() {
	return {
		top: {css: {left: 0, right: "auto", top: 0, bottom: "auto", width: $(window).innerWidth(), height: $(this).data("width")}},
		bottom: {css: {left: 0, right: "auto", top: "auto", bottom: 0, width: $(window).innerWidth(), height: $(this).data("width")}},
		left: {css: {left: 0, right: "auto", top: 0, bottom: "auto", width: $(this).data("width"), height: $(window).innerHeight()}},
		right: {css: {left: "auto", right: 0, top: 0, bottom: "auto", width: $(this).data("width"), height: $(window).innerHeight()}},
		center: {css: {left: "10%", right: "auto", top: "10%", bottom: "auto", width: ($(window).innerWidth() * 0.8), height: ($(window).innerHeight() * 0.8)}}
	};
}

/* Creates and adds a field to the panel
 */
panel.fn.add_field = function(content, options) {
	/* Set-up default options */
	var defaults = {
		class: "panel_field",
		tooltip: ""
	};
	var options = $.extend({}, defaults, options);

	var container = document.createElement('div');
	$(container).html(content);
	$(container).css({
		float: "left",
		marginRight: "5px",
		marginBottom: "5px"
	});
	$(container).addClass(options.class);
	$(container).tooltip(options.tooltip);
	$(this).find(".panel_body_container").append(container);
	$(this).find(".panel_body").resize();

	return container;
}

/* Add a section
 */
panel.fn.add_section = function(title) {
	this.add_field(title, {
		class: "panel_section_title"
	});
}

panel.fn.add_separator = function() {
	this.add_field("", {
		class: "panel_separator"
	});
}

panel.fn.add_field_edit_generic = function(title, value, options) {
	/* Set-up default options */
	var defaults = {
		enable_input: false,
		enable_title: false,
		enable_check: false,
		unit: null,
		class: "panel_field",
		change: function(value, enable) {},
		update: []
	};
	var options = $.extend({}, defaults, options);
	/* Convert the value to a function */
	var get_value = value;
	if (typeof get_value != "function") {
		get_value = function() { return value; };
	}
	/* Construct the html code */
	var html = "";
	if (options.enable_check) {
		html += "<div><input type=\"checkbox\"/></div>";
	}
	if (options.enable_title) {
		html += "<div>" + title + ":</div>";
	}
	if (options.enable_input) {
		html += "<div><input type=\"text\"/><div>";
	}
	if (options.unit) {
		html += "<div>" + options.unit + "</div>";
	}
	var container = this.add_field(html, options);
	/* Helper functions */
	var get_field_value = function() {
		return $(container).find("input[type=text]").val();
	};
	var set_field_value = function(value) {
		if (typeof value === "boolean") {
			$(container).find("input[type=checkbox]").prop('checked', value);
		}
		else {
			$(container).find("input[type=text]").val(value);
			$(container).find("input[type=checkbox]").prop('checked', true);
			$(container).find("input[type=text]").change();
		}
		$(container).find("input[type=checkbox]").change();
	};
	/* Event when the value has been changed */
	$(container).find("input[type=text]").change(function() {
		$(container).find("input[type=checkbox]").prop('checked', true);
		$(container).find("input[type=checkbox]").change();
		options.change(get_field_value(), true);
	});
	$(container).find("input[type=checkbox]").change(function() {
		if ($(this).is(":checked")) {
			$(this).parent().siblings("div").removeClass("disabled");
		}
		else {
			$(this).parent().siblings("div").addClass("disabled");
		}
		options.change(get_field_value(), $(this).is(":checked"));
	});
	/* Update the value when some events have been triggered */
	for (var i in options.update) {
		(options.update[i])(function() {set_field_value(get_value());});
	}
	/* Set the value of the field */
	set_field_value(get_value());
}

panel.fn.add_field_input = function(title, value, options) {
	/* Set-up default options */
	var defaults = {
		enable_input: true,
		enable_title: true,
		class: "panel_field panel_field_input"
	};
	var options = $.extend({}, defaults, options);
	/* Convert the value to a function */
	this.add_field_edit_generic(title, value, options);
}

panel.fn.add_field_check = function(title, value, options) {
	/* Set-up default options */
	var defaults = {
		enable_check: true,
		enable_title: true,
		class: "panel_field panel_field_check"
	};
	var options = $.extend({}, defaults, options);
	/* Convert the value to a function */
	this.add_field_edit_generic(title, value, options);
}

/* Sets the position of the panel
 */
panel.fn.position = function(position) {
	$(this).css({
		position: "fixed",
		zIndex: 1000
	});
	$(this).removeClass("panel_top panel_left panel_right panel_bottom");
	$(this).addClass("panel_" + position);

	var profiles = this.panel_profiles();
	/* Set the profile only if the position is recognized */
	if (typeof profiles[position] != "undefined") {
		$(this).css(profiles[position].css);
		/* Trigger the resize event to all sub-elements */
		$(this).find("*").resize();
	}
}
