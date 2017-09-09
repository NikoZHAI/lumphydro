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

// Helper to find corresponding index of a certain date in the time series
function indexof_date (date) {
  for (var i = hbv.d.init_data.length - 1; i >= 0; i--) {
    if(hbv.d.init_data[i].date == date){return i;}
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
  config['obj_fun'] = c.id_residus;
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
      hbv.c.context.bounds = {LB: P_LB, UB: P_UB};
      $(".save_bounds_success").html('<h5 class="text-success"><strong>SUCCESS</strong><span class="text-success"><i class="glyphicon glyphicon-ok"></i></span><h5>');
      setTimeout(function() { $("#id_bounds").modal('hide'); }, 1500);
    }
  });
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

function enable_datepickers (data, success) {

  if (success) {
    var date = data.map(function (row) {
      return moment(row.date);
    });
    var begin = date[0],
        end = date[date.length - 1];

    $("#datepicker_calibration input").each(function() {
     $( this ).prop("disabled", false);
    });
    $('#calibrate_from').data("DateTimePicker")
                        .defaultDate(moment(begin))
                        .enabledDates(date);
    $('#calibrate_to').data("DateTimePicker")
                      .defaultDate(moment(end))
                      .enabledDates(date);
  }
  else
  {
    $("#datepicker_calibration input").each(function() {
       $( this ).prop("disabled", true);
    });
  }
}

function deploy_plots (plots) {
  /*
    Deploy all generated Bokeh plots into html and JS
  */
  $("#id_pane_plot_q").html(plots.div.q);
  $(".jslocator_q").next().replaceWith(plots.script.q);

  $("#id_pane_plot_p").html(plots.div.p);
  $(".jslocator_p").next().replaceWith(plots.script.p);

  $("#id_pane_plot_t").html(plots.div.t);
  $(".jslocator_t").next().replaceWith(plots.script.t);

  $("#id_pane_plot_etp").html(plots.div.etp);
  $(".jslocator_etp").next().replaceWith(plots.script.etp);

  /* Spared for Ground Water Plots */

  $("#id_pane_plot_st").html(plots.div.st);
  $(".jslocator_st").next().replaceWith(plots.script.st);

  $("#id_pane_plot_perf").html(plots.div.perf);
  $(".jslocator_perf").next().replaceWith(plots.script.perf);
}
