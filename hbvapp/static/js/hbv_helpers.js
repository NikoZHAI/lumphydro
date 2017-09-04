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

// Customized unit test
function assert(condition, message) {
  if (!condition) {
    alert(message);
    throw new Error(message);
  }
}

function initialize_data (text, context) {
  var delimiter = context.id_csvSeparatorInput,
      header = parseInt(context.id_csvHeaderInput);
  var success = false;
  try {
    var data = d3.dsvFormat(delimiter).parse(text, function(d, i) {
      return {
        date: new Date(d.date),
        prec: +d.prec,     // Precipitation
        q_rec: +d.q_rec,   // Recorded discharge
        temp: +d.temp,     // Air temperature
        tm: +d.tm,         // Monthly mean air temperature
        ep: +d.ep,         // Evaporation
      };
    });
    success = true;
  }
  catch (ex) {
    alert(ex.message);
    throw(ex); // Re-throw the exception to outer scope
  }
  finally {
    enable_datepickers(data, success);
  }

  function data_validator() {
    return undefined;
  }
  return data;
}

function generate_config_dict (){
	/*
		Generate a json or json-like object
		to serve as configuration input in AJAX
	*/
  var c = client_context;

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

  return config;
}

function check_not_null_float () {
  var partern = "^(\\+|-|)?((\\d*\\.?\\d+([eE]?(\\+|-|)?\\d+)?)|(\\d+\\.?\\d*([eE]?(\\+|-|)?\\d+)?))$";
  var number = new RegExp(partern);
  var value = this.value;
  var name = this.name.toUpperCase();
  var deja_invalid = this.hasAttribute("invalid");

  var alert_html = `\
    <div class="alert alert-warning fade in" role="alert" style="padding: 5px 15px; margin-bottom: 12px;">\
      ${name} must be a <strong>REAL</strong> number ! \
    </div>\
    `;

  var valid = number.test(value);

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
  var p1 = /^\+?\d+(\.\d+)?$/g;
  var value = this.value;
  var name = this.name.toUpperCase();
  var deja_invalid = this.hasAttribute("invalid");

  var alert_html = `\
    <div class="alert alert-warning fade in" role="alert" style="padding: 5px 15px; margin-bottom: 12px;">\
      ${name} must be a <strong>POSITIVE REAL</strong> number greater than <strong>${mini}<strong>! \
    </div>\
    `;

  var valid = ( (p1.test(value))&&(value > mini) );

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
  var partern = "^(\\+|-|)?((\\d*\\.?\\d+([eE]?(\\+|-|)?\\d+)?)|(\\d+\\.?\\d*([eE]?(\\+|-|)?\\d+)?))$";
  var number = new RegExp(partern);
  var value = this.value;
  var name = this.name.toUpperCase();
  var deja_invalid = this.hasAttribute("invalid");

  var alert_html = `\
    <div class="alert alert-warning fade in" role="alert" style="padding: 5px 15px; margin-bottom: 12px;">\
      ${name} must be a <strong>REAL</strong> number ! \
    </div>\
    `;

  var valid = (number.test(value)) || (isEmpty(value));

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
      ${name} must be a <strong>POSITIVE INTEGER</strong> ! \
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

function generate_par_dict (action) {
  /*
    Generate a json or json-like object
    to serve as model params input in AJAX
  */
  var par_elems = $("#id_parList input[par]");

  if (action == "calibrate") {
    var validation_state = par_elems.map(check_float);
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

  if (client_context.id_sci_note) {
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

function changeContextWhenInput (elem) {
  /*
    Function in charge of changing context of the client
  */
  var twins = [
  "id_perc",
  "id_alpha",
  "id_k1",
  "id_mbas",
  "id_k",
  "id_lz",
  "id_uz",
  "id_c_flux",
  "id_beta",
  "id_lp",
  "id_etf",
  "id_e_corr",
  "id_fc",
  "id_sm",
  "id_cfr",
  "id_cwh",
  "id_cfmax",
  "id_ttm",
  "id_utt",
  "id_ltt",
  "id_sfcf",
  "id_rfcf",
  "id_wc",
  "id_sp",
  "id_tfac",
  "id_area"];

  var id = elem.id;
  var value = elem.value;

  (elem.hasAttribute("invalid")) ? null : client_context[id] = value;

  if (id == "id_RMSE" || id == "id_NSE") {
    if(elem.checked == true) {
      (id == "id_RMSE") ? client_context['id_residus'] = "RMSE" : client_context['id_residus'] = "NSE";
    }
  }

  if (value=="boolean") {
    (elem.checked==true) ? client_context[id] = true : client_context[id] = false;
  }

  if (twins.indexOf(id) >= 0) {
    var siblings = Object.values($(`input[id=${id}]`)).slice(0,2);
    siblings.forEach(function (element) {
      element.value = value;
      element.onchange();
    });
  }
}

function changeContextWhenLoad (context) {
  /*
    Change context when loading a parameter file or running the demo
  */
  var twins = [
    "id_perc",
    "id_alpha",
    "id_k1",
    "id_mbas",
    "id_k",
    "id_lz",
    "id_uz",
    "id_c_flux",
    "id_beta",
    "id_lp",
    "id_etf",
    "id_e_corr",
    "id_fc",
    "id_sm",
    "id_cfr",
    "id_cwh",
    "id_cfmax",
    "id_ttm",
    "id_utt",
    "id_ltt",
    "id_sfcf",
    "id_rfcf",
    "id_wc",
    "id_sp",
    "id_tfac",
    "id_area"];

  for (var id in context) {
    var value = context[id];
    var elem =  $(`input[id=${id}]`);

    if (typeof(value)=="boolean") {
      (value) ? elem.prop("checked", true) : elem.prop("checked", false);
      (elem.is("[invalid]")) ? null : client_context[id] = value;
    }
    else if ( id=="id_residus") {
      (context[id]=="RMSE") ? $("#id_RMSE").prop("checked", true) : $("#id_NSE").prop("checked", false);
      (elem.is("[invalid]")) ? null : client_context[id] = value;
    }
    else if (twins.indexOf(id) >= 0) {
      Object.values(elem).slice(0,2).forEach(function (element) {
        element.value = value;
        element.onchange();
        (element.hasAttribute("invalid")) ? null : client_context[id] = value;
      });
    }
    else {
      elem.value = value;
      (elem.is("[invalid]")) ? null : client_context[id] = value;
    }
  }
}

function sample() {
  context = {
    "id_verbose":true,
    "id_minimise":true,
    "id_tolInput":"0.001",
    "id_warmUpInput":"10",
    "id_csvSeparatorInput":",",
    "id_csvHeaderInput":"0",
    "id_calibrate_all_par":true,
    "id_select_date_range":false,
    "id_sci_note":true,
    "id_snow":true,
    "id_residus":"RMSE",
    "id_perc":"0.1",
    "id_alpha":"0.5",
    "id_k1":"0.00005",
    "id_mbas":"1",
    "id_k":"0.01",
    "id_lz":"0",
    "id_uz":"0",
    "id_c_flux":"0.05",
    "id_beta":"3.5",
    "id_lp":"0.35",
    "id_etf":"2.5",
    "id_e_corr":"1.0",
    "id_fc":"250",
    "id_sm":"0",
    "id_cfr":"0.5",
    "id_cwh":"0.02",
    "id_cfmax":"0.1",
    "id_ttm":"0.1",
    "id_utt":"0.1",
    "id_ltt":"-0.1",
    "id_sfcf":"1.0",
    "id_rfcf":"1.0",
    "id_wc":"0",
    "id_sp":"0",
    "id_tfac":"24",
    "id_area":"135.0"
  };
  changeContextWhenLoad(context);
}

// A context object to store everything
client_context = {
  "id_verbose":false,
  "id_minimise":true,
  "id_residus":"RMSE",
  "id_tolInput":"0.001",
  "id_warmUpInput":"10",
  "id_csvSeparatorInput":",",
  "id_csvHeaderInput":"0",
  "id_select_all_par":true,
  "id_select_date_range":false,
  "id_sci_note":true,
  "id_snow":true,
  "id_perc":"",
  "id_alpha":"",
  "id_k1":"",
  "id_mbas":"",
  "id_k":"",
  "id_lz":"",
  "id_uz":"",
  "id_c_flux":"",
  "id_beta":"",
  "id_lp":"",
  "id_etf":"",
  "id_e_corr":"",
  "id_fc":"",
  "id_sm":"",
  "id_cfr":"",
  "id_cwh":"",
  "id_cfmax":"",
  "id_ttm":"",
  "id_utt":"",
  "id_ltt":"",
  "id_sfcf":"",
  "id_rfcf":"",
  "id_wc":"",
  "id_sp":"",
  "id_tfac":"",
  "id_area":""
};
