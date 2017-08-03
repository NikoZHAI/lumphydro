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

  return config;
}

function show_calibrated_par(par) {
  /*
    Show calibrated parameters on the parameter input panel
  */

  var index = ['ltt',
      'utt',
      'ttm',
      'cfmax',
      'fc',
      'e_corr',
      'etf',
      'lp',
      'k',
      'k1',
      'alpha',
      'beta',
      'cwh',
      'cfr',
      'c_flux',
      'perc',
      'rfcf',
      'sfcf',
      'tfac',
      'area'
      ];

  var par_elems = $("#id_parag_pars input");

  for (var i = par_elems.length - 1; i >= 0; i--) {
    par_elems[i].value = par[index[i]];
  }
}
