# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from .hbvcore import hbv96
import json

import numpy as np
import pandas as pd
from bokeh.embed import components
from bokeh.models import LinearAxis, Legend, BoxZoomTool, HoverTool, PanTool, RedoTool, ResetTool, SaveTool, UndoTool, WheelZoomTool
from bokeh.models.ranges import Range1d
from bokeh.palettes import magma, plasma, viridis
from bokeh.plotting import figure, ColumnDataSource

# Create HBV object
mcd = hbv96.HBV96()

mcd.par['area'] = 135.0

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

		elif action=='simulate':
			mcd.config.update(json.loads(post.get('config')))
			mcd.par.update(json.loads(post.get('par')))
			mcd.extract_to_dict()
			mcd._simulate_without_calibration()
			context['res_head'] = json.dumps(mcd.data[:5])
			context['size'] = len(mcd.data)
			context['par'] = mcd.par
			context['plots'] = plot_simulation(mcd.data)
			context['data'] = mcd.data
			return JsonResponse(context)

		elif action=='calibrate':
			mcd.config.update(json.loads(post.get('config')))
			mcd.extract_to_dict()
			mcd.calibrate()
			context['res_head'] = json.dumps(mcd.data[:5])
			context['size'] = len(mcd.data)
			context['par'] = mcd.par
			context['plots'] = plot_simulation(mcd.data)
			context['data'] = mcd.data
			return JsonResponse(context)
		
		elif action=='summarize':
			context['res_head'] = json.dumps(mcd.data[:5])
			context['size'] = len(mcd.data)
			return JsonResponse(context)

		else:
			return JsonResponse(context)
	else:
		return render(request, template)

'''
  ---------- Bokeh plots ------------
'''
def plot_simu_q(source):

	hover = HoverTool(
		names=['q_rec',],
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
		p.line('date', series, source=source, color=color, alpha=0.8, legend=name, name=series)

	p.legend.location = "top_center"
	p.legend.orientation = "horizontal"
	p.legend.click_policy='hide'
	
	return p

def plot_simu_p(source):

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

	return p

def plot_simu_t(source):

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


	return p

def plot_simu_etp(source):

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
	p.title.text = "Evaporation and Soil Moisture"

	for series, name, color in zip(['sm', 'ep', 'q_rec'], ['Soil Moisture', 'Measured Evaporation', 'Measured Discharge'], ['#79D151', '#DD4968', '#404387']):
		p.line('date', series, source=source, color=color, alpha=0.8, legend=name, name=series)

	p.legend.location = "top_center"
	p.legend.orientation = "horizontal"
	p.legend.click_policy='hide'
	
	return p

def plot_simu_gw():
	# To be implemented...
		pass	

def plot_simu_st(source):

	hover = HoverTool(
		names=['sm',],
	    tooltips=[
	        ( 'date', '@date{%F}' ),
	        ( 'Snow Pack', '@sp{0.000 a}' ),
	        ( 'Soil Moisture', '@sm{0.000 a}' ), 
	        ( 'Water Content', '@wc{0.000 a}' ),
	        ( 'Upper Zone', '@uz{0.000 a}' ),
	        ( 'Lower Zone', '@lz{0.000 a}' ), # use @{ } for field names with spaces
	    ],
	    formatters={
	        'date' : 'datetime', # use 'datetime' formatter for 'date' field
	    },

	    # display a tooltip whenever the cursor is vertically in line with a glyph
	    mode='mouse',
	)
	tools = [PanTool(), WheelZoomTool(dimensions="width"),
		BoxZoomTool(dimensions="width"), UndoTool(), RedoTool(),
		ResetTool(),hover, SaveTool()]

	p = figure(plot_width=800, plot_height=450, tools=tools, 
		responsive=True, x_axis_type='datetime')
	p.title.text = "Simulated States"

	renderers = []
	lines = ['sm', 'sp', 'wc', 'uz', 'lz']
	names =  ['Soil Moisture', 'Snow Pack', 'Water Content', 'Upper Zone', 'Lower Zone']
	colors = plasma(5)

	for series, color in zip(lines, colors):
		renderers.append([p.line('date', series, source=source, color=color, alpha=0.8, name=series)])

	legend = Legend(
		items=zip(names, renderers),
		location="center",
		orientation="horizontal",
		click_policy="hide",
		glyph_width = 40,
		padding=10,
		spacing=20,
		border_line_width=1,
		border_line_color='navy',
		margin=20,
		label_standoff=6
		)
	p.add_layout(legend, 'below')
	
	return p

def plot_simu_perf(source):
	_range = len(source.data['cumu_rmse'])-1
	hover = HoverTool(
		names=['cumu_rmse',],
	    tooltips=[
	        ( 'date', '@date{%F}' ),
	        ( 'Bias', '@bias{0.000 a}' ),
	        ( 'Cumulative SSE', '@cumu_sse{0.000 a}' ), # use @{ } for field names with spaces
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

	p = figure(plot_width=800, plot_height=450, tools=tools, responsive=True,
		x_axis_type='datetime', toolbar_location='above')
	p.y_range = Range1d( np.floor(min(source.data['bias'])), np.ceil(max(source.data['bias'])) )
	p.extra_y_ranges = {'y_sse': Range1d(np.ceil( source.data['cumu_sse'][_range]), 0)}
	p.title.text = "Performance Indicators"
	p.add_layout(LinearAxis(y_range_name='y_sse'), 'right')

	bias = p.vbar(x='date', top='bias', bottom=0, width=1, source=source, color='#404387', 
		alpha=0.8, name='bias')
	rmse_cumu = p.line('date', 'cumu_sse', source=source, color='red', alpha=0.8,
		name='cumu_sse', y_range_name='y_sse')

	legend = Legend(
		items=[
			('Bias', [bias]),
			('Cumulative RMSE', [rmse_cumu]),
			],
		location="center",
		orientation="horizontal",
		click_policy="hide",
		glyph_width = 40,
		padding=10,
		spacing=20,
		border_line_width=1,
		border_line_color='navy',
		margin=20,
		label_standoff=6
		)
	p.add_layout(legend, 'below')
	
	return p

def plot_simulation(simulation_result):
	source = synthesize_data(simulation_result)

	script_q, div_q = components(plot_simu_q(source))
	script_p, div_p = components(plot_simu_p(source))
	script_t, div_t = components(plot_simu_t(source))
	script_etp, div_etp = components(plot_simu_etp(source))
	script_st, div_st = components(plot_simu_st(source))
	script_perf, div_perf = components(plot_simu_perf(source))

	plots = dict(

		script=dict(
			q=script_q,
			p=script_p,
			t=script_t,
			etp=script_etp,
			st=script_st,
			perf=script_perf
			),

		div=dict(
			q=div_q,
			p=div_p,
			t=div_t,
			etp=div_etp,
			st=div_st,
			perf=div_perf
			)
		)

	return plots

def plot_all(source):

	q = plot_simu_q(source)
	p = plot_simu_p(source)
	t = plot_simu_t(source)
	etp = plot_simu_etp(source)
	st = plot_simu_st(source)
	perf = plot_simu_perf(source)

def synthesize_data(simulation_result):
	data = pd.DataFrame(simulation_result)

	''' ------- Calculate Residus ------- '''
	# Range for processing residus
	_range = len(data)+1

	# Calculate cumulative RMSE
	def _rmse(q_rec, q_sim):
		erro = np.square(np.subtract(q_rec,q_sim))
		if erro.any < 0:
			return(np.nan)
		f = np.sqrt(np.nanmean(erro))
		return f

	rmse = list()
	cumu_rmse = [0]
	for i in xrange(1, _range):
		this_rmse = _rmse(data['q_rec'][:i], data['q_sim'][:i])
		rmse.append(this_rmse)
		cumu_rmse.append( (this_rmse + cumu_rmse[i-1]) )
	cumu_rmse.pop(0)

	# Calculate cumulative SSE
	def _sse(q_rec, q_sim):		# q_rec and q_sim here are not vectors
		erro = np.square(np.subtract(q_rec,q_sim))
		if erro < 0:
			return(np.nan)
		else:
			return erro

	cumu_sse = [0]
	for i in xrange(1, (_range-1)):
		cumu_sse.append(_sse(data.at[i,'q_rec'], data.at[i, 'q_sim']) + cumu_sse[i-1])
	''' ---------- Calculate cumulative Residus END ---------- '''


	source = ColumnDataSource(data=dict(
		date=pd.to_datetime(data['date']),	# Date
		q_rec=data['q_rec'],				# Measured discharge
		q_sim=data['q_sim'],				# Simulated discharge
		bias=(data['q_sim']-data['q_rec']), # Bias of the model, difference between simulated and measured discharge
		prec=data['prec'],					# Precipitation
		sp=data['sp'],						# Simulated snow pack
		diff_temp=data['temp']-data['tm'],	# Difference 
		t=data['temp'],						# Air temperature
		tm=data['tm'],						# Long-term averaged air temperature
		sm=data['sm'],						# Soil moisture
		ep=data['ep'],						# Recorded evaporation
		wc=data['wc'],						# Water content
		uz=data['uz'],						# Upper zone value
		lz=data['lz'],						# Lower zone value
		cumu_rmse=cumu_rmse,				# Cumulative Root Mean Square Error
		cumu_sse=cumu_sse,					# Cumulative Square Standard Error
	))

	return source

