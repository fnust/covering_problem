import math
from math import exp
from random import randint, choice, random

from tqdm import tqdm

from services.generation import Test
from services.visualization import Video, IMAGE_SIZE


class SimulatedAnnealing:
    def __init__(self, test: Test):
        self.name = 'simulated_annealing'
        self.condition = []
        self.temperature = 0
        self.test = test

    def start(self, initial_temperature: int, visualization: bool = True, count_iteration: int = 10000,
              consistency_of_result: int = 10000) -> int:
        count_result_repetitions = 0
        masks = []
        count = 0
        self.temperature = initial_temperature

        self.__create_condition()
        pbar = tqdm(total=count_iteration, colour='GREEN')
        while count < count_iteration and count_result_repetitions < consistency_of_result:
            pbar.update(1)
            old_result = self.__value_of_energy(self.condition)
            new_condition = self.__change_condition()
            delta = self.__value_of_energy(new_condition) - self.__value_of_energy(self.condition)
            if delta >= 0 or self.__probability_of_acceptance(delta):
                self.condition = new_condition
            result = self.__value_of_energy(self.condition)
            if old_result == result:
                count_result_repetitions += 1
            else:
                count_result_repetitions = 0
            masks.append(self.condition)
            count += 1
            self.temperature = initial_temperature * self.__change_temperature(count + 1)

        if visualization:
            file_name = (f'{self.name}_{initial_temperature}_'
                         f'{count_iteration}_{consistency_of_result}')
            video = Video(IMAGE_SIZE, self.test)
            video.create_video(masks, file_name)
        pbar.close()
        return self.__value_of_energy(masks[-1])

    def __create_condition(self) -> None:
        condition = [randint(0, 1) for _ in range(self.test.count_covering_objects)]
        self.condition = self.fix_condition(condition)

    def fix_condition(self, condition: list):
        uncovered_objects = set()
        columns_count_in_coverage = [0] * self.test.count_objects_to_be_covered
        b: list[list[int]] = [[] for _ in range(self.test.count_covering_objects)]
        a: list[list[int]] = [[] for _ in range(self.test.count_objects_to_be_covered)]

        for i in range(self.test.count_objects_to_be_covered):
            columns_count_in_coverage[i] = sum([x * y for x, y in zip(condition, self.test.coverage_array[i])])
            if columns_count_in_coverage[i] == 0:
                uncovered_objects.add(i)
            for j in range(self.test.count_covering_objects):
                if self.test.coverage_array[i][j] == 1:
                    b[j].append(i)
                    a[i].append(j)
        while len(uncovered_objects) != 0:
            i = list(uncovered_objects)[0]
            j = sorted(a[i], key=lambda k: self.calculate_significance(k, uncovered_objects, b[k]))[0]
            condition[j] = 1
            for v in b[j]:
                columns_count_in_coverage[v] += 1
            uncovered_objects = uncovered_objects.difference(b[j])
        for j in sorted([k for k in range(self.test.count_covering_objects) if condition[k] == 1],
                        key=lambda x: -self.test.covering_objects_costs[x]):
            if len([i for i in b[j] if columns_count_in_coverage[i] < 2]) == 0:
                condition[j] = 0
                for i in b[j]:
                    columns_count_in_coverage[i] -= 1
        return condition

    def calculate_significance(self, k, uncovered_objects, j):
        return self.test.covering_objects_costs[k] / len(uncovered_objects.intersection(j))

    def __check_condition(self, condition: list) -> int:
        for object_to_be_covered in self.test.coverage_array:
            if 1 not in [a * b for a, b in zip(condition, object_to_be_covered)]:
                return choice([i for i, v in enumerate(object_to_be_covered) if v == 1])
        return -1

    def __change_condition(self) -> list:
        new_condition = self.condition.copy()
        weights = []
        all_weight = 0
        for j in range(self.test.count_covering_objects):
            weight = self.__value_of_object(j)
            all_weight += weight
            weights.append(weight)

        proportion = [0]
        for weight in weights:
            proportion.append(proportion[-1] + weight / all_weight)
        proportion[-1] = 1
        probability = random()
        for i in range(1, self.test.count_covering_objects + 1):
            if probability < proportion[i]:
                new_condition[i - 1] = 0
                break
        return self.fix_condition(new_condition)

    def __value_of_energy(self, condition: list) -> int:
        return sum([a * b for a, b in zip(condition, self.test.covering_objects_costs)])

    def __change_temperature(self, iteration: int) -> float:
        if self.temperature != 0:
            # self.temperature /= math.log10(iteration)
            return math.log(2) / math.log(iteration)

    def __probability_of_acceptance(self, delta: int) -> bool:
        probability = random()
        if self.temperature != 0:
            return probability < exp(delta / self.temperature)
        else:
            return False

    def __value_of_object(self, j):
        return self.test.covering_objects_costs[j] / sum([1 for obj in self.test.coverage_array if obj[j] == 1])
