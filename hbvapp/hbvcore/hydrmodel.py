#!/usr/bin/env python
# -*- coding: utf-8 -*-
# HBV-96 model class
from __future__ import division, print_function
import numpy as np
import scipy.optimize as opt
import pandas as pd
from StringIO import StringIO
from pandas import DataFrame


class HydroModel(object):
	"""docstring for HBV96"""

	"""Public Static Variables"""


	# Parameter index, 18 modifiable and 2 not
	_ind = ['ltt',
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
			'tfac', #Non-modifiable, nm of hrs in time step
			'area'	#Non-modifiable, catchment area
			]

	# Lower boundary parameters
	P_LB = [-1.5, 		#ltt
			0.001, 		#utt
			0.001, 		#ttm
			0.04, 		#cfmax [mm c^-1 h^-1]
			50.0, 		#fc
			0.6, 		#ecorr
			0.001, 		#etf
			0.2, 		#lp
			0.00042, 	#k [h^-1] upper zone
			0.0000042, 	#k1 lower zone
			0.001, 		#alpha
			1.0, 		#beta
			0.001, 		#cwh
			0.01, 		#cfr
			0.0, 		#c_flux
			0.001, 		#perc mm/h
			0.6, 		#rfcf
			0.4] 		#sfcf

	# Upper boundary parameters
	P_UB = [2.5, 		#ltt
			3.0, 		#utt
			2.0, 		#ttm
			0.4, 		#cfmax [mm c^-1 h^-1]
			500.0, 		#fc
			1.4, 		#ecorr
			5.0, 		#etf
			0.5, 		#lp
			0.0167, 	#k upper zone
			0.00062, 	#k1 lower zone
			1.0, 		#alpha
			6.0, 		#beta
			0.1, 		#cwh
			1.0, 		#cfr
			0.08, 		#c_flux - 2mm/day
			0.125, 		#perc mm/hr
			1.4, 		#rfcf
			1.4]		#sfcf

	# Initial status
	DEF_ST = {	'sp': 0.0,	#sp: Snow pack
				'sm': 30.0,	#sm: Soil moisture
				'uz': 30.0,	#uz: Upper zone direct runoff
				'lz': 30.0,	#lz: Lower zone direct runoff
				'wc': 0.0	#wc: Water content
				}		
					
	# Boundary conditions DataFrame
	BOUND = {"low": dict(zip(_ind[:18], P_LB)),
			"up": dict(zip(_ind[:18], P_UB))}

	# Initial flow rate		
	DEF_q0 = 0.183

	# HBV96 model initializer
	def __init__(self):
		self.par = dict()
		self.config = dict()
		self.data = list()

	# Render parameter function
	def render_par(self, obj_name, par_name):
		return	eval('self.'+obj_name+'[par_name]')

	# Set parameter function, external accessibility for Django
	def set_par(self, obj_name, par_name, value):
		exec('self.'+obj_name+'[par_name] = value')

	# Extract data to an array-like dict from csv file uploaded
	def extract_to_dict(self):
		self.data = pd.read_csv(StringIO(self.data),
								sep=self.config['separator'],
								header=self.config['header']).to_dict(orient='records')
		self.config['miles'] = (len(self.data)-1)

	# Extract data to a pandas dataframe from csv file uploaded
	def extract_to_dataframe(self):
		self.data = pd.read_csv(StringIO(self.data),
								sep=self.config['separator'],
								header=self.config['header'])
		self.config['miles'] = (len(self.data)-1)

	# Data checker/validator
	def data_checker(self):
		pass
