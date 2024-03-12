from algorithms.genetic_algorithm import GeneticAlgorithm
from algorithms.simulated_annealing import SimulatedAnnealing
from services.generation import GenerateMap, MAP_SIZE, Test

# # Generation
# RADIUS = 10
# COUNT_OBJECTS_TO_BE_COVERED = 50
# COUNT_COVERING_OBJECTS = 30
#
# objects_map = GenerateMap(MAP_SIZE, COUNT_OBJECTS_TO_BE_COVERED, COUNT_COVERING_OBJECTS, RADIUS)
# objects_map.save_data()

# Experiments
FILE = 'tests/test_50_30_20.txt'
COUNT_CHROMOSOMES = 20
COUNT_ITERATION = 100

test = Test()
test.load(FILE)

# genetic_alg = GeneticAlgorithm(test)
# genetic_alg.start(COUNT_CHROMOSOMES, 50, count_iteration=COUNT_ITERATION,
#                   consistency_of_result=30)

INITIAL_TEMPERATURE = 1000

simulated_annealing = SimulatedAnnealing(test)
simulated_annealing.start(INITIAL_TEMPERATURE, count_iteration=COUNT_ITERATION, visualization=False)
