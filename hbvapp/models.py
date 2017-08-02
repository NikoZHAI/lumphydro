# -*- coding: utf-8 -*-
from django.db import models

class RunLog(models.Model):
	"""Run log class, contains par, config, and datafilepath"""
	OPERATION_CHOICES = (
		('simulation','Simulate'),
		('calibration', 'Calibrate')
	)

	comment = models.TextField()
	operation = models.CharField(
		max_length=12,
		choices=OPERATION_CHOICES,
		default='simulation'
	)

class Parameter(models.Model):
	'''Parameters for HBV modle'''
	runlog = models.ForeignKey(RunLog, on_delete=models.CASCADE)

	ltt = models.FloatField()
	utt = models.FloatField()
	ttm = models.FloatField()
	cfmax = models.FloatField()
	fc = models.FloatField()
	e_corr = models.FloatField()
	etf = models.FloatField()
	lp = models.FloatField()
	k = models.FloatField()
	k1 = models.FloatField()
	alpha = models.FloatField()
	beta = models.FloatField()
	alpha = models.FloatField()
	cwh = models.FloatField()
	cfr = models.FloatField()
	c_flux = models.FloatField()
	rfcf = models.FloatField()
	sfcf = models.FloatField()
	area = models.FloatField()
	tfac = models.PositiveSmallIntegerField()

class Configuration(models.Model):
	"""Configuration for operation"""
	SEPARATOR_CHOICES = (
		(',', 'Comma: ,'),
		(';', 'Semicolon: ;'),
		('\t', 'Tab: "\\t"')
	)
	OBJECT_FUNCTION_CHOICES = (
		('_rmse', 'RMSE'),
		('_nse', 'NSE')
	)

	runlog = models.ForeignKey(RunLog, on_delete=models.CASCADE)

	separator = models.CharField(max_length=3, default=',', choices=SEPARATOR_CHOICES)
	header = models.PositiveSmallIntegerField(default=0)
	warm_up = models.PositiveSmallIntegerField(default=10)
	obj_fun = models.CharField(max_length=5, default='_rmse', choices=OBJECT_FUNCTION_CHOICES)
	tol = models.FloatField(default=0.0001)
	minimise = models.BooleanField(default=True)
	verbose = models.BooleanField(default=False)