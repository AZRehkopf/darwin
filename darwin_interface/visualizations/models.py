from django.db import models

class Graph(models.Model):
	graph_title = models.CharField(max_length=200)
	pub_date = models.DateTimeField('date published')

class DataPoint(models.Model):
	parent_graph = models.ForeignKey(Graph, on_delete=models.CASCADE)
	avg_execution_time = models.FloatField()
	avg_generations = models.IntegerField(default=0)
	iterations = models.IntegerField(default=0)
	word_length = models.IntegerField(default=0)
	population_size = models.IntegerField(default=0)
	mutations = models.IntegerField(default=0)
	num_of_breeders = models.IntegerField(default=0)
	fit_breeders = models.IntegerField(default=0)