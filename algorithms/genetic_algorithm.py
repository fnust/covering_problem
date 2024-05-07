from random import randint, choice, random

from tqdm import tqdm

from services.generation import Test
from services.visualization import Video, IMAGE_SIZE


class Chromosome:
    def __init__(self, genes: list | tuple, fitness_function_value: int, allowable: bool = True):
        self.genes = tuple(genes)
        self.fitness_function_value = fitness_function_value
        self.allowable = allowable


class GeneticAlgorithm:
    def __init__(self, test: Test):
        self.name = 'genetic_algorithm'
        self.test = test
        self.count_chromosomes = 0
        self.generation: list[Chromosome] = []

    def start(self, count_chromosomes: int, mutation_frequency: float = 1, selection_percentage: tuple = (0, 0, 100),
              crossover_percentage: tuple = (0, 100, 0, 0), fine_rules: tuple = (0, 0), visualization: bool = True,
              count_iteration: int = 10000, consistency_of_result: int = 10000) -> int:
        self.count_chromosomes = count_chromosomes
        selection = Selection(self.test.covering_objects_costs, count_chromosomes)
        current_selection = selection.random
        crossover = Crossover(self.test)
        current_crossover = crossover.random
        masks = []
        count_result_repetitions = 0
        count = 0
        result: Chromosome | list = []
        fine_amount = fine_rules[0]
        count_of_not_allowable = (fine_rules[1] * self.count_chromosomes) / 100
        self.__create_chromosomes(fine_amount, count_of_not_allowable)

        pbar = tqdm(total=count_iteration, colour='GREEN')
        while count < count_iteration and count_result_repetitions < consistency_of_result:
            pbar.update(1)
            old_result = result
            if round(count_iteration * sum(selection_percentage[:1]) / 100) == count:
                current_selection = selection.proportional
            if round(count_iteration * sum(selection_percentage[:2]) / 100) == count:
                current_selection = selection.elite

            if round(count_iteration * sum(crossover_percentage[:1]) / 100) == count:
                current_crossover = crossover.one_point
            if round(count_iteration * sum(crossover_percentage[:2]) / 100) == count:
                current_crossover = crossover.two_point
            if round(count_iteration * sum(crossover_percentage[:3]) / 100) == count:
                current_crossover = crossover.uniform

            self.generation = current_selection(self.generation)
            self.generation = self.__create_new_generation(current_crossover, mutation_frequency, fine_amount,
                                                           count_of_not_allowable)
            self.generation = current_selection(self.generation)
            result = sorted([chromosome for chromosome in self.generation if chromosome.allowable],
                            key=lambda x: self.calculate_cost(x.genes))[0]

            if old_result == result:
                count_result_repetitions += 1
            else:
                count_result_repetitions = 0
            masks.append(list(result.genes))
            count += 1

        if visualization:
            file_name = (f'{self.name}_{count_chromosomes}_{str(selection_percentage)}_'
                         f'{count_iteration}_{consistency_of_result}')
            video = Video(IMAGE_SIZE, self.test)
            video.create_video(masks, file_name)
        pbar.close()
        return self.calculate_cost(masks[-1])

    def __create_chromosomes(self, fine_amount, count_of_not_allowable):
        chromosomes = set()
        count = 0
        while len(chromosomes) < self.count_chromosomes:
            genes = [randint(0, 1) for _ in range(self.test.count_covering_objects)]
            count_fines = 0
            if fine_amount == 0 or count >= count_of_not_allowable:
                genes = self.__mutation(genes)
            else:
                count += 1
                if 1 not in genes:
                    genes = self.__mutation(genes)
                count_fines = self.calculate_fine(genes)
            chromosome = Chromosome(genes, self.fitness_function(genes) - count_fines * fine_amount, count_fines == 0)
            chromosomes.add(chromosome)
        self.generation = list(chromosomes)

    def __create_new_generation(self, crossover, frequency: float, fine_amount: int,
                                count_of_not_allowable: int) -> list:
        new_chromosomes = []
        for i in range(0, self.count_chromosomes, 2):
            new_chromosomes += crossover(list(self.generation[i].genes), list(self.generation[i + 1].genes))
        count = 0
        chromosomes = set(self.generation)
        for genes in new_chromosomes:
            probability = random()
            if probability < frequency:
                genes = self.__mutation(genes)
            count_fines = 0
            if fine_amount == 0 or count >= count_of_not_allowable:
                genes = self.fix_chromosome(genes)
            else:
                count += 1
                if 1 not in genes:
                    genes = self.__mutation(genes)
                count_fines = self.calculate_fine(genes)
            chromosome = Chromosome(genes, self.fitness_function(genes) - count_fines * fine_amount, count_fines == 0)
            chromosomes.add(chromosome)
        return list(chromosomes)

    def __mutation(self, genes: list) -> list:
        position = randint(0, self.test.count_covering_objects - 1)
        genes[position] = 1 - genes[position]
        return genes

    def fix_chromosome(self, chromosome: list):
        uncovered_objects = set()
        columns_count_in_coverage = [0] * self.test.count_objects_to_be_covered
        b: list[list[int]] = [[] for _ in range(self.test.count_covering_objects)]
        a: list[list[int]] = [[] for _ in range(self.test.count_objects_to_be_covered)]

        for i in range(self.test.count_objects_to_be_covered):
            columns_count_in_coverage[i] = sum([x * y for x, y in zip(chromosome, self.test.coverage_array[i])])
            if columns_count_in_coverage[i] == 0:
                uncovered_objects.add(i)
            for j in range(self.test.count_covering_objects):
                if self.test.coverage_array[i][j] == 1:
                    b[j].append(i)
                    a[i].append(j)
        while len(uncovered_objects) != 0:
            i = list(uncovered_objects)[0]
            j = sorted(a[i], key=lambda k: self.calculate_significance(k, uncovered_objects, b[k]))[0]
            chromosome[j] = 1
            for v in b[j]:
                columns_count_in_coverage[v] += 1
            uncovered_objects = uncovered_objects.difference(b[j])
        for j in sorted([k for k in range(self.test.count_covering_objects) if chromosome[k] == 1],
                        key=lambda x: -self.test.covering_objects_costs[x]):
            if len([i for i in b[j] if columns_count_in_coverage[i] < 2]) == 0:
                chromosome[j] = 0
                for i in b[j]:
                    columns_count_in_coverage[i] -= 1
        return chromosome

    def calculate_significance(self, k, uncovered_objects, j):
        return self.test.covering_objects_costs[k] / len(uncovered_objects.intersection(j))

    def calculate_fine(self, genes: list):
        count_fines = 0
        for object_to_be_covered in self.test.coverage_array:
            if 1 not in [a * b for a, b in zip(genes, object_to_be_covered)]:
                count_fines += 1
        return count_fines

    def calculate_cost(self, genes: list | tuple):
        return sum([a * b for a, b in zip(genes, self.test.covering_objects_costs)])

    def fitness_function(self, genes: list | tuple):
        return sum(self.test.covering_objects_costs) - self.calculate_cost(genes) + 1


class Selection:
    def __init__(self, costs: list[int], count: int):
        self.max_cost = sum(costs)
        self.count = count

    def random(self, chromosomes: list[Chromosome]) -> list:
        new_generation = set()
        while len(new_generation) < self.count:
            chromosome = choice(list(chromosomes))
            if chromosome not in new_generation:
                new_generation.add(chromosome)
                chromosomes.remove(chromosome)
        return list(new_generation)

    def elite(self, chromosomes: list[Chromosome]) -> list:
        return sorted(chromosomes, key=lambda x: x.fitness_function_value, reverse=True)[:self.count]

    def proportional(self, chromosomes: list[Chromosome]) -> list:
        proportion = [0]
        weight = []
        all_fitness = [chromosome.fitness_function_value for chromosome in chromosomes]
        min_val = min(all_fitness, key=lambda x: abs(x))
        all_fitness = [val if val > 0 else min_val for val in all_fitness]
        sum_fitness = sum(all_fitness)
        for val in all_fitness:
            weight.append(val / sum_fitness)
            proportion += [proportion[-1] + weight[-1]]
        proportion[-1] = 1
        new_generation = list()

        while len(new_generation) < self.count:
            probability = random()
            for i in range(1, len(chromosomes) + 1):
                if probability < proportion[i]:
                    new_generation.append(chromosomes[i - 1])
                    break
        return list(new_generation)


class Crossover:
    def __init__(self, test):
        self.test = test

    def one_point(self, parent_1, parent_2) -> list:
        separation = randint(2, self.test.count_covering_objects - 3)
        new_chromosome_1 = parent_1[:separation] + parent_2[separation:]
        new_chromosome_2 = parent_2[:separation] + parent_1[separation:]

        return [new_chromosome_1, new_chromosome_2]

    def two_point(self, parent_1, parent_2):
        separation_1 = randint(2, self.test.count_covering_objects - 3)
        separation_2 = randint(separation_1, self.test.count_covering_objects - 2)
        new_chromosome_1 = parent_1[:separation_1] + parent_2[separation_1:separation_2] + parent_1[separation_2:]
        new_chromosome_2 = parent_2[:separation_1] + parent_1[separation_1:separation_2] + parent_2[separation_2:]

        return [new_chromosome_1, new_chromosome_2]

    def uniform(self, parent_1, parent_2):
        cost_1 = sum([a * b for a, b in zip(parent_1, self.test.covering_objects_costs)])
        cost_2 = sum([a * b for a, b in zip(parent_2, self.test.covering_objects_costs)])
        probability = cost_1 / (cost_1 + cost_2)
        parents = [parent_1, parent_2]
        new_chromosome_1 = [parents[random() < probability][i] for i in range(self.test.count_covering_objects)]
        new_chromosome_2 = [parents[random() < probability][i] for i in range(self.test.count_covering_objects)]

        return [new_chromosome_1, new_chromosome_2]

    def random(self, parent_1, parent_2):
        parents = [parent_1, parent_2]
        new_chromosome_1 = [parents[randint(0, 1)][i] for i in range(self.test.count_covering_objects)]
        new_chromosome_2 = [parents[randint(0, 1)][i] for i in range(self.test.count_covering_objects)]

        return [new_chromosome_1, new_chromosome_2]
