/*
This JavaScript file contains functions
to help web iteracting on client-side.

Including:
	- Input dictionaries parsing;
	- Show calibrating results params;
	- Input validator;
	...
*/

String.prototype.toFloat = function() {
  var val = parseFloat(this).toFixed(2);
  return parseFloat(val);
};

// Get the last elemnt of an array
Array.prototype.last = function(){
  return this[this.length - 1];
};

//
function output(inp, element) {
    element.html("<pre>"+inp+"</pre>");
}

// Helper function to detect empty object and array
function isEmpty(obj) {
  for(var prop in obj) {
    if(obj.hasOwnProperty(prop))
      return false;
  }
  var deepchecker = JSON.stringify(obj);
  deepchecker === JSON.stringify({}) || deepchecker === JSON.stringify([]);
  return true;
}

// Helper function to check if a value is number (float/int/exp)
function isFloat(value) {
  var partern = "^(\\+|-|)?((\\d*\\.?\\d+([eE]?(\\+|-|)?\\d+)?)|(\\d+\\.?\\d*([eE]?(\\+|-|)?\\d+)?))$";
  var number = new RegExp(partern);
  return number.test(value);
}

// Customized unit test
function assert (condition, message) {
  if (!condition) {
    alert(message);
    throw new Error(message);
  }
}

// Helper to find corresponding index of a certain time in the time series
function indexof_time (time) {
  for (var i = hbv.d.init_data.length - 1; i >= 0; i--) {
    if(hbv.d.init_data[i].time == time){return i;}
  }
}

// Helper to find corresponding step of time of a certain index
function timeof_index (ind) {
  return hbv.d.init_data[ind].time;
}

// Helper, after a time input to find nearest existing time in current dataset
function environ_index_of (time, roundMethod) {
  roundMethod = roundMethod || Math.ceil;
  var e;
  (moment.isMoment(time)) ? e = moment.utc(time.format("YYYY-MM-DD HH:mm:ss")) : e = moment.utc(time);
  var first_step = hbv.d.info.last().first_step,
      last_step = hbv.d.info.last().last_step,
      time_step = hbv.d.info.last().time_step,
      diff_e_first = e.diff(first_step, "seconds"),
      index = roundMethod(diff_e_first/time_step);

  if(index>hbv.d.info.last().len-1){
    return hbv.d.info.last().len-1;
  }
  else if(index<0){
    return 0;
  }
  else{
    return index;
  }
}

// Helper for catch ajax error message
function ajax_error (jqXHR, exception) {
  var msg = '';
  if (jqXHR.status === 0) {
      msg = 'No connection.\n Verify Network.';
  } else if (jqXHR.status == 404) {
      msg = 'Requested page not found. [404]';
  } else if (jqXHR.status == 500) {
      msg = 'Internal Server Error [500].';
  } else if (exception === 'parsererror') {
      msg = 'Requested JSON parse failed.';
  } else if (exception === 'timeout') {
      msg = 'Time out error.';
  } else if (exception === 'abort') {
      msg = 'Ajax request aborted.';
  } else {
      msg = 'Uncaught Error.\n' + jqXHR.responseText;
  }
  msg += '\nPlease open the console (Press F12) to check details.';
  $('#ajax_error').html(`<p class="text-danger">
      <font size="4"><strong>FATAL!: </strong></font>
      <font size="2">${msg}</font></p>`)
                  .parent().fadeIn(200);
}

function check_not_null_float () {
  var value = this.value;
  var name = this.name.toUpperCase();
  var deja_invalid = this.hasAttribute("invalid");

  var alert_html = `\
    <div class="alert alert-warning fade in" role="alert" style="padding: 5px 15px; margin-bottom: 12px;">\
      ${name} must be a <strong>REAL</strong> number ! \
    </div>\
    `;

  var valid = isFloat(value);

  if (valid) {
    if(deja_invalid){
      this.removeAttribute("invalid");
      $(this.parentNode).next().remove();
    }
    return true;
  }
  else {
    if(!deja_invalid) {
      this.setAttribute("invalid", "");
      $(alert_html).insertAfter(this.parentNode);
    }
    return false;
  }
}

function check_minimum_float (mini) {
  var value = this.value;
  var name = this.name.toUpperCase();
  var deja_invalid = this.hasAttribute("invalid");

  var alert_html = `\
    <div class="alert alert-warning fade in" role="alert" style="padding: 5px 15px; margin-bottom: 12px;">\
      ${name} must be a <strong>POSITIVE REAL</strong> number greater than <strong>${mini}<strong>! \
    </div>\
    `;

  var valid = ( isFloat(value)&&(value > mini) );

  if (valid) {
    if(deja_invalid){
      this.removeAttribute("invalid");
      $(this.parentNode).next().remove();
    }
    return true;
  }
  else {
    if(!deja_invalid) {
      this.setAttribute("invalid", "");
      $(alert_html).insertAfter(this.parentNode);
    }
    return false;
  }
}

function check_float () {
  var value = this.value;
  var name = this.name.toUpperCase();
  var deja_invalid = this.hasAttribute("invalid");

  var alert_html = `\
    <div class="alert alert-warning fade in" role="alert" style="padding: 5px 15px; margin-bottom: 12px;">\
      ${name} must be a <strong>REAL</strong> number ! \
    </div>\
    `;

  var valid = isFloat(value) || (isEmpty(value));

  if (valid) {
    if(deja_invalid){
      this.removeAttribute("invalid");
      $(this.parentNode).next().remove();
    }
    return true;
  }
  else {
    if(!deja_invalid) {
      this.setAttribute("invalid", "");
      $(alert_html).insertAfter(this.parentNode);
    }
    return false;
  }
}

function check_int () {
  var p = /^\+?\d+$/g;
  var value = this.value;
  var name = this.name;
  var deja_invalid = this.hasAttribute("invalid");

  var alert_html = `\
    <div class="alert alert-warning fade in" role="alert" style="padding: 5px 15px; margin-bottom: 12px;">\
      ${name} must be a <strong>NON-NEGATIVE INTEGER</strong> ! \
    </div>\
    `;

  var valid =( (p.test(value))&&(value >= 0) );

  if (valid) {
    if(deja_invalid){
      this.removeAttribute("invalid");
      $(this.parentNode).next().remove();
    }
    return true;
  }
  else {
    if(!deja_invalid) {
      this.setAttribute("invalid", "");
      $(alert_html).insertAfter(this.parentNode);
    }
    return false;
  }
}

function check_cali_callback (e) {
  var box = e.target;
  var input = $(box).parent().parent().find("input[type=text]");

  if (box.checked==true) {
    input.prop("checked", true);
    hbv.c.context.par_to_calibrate[input[0].id] = true;
  }
  else {
    input.prop("checked", false);
    hbv.c.context.par_to_calibrate[input[0].id] = false;
  }
}

// Reserved for Bokeh
function deploy_plots (plots) {
  /*
    Deploy all generated Bokeh plots into html and JS
  */
  // $("#id_pane_plot_q").html(plots.div.q);
  // $(".jslocator_q").next().replaceWith(plots.script.q);

  // $("#id_pane_plot_p").html(plots.div.p);
  // $(".jslocator_p").next().replaceWith(plots.script.p);

  // $("#id_pane_plot_t").html(plots.div.t);
  // $(".jslocator_t").next().replaceWith(plots.script.t);

  // $("#id_pane_plot_etp").html(plots.div.etp);
  // $(".jslocator_etp").next().replaceWith(plots.script.etp);

  // /* Spared for Ground Water Plots */

  // $("#id_pane_plot_st").html(plots.div.st);
  // $(".jslocator_st").next().replaceWith(plots.script.st);

  $("#id_pane_plot_perf").html(plots.div.perf);
  $(".jslocator_perf").next().replaceWith(plots.script.perf);
}

function enable_timepickers (success) {

  if (success) {
    var time = hbv.d.init_data.map(function (row) {
      return moment.utc(row.time);
    });
    var begin = time[0],
        end = time[time.length - 1];

    $("#timepicker_calibration input").each(function() {
     $( this ).prop("disabled", false);
    });
    $('#calibrate_from').data("DateTimePicker")
                        .clear()
                        .enabledDates(time);
    $('#calibrate_to').data("DateTimePicker")
                      .clear()
                      .enabledDates(time);
    $('#calibrate_from').data("DateTimePicker")
                        .date(begin);
    $('#calibrate_to').data("DateTimePicker")
                      .date(end);
  }
  else
  {
    $("#timepicker_calibration input").each(function() {
       $( this ).prop("disabled", true);
    });
  }
}

function enable_timepickers_for_plots(success) {

  if (success) {
    var time = hbv.d.data[0].time.map(function(e){return moment.utc(e);}),
        begin = time[0],
        end = time.last();

    $("#div_timepicker_for_plots input").each(function() {
     $( this ).prop("disabled", false);
    });
    $('#left').data("DateTimePicker")
              .clear()
              .enabledDates(time);
    $('#right').data("DateTimePicker")
               .clear()
               .enabledDates(time);
    $('#left').data("DateTimePicker")
              .defaultDate(begin);
    $('#right').data("DateTimePicker")
               .defaultDate(end);

    // set current focus of the plot and schema to whole set of data
    hbv.s.set_local_extrems(0, time.length-1);
  }
  else
  {
    $("#div_timepicker_for_plots input").each(function() {
       $( this ).prop("disabled", true);
    });
  }
}

function generate_config_dict () {
  /*
    Generate a json or json-like object
    to serve as configuration input in AJAX
  */
  var c = hbv.c.context;

  /*
    validators
  */

  // A Json object for AJAX POST or POST
  var config = {};

  config['header'] = parseInt(c.id_csvHeaderInput);
  config['separator'] = c.id_csvSeparatorInput;
  config['warm_up'] = parseInt(c.id_warmUpInput);
  config['obj_fun'] = c.id_criteria;
  config['tol'] = parseFloat(c.id_tolInput);
  config['minimise'] = c.id_minimise;
  config['verbose'] = c.id_verbose;
  config['fun_name'] = config['obj_fun'];
  config['kill_snow'] = !c.id_snow;
  config['calibrate_from'] = c.calibrate_from;
  config['calibrate_to'] = c.calibrate_to;
  config['calibrate_all_par'] = c.id_calibrate_all_par;
  config['par_to_calibrate'] = new Array();
  config['init_guess'] = c.id_init_guess;

  Object.keys(c.par_to_calibrate).forEach(function(k){
    if (c.par_to_calibrate[k]) {
      config['par_to_calibrate'].push(k.slice(3));
    }
    else{undefined;}
  });

  return config;
}

function generate_par_dict (action) {
  /*
    Generate a json or json-like object
    to serve as model params input in AJAX
  */
  var par_elems = $("#id_parList input[par]");

  if (action == "calibrate") {
    var validation_state = par_elems.map(function (i, element) {
      if (element.checked==true) {
        return true;
      }
      else {
        return check_not_null_float.call(element);
      }
    });
    validation_state.areaValid = check_not_null_float.call(par_elems[0]);
  }
  else {
    var validation_state = par_elems.map(check_not_null_float);
  }

  var passed = !(Object.values(validation_state).includes(false));

  assert(passed, "Oh~o! Something wrong in input parameters ! Please check again !")

  var par_obj = new Object();
  // Create an object {ElementID: Element}
  for (var i = par_elems.length - 1; i >= 0; i--) {
    par_obj[par_elems[i].id.slice(3)] = parseFloat(par_elems[i].value);
  }

  return par_obj;
}

function generate_st_dict () {
  /*
    Generate a json or json-like object
    to serve as model states input in AJAX
  */
  var st_elems = $("#id_parList input[st]");
  var validation_state = st_elems.map(check_not_null_float);
  var passed = !(Object.values(validation_state).includes(false));

  assert(passed, "Oh~o! Something wrong in input parameters ! Please check again !")

  var st_obj = new Object();
  // Creat an object {ElementID: Element}
  for (var i = st_elems.length - 1; i >= 0; i--) {
    st_obj[st_elems[i].id.slice(3)] = parseFloat(st_elems[i].value);
  }

  return st_obj;
}

function relayout_dp_for_plots(i, time) {
  var left_bound = moment.utc(hbv.d.init_data[0].time),
      right_bound = moment.utc(hbv.d.init_data.slice(-1)[0].time),
      time = moment.utc(time);
  (time>right_bound) ? time=right_bound : undefined;
  (time<left_bound) ? time=left_bound : undefined;

  var update = {};
  update[`xaxis.range[${i}]`] = time;
  update[`xaxis.rangeslider.range[${i}]`] = time;

  Object.values($("div[forplot] div.js-plotly-plot")).slice(0,-2).forEach(function(this_plot){
    Plotly.relayout(this_plot, update);
  });
}

function show_calibrated_par (par) {
  /*
    Show calibrated parameters on the parameter input panel
  */

  var par_obj = new Object();
  var par_elems = $("#id_parList input");

  // Create an object {ElementID: Element}
  for (var i = par_elems.length - 1; i >= 0; i--) {
    par_obj[par_elems[i].id] = par_elems[i];
  }

  if (hbv.c.context.id_sci_note) {
    for (var this_par in par) {
      if (this_par!='area'&&this_par!='tfac') {
        par_obj['id_'+this_par].value = par[this_par].toExponential(2);
      }
    }
  }
  else {
    for (var this_par in par) {
      if (this_par!='area'&&this_par!='tfac') {
        par_obj['id_'+this_par].value = par[this_par];
      }
    }
  }

  // MAXBAS is elegant if remains integer
  par_obj['id_mbas'].value = parseInt(par_obj['id_mbas'].value);
}

function save_bounds() {

  var lb_elems = $("#col_LB input"),
      ub_elems = $("#col_UB input"),
      P_LB = new Array(),
      P_UB = new Array();

  var validation_state_0 = lb_elems.map(function (i, element) {
    P_LB.push(parseFloat(element.value));
    return check_not_null_float.call(element);
  });
  var validation_state_1 = ub_elems.map(function (i, element) {
    P_UB.push(parseFloat(element.value));
    return check_not_null_float.call(element);
  });

  var pass = !(Object.values(validation_state_0).includes(false) || Object.values(validation_state_1).includes(false));

  assert(pass, "Oh~o! Something wrong in PARAMETER BOUNDARIES ! Please check again !")

  $.ajax({
    url: "",
    type: "POST",
    async: true,
    data: {'P_LB': JSON.stringify(P_LB),
            'P_UB': JSON.stringify(P_UB),
            'action': 'save_bounds'},
    success: function(){
      hbv.c.context.bounds = {P_LB: P_LB, P_UB: P_UB};
      $(".save_bounds_success").html('<h5 class="text-success"><strong>SUCCESS</strong><span class="text-success"><i class="glyphicon glyphicon-ok"></i></span><h5>');
      setTimeout(function() { $("#id_bounds").modal('hide'); }, 1500);
    }
  });
}

/* Parameter Input Markup on the schematisation */
function markupInputWidgets() {
  var divs = $("#id_schema_innerdiv div"),
      inputs = $("#id_schema_innerdiv input"),
      outter_div = $("#id_schema_innerdiv")[0].getBoundingClientRect();

  divs.map(function(i, e){
    var id = e.id.substring(6),
        rect = $("#wid"+id)[0].getBoundingClientRect(),
        style_div = {
          "left": `${rect.left+rect.width-outter_div.left}px`,
          "top": `${rect.top-outter_div.top-1}px`,
          "height": `${rect.height+2}px`,
          "width": "0%",
        },
        style_input = {
          "height": `${rect.height+2}px`,
        };
    $(inputs[i]).css(style_input);
    $(e).css(style_div);
  });
}

function toggleHover() {
  var id_input = "#id_schema_innerdiv #id_" + this.id.substring(4),
      id_div = "#id_div_" + this.id.substring(4);
  $(id_div).toggleClass("hovered");
  $(id_input).toggleClass("hovered");
}

