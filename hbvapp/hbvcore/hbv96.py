#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

		# A dictionary for model parameters
		self.par = dict()
		
		# A dictionary for model configurations
		self.config = dict()

		# A np.array-like df for both input and out put data
		self.data = list()

		# A np.array-like df for intermediate values
		self.int_tab = list()

	# Extract data to an array-like dict from csv file uploaded
	def extract_to_dict(self):
		if type(self.data) is list:
			pass
		else:
			self.data = pd.read_csv(StringIO(self.data),
									sep=self.config['separator'],
									header=self.config['header']).to_dict(orient='records')
			

	# Extract data to a pandas dataframe from csv file uploaded
	def extract_to_dataframe(self):
		self.data = pd.read_csv(StringIO(self.data),
								sep=self.config['separator'],
								header=self.config['header'])


class HBV96(HydroModel):
	""" Calss HBV96 << Hydromodel """
	'''
	Class HBV96 contains main calculation functions of the HBV96 model.
	'''
	""""""

	def _precipitation(self, intab, outab, int_tab):
		'''
		==============
		Precipitation
		==============

		Precipitaiton routine of the HBV96 model.

		If temperature is lower than self.par['ltt'], all the precipitation is considered as
		snow. If the temperature is higher than self.par['utt'], all the precipitation is
		considered as rainfall. In case that the temperature is between self.par['ltt'] and
		self.par['utt'], precipitation is a linear mix of rainfall and snowfall.

		Parameters
		----------
		intab['temp'] : float
		Measured temperature [C]
		self.par['ltt'] : float
		Lower temperature treshold [C]
		self.par['utt'] : float
		Upper temperature treshold [C]
		intab['prec'] : float 
		Precipitation [mm]
		self.par['rfcf'] : float
		Rainfall corrector factor
		self.par['sfcf'] : float
		Snowfall corrector factor

		Returns
		-------
		_rf : float
		Rainfall [mm]
		_sf : float
		Snowfall [mm]
		'''
		# To terminate the process if precipitation routine is in the list to kill
		if self.config['kill_snow']:
			int_tab['rf'] = intab['prec']
			int_tab['sf'] = 0.0
			return None

		if intab['temp'] <= self.par['ltt']:
			int_tab['rf'] = 0.0
			int_tab['sf'] = intab['prec']*self.par['sfcf']

		elif intab['temp'] >= self.par['utt']:
			int_tab['rf'] = intab['prec']*self.par['rfcf']
			int_tab['sf'] = 0.0

		else:
			int_tab['rf'] = (intab['temp']-self.par['ltt'])/(self.par['utt']-self.par['ltt']) * intab['prec'] * self.par['rfcf']
			int_tab['sf'] = (1.0-(intab['temp']-self.par['ltt'])/(self.par['utt']-self.par['ltt'])) * intab['prec'] * self.par['sfcf']


	def _snow(self, intab, outab, int_tab):
		'''
		====
		Snow
		====

		Snow routine of the HBV-96 model.

		The snow pack consists of two states: Water Content (wc) and Snow Pack 
		(sp). The first corresponds to the liquid part of the water in the snow,
		while the latter corresponds to the solid part. If the temperature is 
		higher than the melting point, the snow pack will melt and the solid snow
		will become liquid. In the opposite case, the liquid part of the snow will
		refreeze, and turn into solid. The water that cannot be stored by the solid
		part of the snow pack will drain into the soil as part of infiltration.

		Parameters
		----------
		self.par['cfmax'] : float 
		Day degree factor
		self.par['tfac'] : float
		Temperature correction factor
		intab['temp'] : float 
		Temperature [C]
		self.par['ttm'] : float 
		Temperature treshold for Melting [C]
		self.par['cfr'] : float 
		Refreezing factor
		self.par['cwh'] : float 
		Capacity for water holding in snow pack
		_rf : float 
		Rainfall [mm]
		_sf : float 
		Snowfall [mm]
		intab['wc'] : float 
		Water content in previous state [mm]
		intab['sp'] : float 
		snow pack in previous state [mm]

		Returns
		-------
		_inf : float 
		Infiltration [mm]
		intab['wc'] : float 
		Water content in posterior state [mm]
		_intab['sp'] : float 
		Snowpack in posterior state [mm]
		'''

		# To terminate the process if sonw routine is in the list to kill
		if self.config['kill_snow']:
			outab['sp'] = 0.0
			outab['wc'] = 0.0
			int_tab['inf'] = int_tab['rf']
			return None
		else: 
			pass

		if intab['temp'] > self.par['ttm']:

			if self.par['cfmax']*(intab['temp']-self.par['ttm']) < intab['sp']+int_tab['sf']:
				int_tab['melt'] = self.par['cfmax']*(intab['temp']-self.par['ttm'])
			else:
				int_tab['melt'] = intab['sp']+int_tab['sf']

			outab['sp'] = intab['sp'] + int_tab['sf'] - int_tab['melt']
			outab['wc'] = intab['wc'] + int_tab['melt'] + int_tab['rf']

		else:
			if self.par['cfr']*self.par['cfmax']*(self.par['ttm']-intab['temp']) < intab['wc']:
				int_tab['refr'] = self.par['cfr']*self.par['cfmax']*(self.par['ttm'] - intab['temp'])
			else:
				int_tab['refr'] = intab['wc'] + int_tab['rf']

			outab['sp'] = intab['sp'] + int_tab['sf'] + int_tab['refr']
			outab['wc'] = intab['wc'] - int_tab['refr'] + int_tab['rf']

		if outab['wc'] > self.par['cwh']*outab['sp']:
			int_tab['inf'] = outab['wc']-self.par['cwh']*outab['sp']
			outab['wc'] = self.par['cwh']*outab['sp']
		else:
			int_tab['inf'] = 0.0


	def _soil(self, intab, outab, int_tab):
		'''
		====
		Soil
		====

		Soil routine of the HBV-96 model.

		The model checks for the amount of water that can infiltrate the soil, 
		coming from the liquid precipitation and the snow pack melting. A part of 
		the water will be stored as soil moisture, while other will become runoff, 
		and routed to the upper zone tank.

		Parameters
		----------
		self.par['fc'] : float 
		Filed capacity
		self.par['beta'] : float 
		Shape coefficient for effective precipitation separation
		self.par['etf'] : float 
		Total potential evapotranspiration
		intab['temp'] : float 
		Temperature
		intab['tm'] : float 
		Average long term temperature
		self.par['e_corr'] : float 
		Evapotranspiration corrector factor
		self.par['lp'] : float _soil 
		wilting point
		self.par['tfac'] : float 
		Time conversion factor
		self.par['c_flux'] : float 
		Capilar flux in the root zone
		_act_inf : float 
		actual infiltration
		intab['ep'] : float 
		actual evapotranspiration
		intab['sm'] : float
		Previous soil moisture value
		intab['uz'] : float
		Previous Upper zone value

		Returns
		-------
		intab['sm'] : float 
		New value of soil moisture
		intab['uz'] : float 
		New value of direct runoff into upper zone
		'''

		int_tab['qdr'] = max(intab['sm'] + int_tab['inf'] - self.par['fc'], 0.0)
		int_tab['act_inf'] = max(int_tab['inf'] - int_tab['qdr'], 0.0)
		int_tab['r'] = ((intab['sm']/self.par['fc'])** self.par['beta']) * int_tab['act_inf']
		int_tab['ep_int'] = (1.0 + self.par['etf']*(intab['temp'] - intab['tm']))*self.par['e_corr']*intab['ep']
		int_tab['ea'] = max(int_tab['ep_int'], (intab['sm']/(self.par['lp']*self.par['fc']))*int_tab['ep_int'])

		int_tab['cf'] = self.par['c_flux']*((self.par['fc'] - intab['sm'])/self.par['fc'])
		outab['sm'] = max(intab['sm'] + int_tab['act_inf'] - int_tab['r'] + int_tab['cf'] - int_tab['ea'], 0.0)
		outab['uz'] = intab['uz'] + int_tab['r'] - int_tab['cf']


	def _response(self, intab, outab, int_tab):
		'''
		========
		Response
		========
		The response routine of the HBV-96 model.

		The response routine is in charge of transforming the current values of 
		upper and lower zone into discharge. This routine also controls the 
		recharge of the lower zone tank (baseflow). The transformation of units 
		also occurs in this point.

		Parameters
		----------
		self.par['tfac'] : float
		Number of hours in the time step
		self.par['perc'] : float
		Percolation value [mm\hr]
		self.par['alpha'] : float
		Response box parameter
		self.par['k'] : float
		Upper zone recession coefficient
		self.par['k1'] : float 
		Lower zone recession coefficient
		self.par['area'] : float
		Catchment self.par['area'] [Km2]
		intab['lz'] : float 
		Previous lower zone value [mm]
		intab['uz'] : float 
		Previous upper zone value before percolation [mm]
		qdr : float
		Direct runoff [mm]
		'''

		outab['lz'] = max(intab['lz'] + min(self.par['perc'], outab['uz']), 0.0)
		outab['uz'] = max(outab['uz'] - self.par['perc'], 0.0)

		int_tab['q0'] = self.par['k']*outab['uz']**(1.0 + self.par['alpha'])
		int_tab['q1'] = self.par['k1']*outab['lz']

		outab['uz'] = max(outab['uz'] - int_tab['q0'], 0.0)
		outab['lz'] = max(outab['lz'] - int_tab['q1'], 0.0)

		int_tab['gw'] = int_tab['q0'] + int_tab['q1']

		outab['q_sim'] = self.par['area']*(int_tab['gw'] + int_tab['qdr'])/(3.6*self.par['tfac'])


	def _routing(self):
		'''
		========
		Routing
		========
		The routing routine of the HBV-96 model.

		Runoff from the groundwater boxes is computed as the sum of two or 
		three linear outflow equations (K , K1) d−1, depending on whether SUZ is 
		above a threshold value. This runoff is finally transformed by a triangular weighting 
		function defined by the parameter MAXBAS to give the simulated runoff(mm d−1 ).

		Parameters
		----------
		mbas : MAXBAS
		'''
		MAXBAS = int(self.par['mbas'])

		if (MAXBAS == 1):
			return None

		h = [0.0]
		c = list()

		for i in xrange(1, MAXBAS+1):
			if (i < MAXBAS/2.0):
				h.append( 4.0*i/MAXBAS**2.0 )
				c.append( (h[i]+h[i-1])/2.0 )

			elif (i >= 1+MAXBAS/2.0):
				h.append( h[MAXBAS-i] )
				c.append( (h[i]+h[i-1])/2.0 )

			elif (i == MAXBAS/2.0):
				h.append( 1.0/i )
				c.append( (h[i]+h[i-1])/2.0 )

			else:
				h.append( h[MAXBAS-i] )
				c.append( h[i]/2.0+1.0/MAXBAS )

		for t in xrange(MAXBAS, self.config['miles']):
			_gw_routing = 0.0
			for k in xrange(MAXBAS):
				_gw_routing += self.int_tab[t-k].get('gw') * c[k]

			self.int_tab[t]['gw'] = _gw_routing

			self.data[t]['q_sim'] = self.par['area']*(_gw_routing + self.int_tab[t].get('qdr'))/(3.6*self.par.get('tfac'))

			if self.data[t]['q_sim'] > 1e4:
				try:
					message = {'t': t, 'tol': 1e4, 'value': 1}
					raise DivergentError(message)
				except DivergentError as e:
					print('At loop {0}, q_sim = {1} > {2}. Result in divergence !!! '.format(e.message.get('t'), e.message.get('value'), e.message.get('tol')))
					raise
			else:
				pass

		return None

	def _step_run(self):
		'''
		==================
		Run model function
		==================

		Function to execute the demanded routines. So basically, step-run is able
		to execute the whole set as well as a part of the 5 HBV routines.
		'''
		intermedia = list()
		for t in xrange(self.config['miles']):
			# Consider sub-hashtable i as input and (i+1) as output table
			intab = self.data[t]
			outab = self.data[t+1]
			tab = dict()
			self._precipitation(intab, outab, tab)
			self._snow(intab, outab, tab)
			self._soil(intab, outab, tab)
			self._response(intab, outab, tab)
			intermedia.append( dict(tab) )

		# To avoid out-of-range problem, because there are always T-1 intermediate values
		# que = intermedia[len(intermedia)-1]
		# intermedia.append(que)

		self.int_tab = list(intermedia)

		self._routing()

	def _nse(self, q_rec, q_sim):
		'''
		===
		NSE
		===

		Nash-Sutcliffe efficiency. Metric for the estimation of performance of the 
		hydrological model

		Parameters
		----------
		q_rec : array_like [n]
		Measured discharge [m3/s]
		q_sim : array_like [n] 
		Simulated discharge [m3/s]

		Returns
		-------
		f : float
		NSE value
		'''
		a = np.square(np.subtract(q_rec, q_sim))
		b = np.square(np.subtract(q_rec, np.nanmean(q_rec)))
		if a.any < 0.0:
			return(np.nan)
		f = 1.0 - (np.nansum(a)/np.nansum(b))
		return f


	def _rmse(self, q_rec, q_sim):
		'''
		====
		RMSE
		====

		Root Mean Squared Error. Metric for the estimation of performance of the 
		hydrological model.

		Parameters
		----------
		q_rec : array_like [n]
		Measured discharge [m3/s]
		q_sim : array_like [n] 
		Simulated discharge [m3/s]

		Returns
		-------
		f : float
		RMSE value
		'''
		erro = np.square(np.subtract(q_rec,q_sim))
		if erro.any < 0:
			return(np.nan)
		f = np.sqrt(np.nanmean(erro))
		return f

	def calibrate(self):
		'''
		=========
		Calibrate
		=========

		Run the calibration of the HBV-96. The calibration is used to estimate the
		optimal set of parameters that minimises the difference between 
		observations and modelled discharge.

		Parameters
		----------

		flow : array_like [n]
		Measurements of discharge [m3/s]
		intab['avg_prec'] : array_like [n]
		Average precipitation [mm/h]
		intab['temp'] : array_like [n]
		Average temperature [C]
		et : array_like [n]
		Potential Evapotranspiration [mm/h] 
		p2 : array_like [2]
		Problem parameter vector setup as:
		[self.par['tfac'], self.par['area']]
		init_st : array_like [5], optional
		Initial model states, [sp, sm, uz, lz, wc]. If unspecified, 
		[0.0, 30.0, 30.0, 30.0, 0.0] mm
		ll_temp : array_like [n], optional
		Long term average temptearature. If unspecified, calculated from intab['temp'].
		x_0 : array_like [18], optional
		First guess of the parameter vector. If unspecified, a random value
		will be sampled between the boundaries of the 
		x_lb : array_like [18], optional
		Lower boundary of the parameter vector. If unspecified, a random value
		will be sampled between the boundaries of the 
		x_ub : array_like [18], optional
		First guess of the parameter vector. If unspecified, a random value
		will be sampled between the boundaries of the
		obj_fun : function, optional
		Function that takes 2 parameters, recorded and simulated discharge. If
		unspecified, RMSE is used.
		wu : int, optional
		Warming up period. This accounts for the number of steps that the model
		is run before calculating the performance function.
		verbose : bool, optional
		If True, displays the result of each model evaluation when performing
		the calibration of the hydrological model.
		tol : float, optional
		Determines the tolerance of the solutions in the optimisaiton process.
		minimise : bool, optional
		If True, the optimisation corresponds to the minimisation of the 
		objective function. If False, the optimial of the objective function is
		maximised.
		fun_nam : str, optional
		Name of the objective function used in calibration. If unspecified, is
		'RMSE'

		Returns
		-------
		params : array_like [18]
		Optimal parameter set

		performance : float
		Optimal value of the objective function
		'''
		self._init_simu()
		x_0 = self.config['init_guess']
		
		def _cal_fun_minimize(par_to_optimize):
			self.par.update(dict(zip(self._ind[:18], par_to_optimize))) # Update the parameter dictionary
			_q_sim, _q_rec = self._simulate_for_calibration()

			# Index for calibration
			_begin = self.config['warm_up']+self.config['calibrate_from'].get('index')
			_end = self.config['calibrate_to'].get('index')+1
			
			perf = self.obj_fun(_q_rec[_begin:_end],
							_q_sim[_begin:_end])

			if self.config['verbose']:
				print('{0}: {1}'.format(self.config['fun_name'], perf))
			
			return perf
		
		def _cal_fun_maximize(par_to_optimize):
			self.par.update(dict(zip(self._ind[:18], par_to_optimize))) # Update the parameter dictionary
			_q_sim, _q_rec = self._simulate_for_calibration()
			
		# Index for calibration
			_begin = self.config['warm_up']+self.config['calibrate_from'].get('index')
			_end = self.config['calibrate_to'].get('index')+1
			
			perf = -self.obj_fun(_q_rec[_begin:_end],
							_q_sim[_begin:_end])

			if self.config['verbose']:
				print('{0}: {1}'.format(self.config['fun_name'], perf))
			
			return perf

		# Boundaries
		x_b = zip(self.P_LB, self.P_UB)

		# Initial guess
		if x_0 is None:
			x_0 = np.random.uniform(self.P_LB, self.P_UB)

		# Model optimisation
		if self.config['minimise']:
			par_cal = opt.minimize(_cal_fun_minimize, x_0, method='L-BFGS-B',
									bounds=x_b, tol=self.config['tol'])
		else:
			par_cal = opt.minimize(_cal_fun_maximize, x_0, method='L-BFGS-B',
									bounds=x_b, tol=self.config['tol'])
		
		self._performance = par_cal.fun

		return None

	def _simulate_for_calibration(self):
		self._step_run()
		_q_sim = map(lambda d: d.get('q_sim', np.nan), self.data)
		_q_rec = map(lambda d: d.get('q_rec', np.nan), self.data)
		
		return _q_sim, _q_rec

	def _simulate_without_calibration(self):
		self._init_simu()
		self._step_run()
		return None

	def _init_simu(self):
		self.config['miles'] = (len(self.data)-1)
		self.data[0].update(self.DEF_ST)
		self.data[0].update({'q_sim': self.DEF_q0})
		if self.config['obj_fun'] == 'RMSE':
			self.obj_fun = self._rmse
		elif self.config['obj_fun'] == 'NSE':
			self.obj_fun = self._nse
		else:
			pass
		
		return None

# Exceptions
class DivergentError(Exception):
	""" DivergentError """
	'''
	Error occurs when result numbers are out of machine precision and cause
	divergent floating point number calculations
	'''
	def __init__(self, message):
		self.message = message

	def __str__(self):
		return repr(self.message)