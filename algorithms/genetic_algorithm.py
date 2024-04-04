from random import randint, choice, random

from tqdm import tqdm

from services.generation import Test
from services.visualization import Video, IMAGE_SIZE


class GeneticAlgorithm:
    def __init__(self, test: Test):
        self.name = 'genetic_algorithm'
        self.test = test
        self.count_chromosomes = 0
        self.generation = list()

    def start(self, count_chromosomes: int, percentage_proportional_selection: int = 0,
              visualization: bool = True, count_iteration: int = 10000, consistency_of_result: int = 10000) -> int:
        self.count_chromosomes = count_chromosomes
        selection = Selection(self.test.covering_objects_costs, count_chromosomes)
        crossover = Crossover(self.test)
        masks = []
        count_result_repetitions = 0
        count = 0
        self.__create_chromosomes()

        pbar = tqdm(total=count_iteration, colour='GREEN')
        while count < count_iteration and count_result_repetitions < consistency_of_result:
            pbar.update(1)
            old_result = selection.elite(self.generation)[0]
            if count_iteration * (1 - percentage_proportional_selection / 100) > count:
                self.generation = self.__create_new_generation(crossover.one_point)
                self.generation = selection.elite(self.generation)[:count_chromosomes]
            else:
                self.generation = selection.elite(self.generation)
                self.generation = self.__create_new_generation(crossover.one_point)
                self.generation = selection.elite(self.generation)
            result = selection.elite(self.generation)[0]
            if old_result == result:
                count_result_repetitions += 1
            else:
                count_result_repetitions = 0
            masks.append(result)
            count += 1

        if visualization:
            file_name = (f'{self.name}_{count_chromosomes}_{percentage_proportional_selection}_'
                         f'{count_iteration}_{consistency_of_result}')
            video = Video(IMAGE_SIZE, self.test)
            video.create_video(masks, file_name)
        pbar.close()
        return selection.calculate_cost(masks[-1])

    def __create_chromosomes(self):
        chromosomes = set()
        while len(chromosomes) < self.count_chromosomes:
            chromosome = [randint(0, 1) for _ in range(self.test.count_covering_objects)]
            while (position := self.__check_chromosome(chromosome)) >= 0:
                chromosome[position] = 1
            chromosomes.add(tuple(chromosome))
        self.generation = list(chromosomes)
        # self.generation = self.selection.elite(chromosomes)
        # self.generation = self.selection.proportional(chromosomes)

    def __check_chromosome(self, chromosome):
        for object_to_be_covered in self.test.coverage_array:
            if 1 not in [a * b for a, b in zip(chromosome, object_to_be_covered)]:
                return choice([i for i, v in enumerate(object_to_be_covered) if v == 1])
        return -1

    def __create_new_generation(self, crossover) -> list:
        new_chromosomes = []
        for i in range(0, self.count_chromosomes, 2):
            new_chromosomes += crossover(self.generation[i], self.generation[i + 1])

        chromosomes = set(self.generation)
        for chromosome in new_chromosomes:
            mutating_chromosome = self.__mutation(list(chromosome))
            while ((position := self.__check_chromosome(mutating_chromosome)) >= 0
                   or tuple(mutating_chromosome) in chromosomes):
                mutating_chromosome = self.__mutation(list(mutating_chromosome))
                mutating_chromosome[position] = 1
            chromosomes.add(tuple(mutating_chromosome))

        return list(chromosomes)

        # self.generation = self.selection.proportional(chromosomes)
        # self.generation = self.selection.elite(chromosomes)[:self.count_chromosomes]

    def __crossover(self, parent_1, parent_2):
        separation = randint(2, self.test.count_covering_objects - 3)
        new_chromosome_1 = parent_1[:separation] + parent_2[separation:]
        new_chromosome_2 = parent_2[:separation] + parent_1[separation:]

        return [new_chromosome_1, new_chromosome_2]

    def __mutation(self, chromosome: list) -> list:
        position = randint(0, self.test.count_covering_objects - 1)
        chromosome[position] = 1 - chromosome[position]
        return chromosome


class Selection:
    def __init__(self, costs: list[int], count: int):
        self.costs = costs
        self.max_cost = sum(costs)
        self.count = count

    def calculate_cost(self, chromosome: tuple) -> int:
        return sum([a * b for a, b in zip(chromosome, self.costs)])

    def elite(self, chromosomes: list) -> list:
        return sorted(chromosomes, key=lambda x: self.max_cost - self.calculate_cost(x) + 1, reverse=True)

    def proportional(self, chromosomes: list) -> list:
        proportion = [0]
        weight = []
        all_fitness = self.max_cost * len(chromosomes) - sum(
            [self.calculate_cost(chromosome) for chromosome in chromosomes]) + len(chromosomes)
        for chromosome in chromosomes:
            weight.append((self.max_cost - self.calculate_cost(chromosome) + 1) / all_fitness)
            proportion += [proportion[-1] + weight[-1]]
        proportion[-1] = 1

        new_generation = []

        while len(set(new_generation)) < self.count:
            probability = random()
            for i in range(1, len(chromosomes) + 1):
                if probability < proportion[i]:
                    if chromosomes[i - 1] not in new_generation:
                        new_generation.append(chromosomes[i - 1])
                    break

        # limit = 1
        # while len(new_generation) < self.count:
        #     probability = uniform(0, limit)
        #     for i in range(1, len(chromosomes) + 1):
        #         if probability < proportion[i]:
        #             # print(probability, proportion[i] - proportion[i - 1], weight[i - 1])
        #             new_generation.append(chromosomes[i - 1])
        #             del proportion[i]
        #             proportion = proportion[:i] + [x - weight[i - 1] for x in proportion[i:]]
        #             chromosomes.remove(new_generation[-1])
        #             del weight[i - 1]
        #             limit = proportion[-1]
        #             break

        return new_generation


class Crossover:
    def __init__(self, test):
        self.test = test

    def one_point(self, parent_1, parent_2):
        separation = randint(2, self.test.count_covering_objects - 3)
        new_chromosome_1 = parent_1[:separation] + parent_2[separation:]
        new_chromosome_2 = parent_2[:separation] + parent_1[separation:]

        return [new_chromosome_1, new_chromosome_2]

    def two_point(self, parent_1, parent_2):
        separation_1 = randint(2, self.test.count_covering_objects - 3)
        separation_2 = randint(separation_1, self.test.count_covering_objects - 3)
        # new_chromosome_1 = parent_1[:separation] + parent_2[separation:]
        # new_chromosome_2 = parent_2[:separation] + parent_1[separation:]

        return

    def uniform(self, parent_1, parent_2):
        return

    def random(self,parent_1, parent_2):
        return

