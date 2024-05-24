from algorithms.black_hole import BlackHole
from algorithms.genetic_algorithm import GeneticAlgorithm
from algorithms.lagrangian_heuristics import LagrangianHeuristics
from algorithms.simulated_annealing import SimulatedAnnealing
from services.generation import Test


class GA_SA:
    def __init__(self, test: Test) -> None:
        self.test = test

    def start(self, count_chromosomes, mutation_frequency, selection_percentage, crossover_percentage, fine_rules,
              count_iteration1, initial_temperature, count_iteration2, optimum=None):
        genetic_alg = GeneticAlgorithm(self.test)
        simulated_ann = SimulatedAnnealing(self.test)
        res1 = genetic_alg.start(count_chromosomes, mutation_frequency, selection_percentage, crossover_percentage,
                                 fine_rules, count_iteration1, time_limit=150, optimum=optimum)
        res2 = simulated_ann.start(initial_temperature, count_iteration2, list(res1[2]), time_limit=150,
                                   optimum=optimum)
        return [res1[0], res2[0]], res1[1] + [res1[1][-1] + i for i in res2[1]], res2[2]


class LH_SA:
    def __init__(self, test: Test) -> None:
        self.test = test

    def start(self, count_iteration1, initial_temperature, count_iteration2, optimum=None):
        lagrange_alg = LagrangianHeuristics(self.test)
        simulated_ann = SimulatedAnnealing(self.test)
        res1 = lagrange_alg.start(count_iteration1, time_limit=150, optimum=optimum)
        res2 = simulated_ann.start(initial_temperature, count_iteration2, list(res1[2]), time_limit=150,
                                   optimum=optimum)
        return [res1[0], res2[0]], res1[1] + [res1[1][-1] + i for i in res2[1]], res2[2]


class BH_SA:
    def __init__(self, test: Test) -> None:
        self.test = test

    def start(self, count_iteration1, count_stars, initial_temperature, count_iteration2, optimum=None):
        black_hole_alg = BlackHole(self.test)
        simulated_ann = SimulatedAnnealing(self.test)
        res1 = black_hole_alg.start(count_iteration1, count_stars, True, time_limit=150, optimum=optimum)
        res2 = simulated_ann.start(initial_temperature, count_iteration2, list(res1[2]), time_limit=150,
                                   optimum=optimum)
        return [res1[0], res2[0]], res1[1] + [res1[1][-1] + i for i in res2[1]], res2[2]


class LH_BH:
    def __init__(self, test: Test) -> None:
        self.test = test

    def start(self, count_iteration1, count_iteration2, count_stars, optimum=None):
        lagrange_alg = LagrangianHeuristics(self.test)
        black_hole_alg = BlackHole(self.test)
        res1 = lagrange_alg.start(count_iteration1, time_limit=30, optimum=optimum)
        res2 = black_hole_alg.start(count_iteration2, count_stars, True, res1[2], 200,
                                    time_limit=270, optimum=optimum)
        return [res1[0], res2[0]], res1[1] + [res1[1][-1] + i for i in res2[1]], res2[2]


class SA_GA:
    def __init__(self, test: Test) -> None:
        self.test = test

    def start(self, initial_temperature, count_iteration1, count_chromosomes, mutation_frequency, selection_percentage,
              crossover_percentage, fine_rules, count_iteration2, optimum=None):
        simulated_ann = SimulatedAnnealing(self.test)
        genetic_alg = GeneticAlgorithm(self.test)
        initial_population = []
        res1s = []
        for _ in range(count_chromosomes):
            res1 = simulated_ann.start(initial_temperature, count_iteration1, time_limit=150 / count_chromosomes,
                                       optimum=optimum)
            initial_population.append(res1[2])
            res1s.append(res1)

        res2 = genetic_alg.start(count_chromosomes, mutation_frequency, selection_percentage, crossover_percentage,
                                 fine_rules, count_iteration2, initial_population, time_limit=150, optimum=optimum)
        res1 = min(res1s, key=lambda x: min(x[0]))
        return [res1[0], [res1[0][-1]] + res2[0]], res1[1] + [res1[1][-1] + i for i in res2[1]], res2[2]
