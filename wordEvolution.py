# Base Python Imports
import string 
import random 
import json
import os 
import time
from operator import itemgetter

# Third Party Imports 
from numpy import linspace

class WordEvolution():	
	def __init__(self, **kwargs):
		if 'file_name' in kwargs:
			self.load_config(kwargs['file_name'])
		elif 'json' in kwargs:
			self.load_json_config(kwargs['json'])

		# Dependant Experiment Variables
		self.WORD_LENGTH = len(self.GOAL)
		self.MUTATIONS_PER_BREEDER = int(self.POP_SIZE / self.NUM_OF_BREEDERS)
		self.RANDOM_BREEDERS = self.NUM_OF_BREEDERS - self.FIT_BREEDERS
		
		# System Environment Variables
		self.START_TIME = time.time()
		self.LOG_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'log.json')
		
		# Class Variables
		self.log_data = []
		self.population = self.generate_population()
		self.fitness = self.check_population_fitness()
		self.generation = 1
		self.complete = False

	def load_file_config(self, config_file):
		config_data = None
		with open(config_file) as config:
			config_data = json.load(config)

		# Independant Experiment Variables
		self.GOAL = config_data['variables']['goal']
		self.POP_SIZE = config_data['variables']['population_size']
		self.MUTATIONS = config_data['variables']['mutations']
		self.NUM_OF_BREEDERS = config_data['variables']['num_of_breeders']
		self.FIT_BREEDERS = config_data['variables']['fit_breeders']

		# Settings
		self.LOG_ALL_GENERATIONS = config_data['settings']['log_all_generations']

	def load_json_config(self, json_data):
		self.GOAL = json_data['goal']
		self.POP_SIZE = json_data['population_size']
		self.MUTATIONS = json_data['mutations']
		self.NUM_OF_BREEDERS = json_data['num_of_breeders']
		self.FIT_BREEDERS = json_data['fit_breeders']

		# Settings
		self.LOG_ALL_GENERATIONS = False

	def generate_population(self):
		population = []
		
		for individual in range(self.POP_SIZE):
			guess = ""
			for char in range(self.WORD_LENGTH):
				guess = guess + random.choice(string.ascii_lowercase)
			population.append(guess)
		
		return population

	def check_fitness(self, individual):
		assert len(individual) == len(self.GOAL)
		
		count = 0 
		for char_a, char_b in zip(individual, self.GOAL):
			if char_a == char_b:
				count = count + 1

		return count/len(self.GOAL)

	def check_population_fitness(self):
		pop_fitness = []

		for individual in self.population:
			fitness = self.check_fitness(individual)
			pop_fitness.append(fitness)

		return pop_fitness

	def select_breeders(self):
		pop_fit_pair = []
		
		for individual, fit_score in zip(self.population, self.fitness):
			tup = (individual, fit_score)
			pop_fit_pair.append(tup)

		pop_fit_pair = sorted(pop_fit_pair, key=itemgetter(1), reverse=True)

		fittest = pop_fit_pair[:self.FIT_BREEDERS]
		luckiest = random.sample(pop_fit_pair[self.FIT_BREEDERS:], self.RANDOM_BREEDERS)

		return fittest + luckiest

	def generate_children(self, breeders):
		parents = []
		children = []
		
		for tup in breeders:
			parents.append(tup[0])

		for individual in parents:
			for child in range(self.MUTATIONS_PER_BREEDER):
				temp_list = list(individual)
				for mut in range(self.MUTATIONS):
					idx = random.randint(0,self.WORD_LENGTH - 1)
					temp_list[idx] = random.choice(string.ascii_lowercase)

				children.append("".join(temp_list))

		return children

	def advance_one_generation(self):
		self.breeders = self.select_breeders()
		self.population = self.generate_children(self.breeders)
		self.fitness = self.check_population_fitness()
		if self.LOG_ALL_GENERATIONS: self.log_generation_stats()
		self.generation = self.generation + 1

		if 1.0 in self.fitness:
			self.complete = True
			if self.LOG_ALL_GENERATIONS: self.log_final_generation()

	def evolve(self):
		while not self.complete:
			self.advance_one_generation()

		return self.get_evolution_stats()
		
	def log_generation_stats(self):
		log_entry = {'generation ' + str(self.generation): self.breeders}
		self.log_data.append(log_entry)

		with open(self.LOG_FILE, mode='w', encoding='utf-8') as log:
			json.dump(self.log_data, log, indent=4)

	def log_final_generation(self):
		self.breeders = self.select_breeders()
		self.log_generation_stats()

	def get_evolution_stats(self):
		data = {'generations': self.generation, 'execution_time': time.time() - self.START_TIME}
		return data

class EvolutionBatch():
	def __init__(self):
		self.iterations = 100
		self.LOG_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'experiment_log.json')

		# Config Vars
		self.LENGTH = 16
		self.pop_size = 100
		self.mutations = 1
		self.survival_rate = 0.1
		self.fittest_selection_rate = 0.8

		# Results
		self.results = []
		self.log_values = []
		
	def run_experiment(self, config):
		experiment = WordEvolution(json=config)
		results = experiment.evolve()
		return results

	def generate_goal_word(self):
		goal_word = ""
		for num in range(self.LENGTH):
			goal_word = goal_word + random.choice(string.ascii_lowercase)

		return goal_word

	def generate_config(self):
		return {"goal": self.generate_goal_word(), "population_size": self.pop_size, "mutations": self.mutations, "num_of_breeders": int(self.survival_rate * self.pop_size), "fit_breeders": int(self.survival_rate * self.pop_size * self.fittest_selection_rate)}

	def run_experiment_batch(self):
		for i in range(self.iterations):
			result = self.run_experiment(self.generate_config())
			self.results.append(result)

		return self.analyze_results()

	def analyze_results(self):
		generations_total = 0
		execution_total = 0
		for result in self.results:
			generations_total += result['generations']
			execution_total += result['execution_time']

		return {'measurements':{'avg_generations': int(generations_total/self.iterations), 'avg_execution_time': execution_total/self.iterations}, 'test_params': {'iterations': self.iterations, 'word_length':self.LENGTH, 'population_size': self.pop_size, 'mutations': self.mutations, 'num_of_breeders': int(self.survival_rate * self.pop_size), 'fit_breeders': int(self.survival_rate * self.pop_size * self.fittest_selection_rate)}}

	def vary_pop_size(self, init, delta, final):
		for value in range(init, final, delta):
			self.pop_size = value
			result = batch.run_experiment_batch()
			self.log_result(result)
		self.pop_size = final
		result = batch.run_experiment_batch()
		self.log_result(result)

	def vary_mutations(self, init, delta, final):
		for value in range(init, final, delta):
			self.mutations = value
			result = batch.run_experiment_batch()
			self.log_result(result)
		self.mutations = final
		result = batch.run_experiment_batch()
		self.log_result(result)

	def vary_survival_rate(self, init, final, segmentations):
		for value in linspace(init,final,segmentations):
			self.survival_rate = value
			result = batch.run_experiment_batch()
			self.log_result(result)

	def vary_fittest_selection_rate(self, init, final, segmentations):
		for value in linspace(init,final,segmentations):
			self.fittest_selection_rate = value
			result = batch.run_experiment_batch()
			self.log_result(result)

	def log_result(self, result):
		self.log_values.append(result)
		with open(self.LOG_FILE, mode='w', encoding='utf-8') as log:
			json.dump(self.log_values, log, indent=4)
		
		self.results = []
	
if __name__ == '__main__':
	batch = EvolutionBatch()
	batch.vary_pop_size(100, 100, 1000)