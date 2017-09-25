# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from .hbvcore.hbv96 import HBV96, DivergentError
import json

import numpy as np
import pandas as pd
from bokeh.embed import components
from bokeh.layouts import gridplot
from bokeh.models import LinearAxis, Legend, BoxZoomTool, HoverTool, PanTool, RedoTool, ResetTool, SaveTool, UndoTool, WheelZoomTool
from bokeh.models.ranges import Range1d
from bokeh.palettes import magma, plasma, viridis
from bokeh.plotting import figure, ColumnDataSource

# Create HBV object
mcd = HBV96()

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
			mcd.data = json.loads(post.get('data'))
			return JsonResponse(context)

		elif action=='simulate':
			mcd.data = json.loads(post.get('data'))
			mcd.config.update(json.loads(post.get('config')))
			mcd.par.update(json.loads(post.get('par')))
			mcd.DEF_ST.update(json.loads(post.get('st')))
			mcd._simulate_without_calibration()
			context['par'] = mcd.par
			context['plots'] = plot_simulation(mcd.data)
			context['data'] = mcd.data
			context['inters'] = mcd.int_tab
			return JsonResponse(context)

		elif action=='calibrate':
			mcd.data = json.loads(post.get('data'))
			mcd.config.update(json.loads(post.get('config')))
			mcd.par.update(json.loads(post.get('par')))
			mcd.calibrate()
			context['par'] = mcd.par
			context['plots'] = plot_simulation(mcd.data)
			context['data'] = mcd.data
			context['inters'] = mcd.int_tab
			return JsonResponse(context)
		
		elif action=='summarize':
			context['summary'] = json.dumps(mcd.summary())
			context['size'] = len(mcd.data)
			return JsonResponse(context)

		elif action=='save_bounds':
			mcd.P_LB = json.loads(post.get('P_LB'))
			mcd.P_UB = json.loads(post.get('P_UB'))
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

def plot_simu_st_without_snow(source):

	hover = HoverTool(
		names=['sm',],
	    tooltips=[
	        ( 'date', '@date{%F}' ),
	        ( 'Soil Moisture', '@sm{0.000 a}' ), 
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
	lines = ['sm', 'uz', 'lz']
	names =  ['Soil Moisture', 'Upper Zone', 'Lower Zone']
	colors = plasma(3)

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
	qq_plot = plot_qqplot(source)
	roc_plot = plot_roc(source)
	grid = gridplot(children=[[qq_plot, roc_plot]], plot_width=700, 
		plot_height=800,responsive=True)
	return grid

def plot_qqplot(source):
	_range = len(source.data['qt_sim'])-1
	tools = [PanTool(), WheelZoomTool(dimensions="width"),
		BoxZoomTool(dimensions="width"), UndoTool(), RedoTool(),
		ResetTool(), SaveTool()]

	p = figure(plot_width=320, plot_height=320, tools=tools,
			toolbar_location='above')
	p.title.text = "Q-Q Plot"
	p.xaxis.axis_label = "Simulated Discharge Quantile [-]"
	p.yaxis.axis_label = "Recorded Discharge Quantile [-]"

	qts = p.circle(x='qt_sim', y='qt_rec', source=source, color='#404387', 
		alpha=0.8, name='quantile', size=2)

	straightline = p.line(x=[0, 1], y= [0, 1], color='red',
		alpha=0.8, name='y=x', line_width=3)

	legend = Legend(
		items=[
			('Q-norm', [qts]),
			('y = x', [straightline]),
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

def plot_roc(source):
	'''
	Import sklearn locally to generate roc curve
	'''
	from sklearn.metrics import roc_curve, auc
	from bokeh.models import Label

    # Compute ROC curve and area the curve
	fpr, tpr, thresholds = roc_curve(source.data['qt_bin'], source.data['qt_sim'])
	roc_auc = auc(fpr, tpr)

    # Ploting
	tools = [PanTool(), WheelZoomTool(dimensions="width"),
		BoxZoomTool(dimensions="width"), UndoTool(), RedoTool(),
		ResetTool(), SaveTool()]

	p = figure(plot_width=320, plot_height=320, tools=tools,
			toolbar_location='above')
	p.title.text = "ROC Curve"
	p.xaxis.axis_label = "FPR (False Positive Rate) [-]"
	p.yaxis.axis_label = "TPR (True Positive Rate) [-]"

	roc = p.line(x=fpr, y=tpr, color='#404387', 
		alpha=0.8, name='roc', line_width=2)

	straightline = p.line(x=[0, 1], y= [0, 1], color='red',
		alpha=0.8, name='y=x', line_width=3)

	legend = Legend(
		items=[
			('ROC', [roc]),
			('y = x', [straightline]),
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

	_auc = Label(x=0.7, y=0.25, text_font_size='1.1em',
		text_font_style='bold', text='AUC = {0:.3f}'.format(roc_auc))

	p.add_layout(legend, 'below')
	p.add_layout(_auc)
	
	return p

def plot_simulation(simulation_result):
	source = synthesize_data(simulation_result)

	# script_q, div_q = components(plot_simu_q(source))
	# script_p, div_p = components(plot_simu_p(source))
	# script_t, div_t = components(plot_simu_t(source))
	# script_etp, div_etp = components(plot_simu_etp(source))
	# if mcd.config['kill_snow']:
	# 	script_st, div_st = components(plot_simu_st_without_snow(source))
	# else:
	# 	script_st, div_st = components(plot_simu_st(source))
	script_perf, div_perf = components(plot_simu_perf(source))

	plots = dict(

		script=dict(
			# q=script_q,
			# p=script_p,
			# t=script_t,
			# etp=script_etp,
			# st=script_st,
			perf=script_perf
			),

		div=dict(
			# q=div_q,
			# p=div_p,
			# t=div_t,
			# etp=div_etp,
			# st=div_st,
			perf=div_perf
			)
		)

	return plots

def plot_all(source):
	return None

def synthesize_data(simulation_result):
	data = pd.DataFrame(simulation_result)

	# Range for processing residus
	_range = len(data)

	''' ---------- Calculate Quantile ---------- '''
	# Sort the two arrays
	asc_qsim = np.sort(data['q_sim'])

	def f_q(value, vec):
		'''
		Function to calculate the quantile of value in vec
		
		Input:
			value: 	Input value
			vec:   	Input vector
		
		Output:
			quantile: _count/float(len(vec))
		'''
		_count = 0
		for v in vec:
			if value >= v: _count+=1
		return _count/float(len(vec))
	
	qt_rec = [f_q(q, data['q_rec']) for q in asc_qsim]
	qt_sim = [i/float(_range) for i in xrange(1, _range+1)]
	qt_bin = [1 if np.abs(rec-sim)/sim<0.1 else 0 for rec, sim in zip(data['q_rec'],data['q_sim'])]

	''' ---------- Calculate Quantile END ---------- '''

	''' ----- Convert all np.nan values into "NaN" for Javascript -----'''

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
		qt_rec=qt_rec,						# Quantiles for simulated values in recorded values
		qt_sim=qt_sim,						# Quantiles for simulated values in simulated values
		qt_bin=qt_bin,						# Binary array for roc curve
	))
	return source
