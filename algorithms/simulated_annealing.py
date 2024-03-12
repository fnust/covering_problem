import math
from math import exp
from random import randint, choice, random
from services.generation import Test
from services.visualization import Video, IMAGE_SIZE


class SimulatedAnnealing:
    def __init__(self, test: Test):
        self.name = 'simulated_annealing'
        self.condition = []
        self.temperature = 0
        self.test = test

    def start(self, initial_temperature: int, visualization: bool = True, count_iteration: int = 10000,
              consistency_of_result: int = 10000) -> None:
        count_result_repetitions = 0
        masks = []
        count = 0
        self.temperature = initial_temperature

        self.__create_condition()
        while count < count_iteration and count_result_repetitions < consistency_of_result:
            print(f'------- {self.name}: {int(count / count_iteration * 100)}% -------')
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
        print(f'------- {self.name}: 100% -------')
        print(f'{self.name}: {self.__value_of_energy(masks[-1])}')

    def __create_condition(self) -> None:
        condition = [randint(0, 1) for _ in range(self.test.count_covering_objects)]
        while (position := self.__check_condition(condition)) >= 0:
            condition[position] = 1
        self.condition = condition

    def __check_condition(self, condition: list) -> int:
        for object_to_be_covered in self.test.coverage_array:
            if 1 not in [a * b for a, b in zip(condition, object_to_be_covered)]:
                return choice([i for i, v in enumerate(object_to_be_covered) if v == 1])
        return -1

    def __change_condition(self) -> list:
        new_condition = self.condition.copy()
        probability = random()

        if probability < 0.4:
            objects = sorted(list(range(self.test.count_covering_objects)),
                             key=lambda x: self.test.covering_objects_costs[x])[self.test.count_covering_objects // 2:]
            position = choice(objects)
            objects.remove(position)
            while len(objects) != 0 and new_condition[position] == 1:
                position = choice(objects)
                objects.remove(position)

            new_condition[position] = 0
        elif probability < 0.8:
            objects = sorted(list(range(self.test.count_covering_objects)),
                             key=lambda x: len([1 for i in self.test.coverage_array if i[x] == 1]))[
                      :self.test.count_covering_objects // 2]
            position = choice(objects)
            objects.remove(position)
            while len(objects) != 0 and new_condition[position] == 1:
                position = choice(objects)
                objects.remove(position)

            new_condition[position] = 0
        else:
            objects = list(range(self.test.count_covering_objects))
            position = choice(objects)
            objects.remove(position)
            while len(objects) != 0 and new_condition[position] == 0:
                position = choice(objects)
                objects.remove(position)

            new_condition[position] = 0

        # position_1 = randint(0, self.test.count_covering_objects - 1)
        # position_2 = randint(0, self.test.count_covering_objects - 1)
        # new_condition[position_1] = 1 - new_condition[position_1]
        # new_condition[position_2] = 1 - new_condition[position_2]
        while (position := self.__check_condition(new_condition)) >= 0:
            new_condition[position] = 1

        return new_condition

    def __sort_by_service(self):

        return

    def __value_of_energy(self, condition: list) -> int:
        return sum([a * b for a, b in zip(condition, self.test.covering_objects_costs)])

    def __change_temperature(self, iteration: int) -> float:
        if self.temperature != 0:
            # self.temperature /= math.log10(iteration)
            return math.log(2) / math.log(iteration)

    def __probability_of_acceptance(self, delta: int) -> bool:
        probability = random()
        print(delta, self.temperature)
        print(exp(delta / self.temperature))
        if self.temperature != 0:
            return probability < exp(delta / self.temperature)
        else:
            return False
