# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from .hbvcore import hbv96
import json

# Create HBV object
mcd = hbv96.HBV96()

mcd.par['area'] = 33.5

mcd.par['tfac'] = 24

mcd.config['header'] = 0

mcd.config['separator'] = ','

mcd.config['obj_fun'] = mcd._rmse

mcd.config['init_guess'] = None

mcd.config['fun_name'] = 'RMSE'

mcd.config['warm_up'] = 10

mcd.config['verbose'] = True

mcd.config['minimise'] = True

mcd.config['tol'] = 0.001

mcd.DEF_q0 = 0.183

# Home page.
@csrf_exempt
def home(request):
	global mcd
	template = 'hbvapp/home.html'
	context = {}
	if request.method == "POST" and request.is_ajax():
		mcd.data = request.POST.get('text')
		mcd.extract_to_dict()
		mcd.calibrate()
		context['res_head'] = json.dumps(mcd.data[:5])
		context['size'] = len(mcd.data)
		# Use JsonResponse just to interact with JQuery
		return JsonResponse(context)
	else:
		return render(request, template)
