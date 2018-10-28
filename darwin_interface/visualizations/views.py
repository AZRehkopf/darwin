from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Graph, DataPoint

import json

def index(request):
	graph_list = Graph.objects.order_by('pub_date')
	
	labels = []
	exec_data = []
	gen_data = []
	for graph in graph_list:
		for point in graph.datapoint_set.all():
			labels.append(point.population_size)
			exec_data.append(point.avg_execution_time)
			gen_data.append(point.avg_generations)

	data = 	{
		'labels': labels,
		'exec_data': exec_data,
		'gen_data': gen_data,
	}

	data = json.dumps(data)

	template = loader.get_template('visualizations/index.html')
	context = {
			'graph_list': graph_list,
			'data': data,
	}
	return HttpResponse(template.render(context, request))	