# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from .hbvcore import hbv96
import json

import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components

# Create HBV object
mcd = hbv96.HBV96()

mcd.par['area'] = 33.5

mcd.par['tfac'] = 24

mcd.config['init_guess'] = None

mcd.DEF_q0 = 0.183

# Home page.
@csrf_exempt
def home(request):
	global mcd
	template = 'hbvapp/home.html'
	context = {}
	if request.method == "POST" and request.is_ajax():
		
		post = request.POST
		action = post.get('action')
		context = {}

		# Use JsonResponse just to interact with JQuery
		if action=='load_file':
			mcd.data = post.get('text')
			return JsonResponse(context)

		elif action=='calibrate':
			mcd.config.update(json.loads(post.get('config')))
			mcd.extract_to_dict()
			mcd.calibrate()
			context['res_head'] = json.dumps(mcd.data[:5])
			context['size'] = len(mcd.data)
			context['par'] = mcd.par
			context['script_plot_simulation'], context['div_plot_simulation'] = plot_simulation(mcd.data)
			return JsonResponse(context)
		
		elif action=='summarize':
			context['res_head'] = json.dumps(mcd.data[:5])
			context['size'] = len(mcd.data)
			return JsonResponse(context)

		else:
			return JsonResponse(context)
	else:
		return render(request, template)

def plot_simulation(simulation_result):
	data = pd.DataFrame(simulation_result)
	data['date'] = pd.to_datetime(data['date'])

	p = figure(plot_width=800, plot_height=450, responsive=True, x_axis_type='datetime')
	p.title.text = "Simulation Flow Rate"

	for series, name, color in zip(['q_rec', 'q_sim'], ['Recorded', 'Simulated'], ['#404387', '#79D151']):
		p.line(data['date'], data[series], color=color, alpha=0.8, legend=name)

	p.legend.location = "top_left"
	p.legend.click_policy='hide'

	script, div = components(p)
	return script, div
	