import time

from tqdm import tqdm
import math
from services.generation import Test
from services.visualization import Video, IMAGE_SIZE

INF = 100000000000


class LagrangianHeuristics:
    def __init__(self, test: Test) -> None:
        self.name = 'lagrangian_heuristics'
        self.test = test
        self.z_max = -INF
        self.z_ub = INF
        self.costs = test.covering_objects_costs.copy()
        self.p = test.covering_objects_costs.copy()
        self.t = [min([a * b for a, b in zip(test.covering_objects_costs, coverage_of_obj) if b != 0]) for
                  coverage_of_obj in test.coverage_array]
        self.x = [0] * test.count_covering_objects

    def start(self, count_iteration: int, time_limit: int = 300, visualization: bool = False,
              consistency_of_result: int = 1000, optimum=None) -> tuple:
        f = 2
        old_z_ub = -self.z_max
        count_result_repetitions = 0
        masks = []
        start_time = time.time()
        times = []
        results = []
        set_covering_objects = set()
        best_solution = []
        for _ in tqdm(range(count_iteration), colour='GREEN'):
            z_lb, coefficients = self.calculate_z_lb()
            self.z_max = max(self.z_max, z_lb)
            if old_z_ub == self.z_ub:
                count_result_repetitions += 1
            else:
                count_result_repetitions = 0
            set_covering_objects = self.find_solution()
            self.z_ub = min(self.z_ub, self.calculate_costs(set_covering_objects))
            masks.append([(0, 1)[i in set_covering_objects] for i in range(self.test.count_covering_objects)])
            times.append(time.time() - start_time)
            results.append(self.z_ub)
            if math.ceil(self.z_max) == self.z_ub:
                break
            self.p = self.calculate_p(z_lb, coefficients)
            if consistency_of_result == 30:
                f /= 2
            subgradient = self.calculate_subgradient()
            if sum([g ** 2 for g in subgradient]) == 0:
                break
            step_size = self.calculate_step_size(f, z_lb, subgradient)
            self.t = self.update_lagrange_multipliers(step_size, subgradient)
            if self.z_ub < old_z_ub:
                old_z_ub = self.z_ub
                best_solution = [(0, 1)[i in set_covering_objects] for i in range(self.test.count_covering_objects)]
            if self.z_ub == optimum:
                break
            if count_result_repetitions > consistency_of_result:
                break
            if times[-1] > time_limit:
                break

        if visualization:
            file_name = f'{self.name}_{count_iteration}'
            video = Video(IMAGE_SIZE, self.test)
            video.create_video(masks, file_name)
        return results, times, best_solution

    def calculate_z_lb(self) -> tuple:
        coefficients = [self.costs[j] - sum(
            [self.test.coverage_array[i][j] * self.t[i] for i in range(self.test.count_objects_to_be_covered)]) for j in
                        range(self.test.count_covering_objects)]
        self.x = [(0, 1)[c <= 0] for c in coefficients]
        return sum([a * b for a, b in zip(coefficients, self.x)]) + sum(self.t), coefficients

    def find_solution(self) -> list:
        s = [i for i in range(self.test.count_covering_objects) if self.x[i] == 1]
        uncovered_objects = set()
        columns_count_in_coverage = [0] * self.test.count_objects_to_be_covered

        for i in range(self.test.count_objects_to_be_covered):
            columns_count_in_coverage[i] = sum([x * y for x, y in zip(self.x, self.test.coverage_array[i])])
            if columns_count_in_coverage[i] == 0:
                uncovered_objects.add(i)

        while len(uncovered_objects) != 0:
            i = list(uncovered_objects)[0]
            j = min(self.test.covering_columns[i], key=lambda x: self.costs[x])
            s.append(j)
            for v in self.test.rows_to_be_covered[j]:
                columns_count_in_coverage[v] += 1
            uncovered_objects = uncovered_objects.difference(self.test.rows_to_be_covered[j])

        for j in sorted(s, key=lambda x: -self.costs[x]):
            if len([i for i in self.test.rows_to_be_covered[j] if columns_count_in_coverage[i] < 2]) == 0:
                s.remove(j)
                for i in self.test.rows_to_be_covered[j]:
                    columns_count_in_coverage[i] -= 1
        return sorted(s)

    def calculate_costs(self, s: list) -> int:
        return sum([self.costs[i] for i in s])

    def calculate_p(self, z_lb, coefficients):
        p = [max(([self.p[k], z_lb], [self.p[k], z_lb + coefficients[k]])[self.x[k] == 0]) for k in
             range(self.test.count_covering_objects)]
        self.costs = [(self.costs[k], INF)[p[k] > self.z_ub] for k in range(self.test.count_covering_objects)]
        return p

    def calculate_subgradient(self):
        g = [1 - sum([a * b for a, b in zip(self.x, self.test.coverage_array[i])]) for i in
             range(self.test.count_objects_to_be_covered)]
        g = [(g[i], 0)[self.t[i] == 0 and g[i] < 0] for i in range(self.test.count_objects_to_be_covered)]
        return g

    def calculate_step_size(self, f, z_lb, subgradient):
        return f * (1.05 * self.z_ub - z_lb) / sum([g ** 2 for g in subgradient])

    def update_lagrange_multipliers(self, step_size, subgradient):
        return [max(0, self.t[i] + step_size * subgradient[i]) for i in range(self.test.count_objects_to_be_covered)]
