import time
from math import exp, log
from random import randint, choice, random

from tqdm import tqdm

from services.generation import Test
from services.visualization import Video, IMAGE_SIZE

INF = 100000000000


class SimulatedAnnealing:
    def __init__(self, test: Test):
        self.name = 'simulated_annealing'
        self.condition = []
        self.temperature = 0
        self.test = test

    def start(self, initial_temperature: int, count_iteration: int = 10000, initial_condition=None,
              consistency_of_result: int = 1000, time_limit=300, visualization: bool = False, optimum=None):
        count_result_repetitions = 0
        masks = []
        count = 0
        results = []
        times = []
        start_time = time.time()
        self.temperature = initial_temperature
        if initial_condition is None:
            self.__create_condition()
        else:
            times = [0]
            results = [self.__value_of_energy(initial_condition)]
            self.condition = initial_condition
        pbar = tqdm(total=count_iteration, colour='GREEN')
        old_result = INF
        best_condition = []
        while count < count_iteration and count_result_repetitions < consistency_of_result:
            pbar.update(1)
            new_condition = self.__change_condition()
            delta = self.__value_of_energy(new_condition) - self.__value_of_energy(self.condition)
            if delta > 0 or self.__probability_of_acceptance(delta):
                self.condition = new_condition
            result = self.__value_of_energy(self.condition)
            if old_result < result:
                count_result_repetitions += 1
            else:
                old_result = result
                best_condition = self.condition.copy()
                count_result_repetitions = 0
            masks.append(self.condition)
            results.append(self.__value_of_energy(self.condition))
            times.append(time.time() - start_time)
            count += 1
            self.temperature = initial_temperature * self.__change_temperature(count + 1)
            if result == optimum:
                break
            if count_result_repetitions > consistency_of_result:
                break
            if times[-1] > time_limit:
                break

        if visualization:
            file_name = (f'{self.name}_{initial_temperature}_'
                         f'{count_iteration}_{consistency_of_result}')
            video = Video(IMAGE_SIZE, self.test)
            video.create_video(masks, file_name)
        pbar.close()
        return results, times, best_condition

    def __create_condition(self) -> None:
        condition = [randint(0, 1) for _ in range(self.test.count_covering_objects)]
        self.condition = self.fix_condition(condition)

    def fix_condition(self, condition: list):
        uncovered_objects = set()
        columns_count_in_coverage = [0] * self.test.count_objects_to_be_covered

        for i in range(self.test.count_objects_to_be_covered):
            columns_count_in_coverage[i] = sum([x * y for x, y in zip(condition, self.test.coverage_array[i])])
            if columns_count_in_coverage[i] == 0:
                uncovered_objects.add(i)

        while len(uncovered_objects) != 0:
            i = list(uncovered_objects)[0]
            j = sorted(self.test.covering_columns[i],
                       key=lambda k: self.calculate_significance(k, uncovered_objects,
                                                                 self.test.rows_to_be_covered[k]))[0]
            condition[j] = 1
            for v in self.test.rows_to_be_covered[j]:
                columns_count_in_coverage[v] += 1
            uncovered_objects = uncovered_objects.difference(self.test.rows_to_be_covered[j])
        for j in sorted([k for k in range(self.test.count_covering_objects) if condition[k] == 1],
                        key=lambda x: -self.test.covering_objects_costs[x]):
            if len([i for i in self.test.rows_to_be_covered[j] if columns_count_in_coverage[i] < 2]) == 0:
                condition[j] = 0
                for i in self.test.rows_to_be_covered[j]:
                    columns_count_in_coverage[i] -= 1
        return condition

    def calculate_significance(self, k, uncovered_objects, j):
        return self.test.covering_objects_costs[k] / len(uncovered_objects.intersection(j))

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

        for _ in range(randint(1, min(self.test.count_covering_objects * 0.05, 2))):
            probability = random()
            for i in range(1, self.test.count_covering_objects + 1):
                if probability < proportion[i]:
                    new_condition[i - 1] = 1 - new_condition[i - 1]
                    break
        return self.fix_condition(new_condition)

    def __value_of_energy(self, condition: list) -> int:
        return sum([a * b for a, b in zip(condition, self.test.covering_objects_costs)])

    def __change_temperature(self, iteration: int) -> float:
        if self.temperature != 0:
            # self.temperature /= math.log10(iteration)
            return log(2) / log(iteration)

    def __probability_of_acceptance(self, delta: int) -> bool:
        if self.temperature != 0:
            return exp(delta / self.temperature) > random()
        else:
            return False

    def __value_of_object(self, j):
        if len(self.test.rows_to_be_covered[j]) == 0:
            return self.test.covering_objects_costs[j] * 2
        return self.test.covering_objects_costs[j] / len(self.test.rows_to_be_covered[j])
