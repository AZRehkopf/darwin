from operator import itemgetter
import string, random, json, os, time

class PasswordEvolution():	
	def __init__(self):
		self.GOAL = 'buzzword'
		self.WORD_LENGTH = len(self.GOAL)
		self.POP_SIZE = 100
		self.MUTATIONS = 1
		self.NUM_OF_BREEDERS = 10
		self.MUTATIONS_PER_BREEDER = int(self.POP_SIZE / self.NUM_OF_BREEDERS)
		self.FIT_BREEDERS = 8
		self.RANDOM_BREEDERS = self.NUM_OF_BREEDERS - self.FIT_BREEDERS
		self.START_TIME = time.time()
		
		self.LOG_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'log.json')
		self.LOG_ALL_GENERATIONS = True
		
		self.log_data = []
		self.population = self.generate_population()
		self.fitness = self.check_population_fitness()
		self.generation = 1
		self.complete = False

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

if __name__ == '__main__':
	experiment = PasswordEvolution()
	print(experiment.evolve())