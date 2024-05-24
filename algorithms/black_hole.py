import time
from math import exp, sqrt, ceil
from random import randint, random
from tqdm import tqdm
from services.generation import Test
from services.visualization import Video, IMAGE_SIZE


class Star:
    def __init__(self, objects: list | tuple, fitness_function_value: int):
        self.objects = tuple(objects)
        self.fitness_function_value = fitness_function_value


class BlackHole:
    def __init__(self, test: Test) -> None:
        self.name = 'black_hole'
        self.test = test
        self.count_stars = 0
        self.stars: list[Star] = []

    def start(self, count_iteration: int, count_stars: int, adaptive: bool = True, initial_black_hole: list = None,
              consistency_of_result: int = 100, time_limit: int = 300,
              visualization: bool = False, optimum=None) -> tuple:
        start_time = time.time()
        times = []
        self.count_stars = count_stars
        self.__create_stars()
        count = 0
        masks = []
        results = []
        counts = []
        count_result_repetitions = 0
        black_hole = Star([1] * self.count_stars, sum(self.test.covering_objects_costs))
        if initial_black_hole is not None:
            self.stars[0] = Star(initial_black_hole, self.fitness_function(initial_black_hole))
        pbar = tqdm(total=count_iteration, colour='GREEN')
        while count < count_iteration:
            count += 1
            pbar.update(1)
            min_star = min(self.stars, key=lambda x: x.fitness_function_value)
            count_result_repetitions += 1
            if min_star.fitness_function_value < black_hole.fitness_function_value:
                count_result_repetitions = 0
                black_hole = min_star
            if adaptive and count_result_repetitions > 10:
                self.change_count_stars(black_hole)
            for i in range(self.count_stars):
                r = self.calculate_event_horizon(black_hole.fitness_function_value)
                d = self.calculate_distance(black_hole.objects, self.stars[i].objects)
                if r > d:
                    self.stars[i] = self.__generate_star()
            self.transform(black_hole.objects)
            counts.append(self.count_stars)
            times.append(time.time() - start_time)
            masks.append(list(black_hole.objects))
            results.append(black_hole.fitness_function_value)
            if black_hole.fitness_function_value == optimum:
                break
            if count_result_repetitions > consistency_of_result:
                break
            if times[-1] > time_limit:
                break

        if visualization:
            file_name = f'{self.name}_{count_iteration}_{str(count_stars)}'
            video = Video(IMAGE_SIZE, self.test)
            video.create_video(masks, file_name)
        pbar.close()
        if not adaptive or time_limit != 300:
            return results, times, black_hole.objects
        return results, times, counts, black_hole.objects

    def __create_stars(self) -> None:
        stars = set()
        while len(stars) < self.count_stars:
            star = self.__generate_star()
            stars.add(star)
        self.stars = list(stars)

    def __generate_star(self) -> Star:
        objects = [randint(0, 1) for _ in range(self.test.count_covering_objects)]
        objects = self.fix_star(objects)
        return Star(objects, self.fitness_function(objects))

    def fix_star(self, objects: list) -> list:
        uncovered_objects = set()
        columns_count_in_coverage = [0] * self.test.count_objects_to_be_covered

        for i in range(self.test.count_objects_to_be_covered):
            columns_count_in_coverage[i] = sum([x * y for x, y in zip(objects, self.test.coverage_array[i])])
            if columns_count_in_coverage[i] == 0:
                uncovered_objects.add(i)

        while len(uncovered_objects) != 0:
            i = list(uncovered_objects)[0]
            j = sorted(self.test.covering_columns[i],
                       key=lambda k: self.calculate_significance(k, uncovered_objects,
                                                                 self.test.rows_to_be_covered[k]))[0]
            objects[j] = 1
            for v in self.test.rows_to_be_covered[j]:
                columns_count_in_coverage[v] += 1
            uncovered_objects = uncovered_objects.difference(self.test.rows_to_be_covered[j])
        for j in sorted([k for k in range(self.test.count_covering_objects) if objects[k] == 1],
                        key=lambda x: -self.test.covering_objects_costs[x]):
            if len([i for i in self.test.rows_to_be_covered[j] if columns_count_in_coverage[i] < 2]) == 0:
                objects[j] = 0
                for i in self.test.rows_to_be_covered[j]:
                    columns_count_in_coverage[i] -= 1
        return objects

    def fitness_function(self, objects: list | tuple) -> int:
        return sum([a * b for a, b in zip(objects, self.test.covering_objects_costs)])

    def calculate_event_horizon(self, f_bh: int) -> float:
        return f_bh / sum([star.fitness_function_value for star in self.stars])

    def transform(self, black_hole: tuple) -> None:
        displaced_stars = []
        for star in self.stars:
            displaced_star = [star.objects[i] - random() * (black_hole[i] - star.objects[i]) for i in
                              range(len(star.objects))]
            displaced_star = [1 / (1 + exp(-obj / 3)) for obj in displaced_star]
            displaced_star = [star.objects[i] if random() <= displaced_star[i] else 0 for i in range(len(star.objects))]
            displaced_star = self.fix_star(displaced_star)
            displaced_stars.append(Star(displaced_star.copy(), self.fitness_function(displaced_star)))
        self.stars = displaced_stars.copy()

    def change_count_stars(self, black_hole: Star) -> None:
        max_star = max(self.stars, key=lambda x: x.fitness_function_value)
        probability = abs(black_hole.fitness_function_value - max_star.fitness_function_value) / sum(
            [star.fitness_function_value for star in self.stars])
        if random() > probability:
            b = ceil(probability * self.count_stars)
            if random() > probability:
                for _ in range(b):
                    self.stars.append(black_hole)
            else:
                for _ in range(b):
                    self.stars.append(self.__generate_star())
            self.count_stars += b
        else:
            w = round(probability * self.count_stars)
            if self.count_stars >= w:
                for _ in range(w):
                    self.stars.remove(max_star)
                    max_star = max(self.stars, key=lambda x: x.fitness_function_value)
                self.count_stars -= w

    def calculate_significance(self, k: int, uncovered_objects: set, j: set) -> float:
        return self.test.covering_objects_costs[k] / len(uncovered_objects.intersection(j))

    def calculate_distance(self, black_hole: tuple, star: tuple) -> float:
        return sqrt(sum([(black_hole[j] - star[j]) ** 2 for j in range(self.test.count_covering_objects)]))
