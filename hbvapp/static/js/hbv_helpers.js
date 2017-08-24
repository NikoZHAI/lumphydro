/*
This JavaScript file contains functions
to help web iteracting on client-side.

Including:
	- Input dictionaries parsing;
	- Show calibrating results params;
	- **_step_run client side;
	...
*/

String.prototype.toFloat = function() {
  var int = parseFloat(this).toFixed(2);
  return parseFloat(int);
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

function generate_config_dict(){
	/*
		Generate a json or json-like object
		to serve as configuration input in AJAX
	*/

  var header = document.getElementById("id_csvHeaderInput");
  var separator = document.getElementById("id_csvSeparatorInput");
  var warm_up = document.getElementById("id_warmUpInput");
  var obj_fun = $("input[name='objFunctionInput']:checked");
  var tol = document.getElementById("id_tolInput");
  var minimise = document.getElementById("id_minimise");
  var verbose = document.getElementById("id_verbose");

  /*
    validators
  */

  // A Json object for AJAX POST or POST
  var config = {};

  config['header'] = parseInt(header.value);
  config['separator'] = separator.value;
  config['warm_up'] = parseInt(warm_up.value);
  config['obj_fun'] = obj_fun.val();
  config['tol'] = parseFloat(tol.value);
  (minimise.checked) ? config['minimise'] = true : config['minimise'] = false;
  (verbose.checked) ? config['verbose'] = true : config['verbose'] = false;
  (config['obj_fun'] == "self._rmse") ? config['fun_name'] = "RMSE" : config['fun_name'] = "NSE";

  return config;
}


function check_float() {
  var p1 = /^\+?\d+(\.\d+)?$/g;
  var p2 = /^\-?\d+(\.\d+)?$/g;
  var value = this.value;
  var name = this.name.toUpperCase();
  var deja_invalid = this.hasAttribute("invalid");

  var alert = `\
    <div class="alert alert-warning fade in" role="alert" style="padding: 5px 15px; margin-bottom: 12px;">\
      ${name} must be a <strong>REAL</strong> number ! \
    </div>\
    `;

  var valid = (p1.test(value)) || (p2.test(value));

  if (valid) {
    if(deja_invalid){
      this.removeAttribute("invalid");
      $(this.parentNode).next().remove();
    }
  }
  else {
    if(!deja_invalid) {
      this.setAttribute("invalid", "");
      $(alert).insertAfter(this.parentNode);
    }
  }
}

function generate_par_dict() {
  /*
    Generate a json or json-like object
    to serve as model params input in AJAX
  */

  var par_obj = new Object();
  var par_elems = $("#id_parList input");
  var patrn = /[-+]?[0-9]*\.?[0-9]+/g;

  // Create an object {ElementID: Element}
  for (var i = par_elems.length - 1; i >= 0; i--) {
    var value = par_elems[i].val();

    if (patrn.test(value)) {
      par_obj[par_elems[i].id.slice(3)] = parseFloat(value);
    }
    else {

    }
  }

  return par_obj;
}


function show_calibrated_par(par) {
  /*
    Show calibrated parameters on the parameter input panel
  */

  var par_obj = new Object();
  var par_elems = $("#id_parList input");

  // Create an object {ElementID: Element}
  for (var i = par_elems.length - 1; i >= 0; i--) {
    par_obj[par_elems[i].id] = par_elems[i];
  }

  for (var this_par in par) {
    if (this_par!='area'&&this_par!='tfac') {
      par_obj['id_'+this_par].value = par[this_par];
    } else {}
  }
}


function deploy_plots(plots) {
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
