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
			mcd.config.update(eval(post.get('config')))
			print mcd.config
			mcd.extract_to_dict()
			mcd.calibrate()
			context['res_head'] = json.dumps(mcd.data[:5])
			context['size'] = len(mcd.data)
			context['par'] = mcd.par
			return JsonResponse(context)
		elif action=='summarize':
			context['res_head'] = json.dumps(mcd.data[:5])
			context['size'] = len(mcd.data)
			return JsonResponse(context)
		else:
			return JsonResponse(context)
	else:
		return render(request, template)

