# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from .hbvcore import hbv96
import json

import pandas as pd
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import BoxZoomTool, HoverTool, PanTool, RedoTool, ResetTool, SaveTool, UndoTool, WheelZoomTool
from bokeh.embed import components

# Create HBV object
mcd = hbv96.HBV96()

mcd.par['area'] = 33.5

mcd.par['tfac'] = 24

mcd.config['init_guess'] = None

mcd.DEF_q0 = 0.188

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
			context['plots'] = plot_simulation(mcd.data)
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

	script_q, div_q = plot_simu_q(data)
	script_p, div_p = plot_simu_p(data)
	script_t, div_t = plot_simu_t(data)
	script_etp, div_etp = plot_simu_etp(data)

	plots = dict(

		script=dict(
			q=script_q,
			p=script_p,
			t=script_t,
			etp=script_etp
			),

		div=dict(
			q=div_q,
			p=div_p,
			t=div_t,
			etp=div_etp
			)
		)
	return plots

def plot_simu_q(data):
	source = ColumnDataSource(data=dict(
		date=pd.to_datetime(data['date']),
		q_rec=data['q_rec'],
		q_sim=data['q_sim'],
		bias=(data['q_sim']-data['q_rec']),
	))

	hover = HoverTool(
		names=['Recorded',],
	    tooltips=[
	        ( 'date', '@date{%F}' ),
	        ( 'Simulated', '@q_sim{0.000 a}' ),
	        ( 'Recorded', '@q_rec{0.000 a}' ), # use @{ } for field names with spaces
	    ],
	    formatters={
	        'date' : 'datetime', # use 'datetime' formatter for 'date' field
	    },

	    # display a tooltip whenever the cursor is vertically in line with a glyph
	    mode='vline',
	)
	tools = [PanTool(), WheelZoomTool(dimensions="width"),
		BoxZoomTool(dimensions="width"), UndoTool(), RedoTool(),
		ResetTool(),hover, SaveTool()]

	p = figure(plot_width=800, plot_height=450, tools=tools, 
		responsive=True, x_axis_type='datetime')
	p.title.text = "Simulation Flow Rate"

	for series, name, color in zip(['q_rec', 'q_sim'], ['Measured Discharge', 'Simulated Discharge'], ['#404387', '#79D151']):
		p.line('date', series, source=source, color=color, alpha=0.8, legend=name, name=name)

	p.legend.location = "top_center"
	p.legend.orientation = "horizontal"
	p.legend.click_policy='hide'
	
	return components(p)

def plot_simu_p(data):
	source = ColumnDataSource(data=dict(
		date=pd.to_datetime(data['date']),
		prec=data['prec'],
		sp=data['sp'],
	))

	hover = HoverTool(
		names=['sp',],
	    tooltips=[
	        ( 'date', '@date{%F}' ),
	        ( 'Snow Pack', '@sp{0.000 a}' ),
	        ( 'Precipitation', '@prec{0.000 a}' ), # use @{ } for field names with spaces
	    ],
	    formatters={
	        'date' : 'datetime', # use 'datetime' formatter for 'date' field
	    },

	    # display a tooltip whenever the cursor is vertically in line with a glyph
	    mode='vline',
	)
	tools = [PanTool(), WheelZoomTool(dimensions="width"),
		BoxZoomTool(dimensions="width"), UndoTool(), RedoTool(),
		ResetTool(),hover, SaveTool()]

	p = figure(plot_width=800, plot_height=450, tools=tools, responsive=True, x_axis_type='datetime')
	p.title.text = "Precipitation Records and Simulated Snow Pack"

	p.vbar(x='date', top='prec', bottom=0, width=1, source=source, color='#404387', 
		alpha=0.8, legend='Precipitation   ', name='Precipitation')
	p.line('date', 'sp', source=source, color='#79D151', 
		alpha=0.8, line_width=2, legend='Snow Pack', name='sp')

	p.legend.location = "top_center"
	p.legend.orientation = "horizontal"
	p.legend.click_policy= "hide"

	return components(p)

def plot_simu_t(data):
	source = ColumnDataSource(data=dict(
		date=pd.to_datetime(data['date']),
		t=data['temp'],
		tm=data['tm'],
		diff=(data['temp']-data['tm']),
	))

	hover = HoverTool(
		names=['Temperature',],
	    tooltips=[
	        ( 'date', '@date{%F}' ),
	        ( 'Measured Air Temperature', '@t{0.000 a}[°C]' ),
	        ( 'Long-term Average', '@tm{0.000 a}[°C]' ), # use @{ } for field names with spaces
	    ],
	    formatters={
	        'date' : 'datetime', # use 'datetime' formatter for 'date' field
	    },

	    # display a tooltip whenever the cursor is vertically in line with a glyph
	    mode='vline',
	)
	tools = [PanTool(), WheelZoomTool(dimensions="width"),
		BoxZoomTool(dimensions="width"), UndoTool(), RedoTool(),
		ResetTool(),hover, SaveTool()]

	p = figure(plot_width=800, plot_height=450, tools=tools, responsive=True, x_axis_type='datetime')
	p.title.text = "Air Temperature"

	for series, name, color, alpha in zip(['t', 'tm'], ['Temperature', 'LTA'], ['#DD4968','#440154'], [0.9, 0.7]):
		p.line('date', series, source=source, color=color, alpha=alpha, legend=name, name=name)

	p.legend.location = "top_center"
	p.legend.orientation = "horizontal"
	p.legend.click_policy='hide'


	return components(p)

def plot_simu_etp(data):
	source = ColumnDataSource(data=dict(
		date=pd.to_datetime(data['date']),
		sm=data['sm'],
		ep=data['ep'],
		q_rec=data['q_rec'],
	))

	hover = HoverTool(
		names=['sm',],
	    tooltips=[
	        ( 'date', '@date{%F}' ),
	        ( 'Evaporation', '@ep{0.000 a}' ),
	        ( 'Soil Moisture', '@sm{0.000 a}' ), 
	        ( 'Discharge', '@q_rec{0.000 a}' ), # use @{ } for field names with spaces
	    ],
	    formatters={
	        'date' : 'datetime', # use 'datetime' formatter for 'date' field
	    },

	    # display a tooltip whenever the cursor is vertically in line with a glyph
	    mode='vline',
	)
	tools = [PanTool(), WheelZoomTool(dimensions="width"),
		BoxZoomTool(dimensions="width"), UndoTool(), RedoTool(),
		ResetTool(),hover, SaveTool()]

	p = figure(plot_width=800, plot_height=450, tools=tools, 
		responsive=True, x_axis_type='datetime')
	p.title.text = "Simulation Flow Rate"

	for series, name, color in zip(['sm', 'ep', 'q_rec'], ['Soil Moisture', 'Measured Evaporation', 'Measured Discharge'], ['#79D151', '#DD4968', '#404387']):
		p.line('date', series, source=source, color=color, alpha=0.8, legend=name, name=series)

	p.legend.location = "top_center"
	p.legend.orientation = "horizontal"
	p.legend.click_policy='hide'
	
	return components(p)
	