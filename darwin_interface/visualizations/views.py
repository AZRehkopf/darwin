from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Graph

def index(request):
	graph_list = Graph.objects.order_by('pub_date')
	template = loader.get_template('visualizations/index.html')
	context = {
			'graph_list': graph_list,
	}
	return HttpResponse(template.render(context, request))	