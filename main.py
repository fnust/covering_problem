from algorithms.genetic_algorithm import GeneticAlgorithm
from algorithms.lagrangian_heuristics import LagrangianHeuristics  # , Test
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
#
test = Test()
test.load(FILE)

genetic_alg = GeneticAlgorithm(test)
print(genetic_alg.name, '*',
      genetic_alg.start(COUNT_CHROMOSOMES, 0.5, count_iteration=COUNT_ITERATION, consistency_of_result=30,
                        visualization=False, crossover_percentage=(25, 25, 25, 25), selection_percentage=(20, 20, 60),
                        fine_rules=(2000, 20)))

INITIAL_TEMPERATURE = 1000

simulated_annealing = SimulatedAnnealing(test)
print(simulated_annealing.name, '*',
      simulated_annealing.start(INITIAL_TEMPERATURE, count_iteration=400, visualization=False))

# test = Test([2, 3, 4, 5], [[1, 0, 1, 0], [1, 0, 0, 1], [0, 1, 1, 1]], 4, 3)
lag = LagrangianHeuristics(test)
print(lag.name, '*', lag.start(100, visualization=False))
