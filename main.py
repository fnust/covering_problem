from algorithms.black_hole import BlackHole
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

INITIAL_TEMPERATURE = 10000

simulated_annealing = SimulatedAnnealing(test)
print(simulated_annealing.name, '*',
      simulated_annealing.start(INITIAL_TEMPERATURE, count_iteration=100, visualization=False))


lag = LagrangianHeuristics(test)
print(lag.name, '*', lag.start(100, visualization=False))

black_hole_alg = BlackHole(test)
print(black_hole_alg.name, '*', black_hole_alg.start(100, 20, visualization=False))
