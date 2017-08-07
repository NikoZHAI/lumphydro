/*
This JavaScript file contains functions
to help web iteracting on client-side.

Including:
	- Input dictionaries parsing;
	- Show calibrating results params;
	- **_step_run client side;
	...
*/


function generate_config_dict(){
	/*
		Generating a json or json-like object
		to serve as configuration input in AJAX
	*/

  var header = document.getElementById("id_csvHeaderInput");
  var separator = document.getElementById("id_csvSeparatorInput");
  var warm_up = document.getElementById("id_warmUpInput");
  var obj_fun = document.getElementById("id_objFunctionInput");
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
  config['obj_fun'] = obj_fun.value;
  config['tol'] = parseFloat(tol.value);
  (minimise.value == "true") ? config['minimise'] = "True" : config['minimise'] = "False";
  (verbose.value == "true") ? config['verbose'] = "True" : config['verbose'] = "False";
  (config['obj_fun'] == "self._rmse") ? config['fun_name'] = "RMSE" : config['fun_name'] = "NSE";

  return config;
}

function show_calibrated_par(par) {
  /*
    Show calibrated parameters on the parameter input panel
  */

  var par_obj = new Object();
  var par_elems = $("#id_parag_pars input");

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
