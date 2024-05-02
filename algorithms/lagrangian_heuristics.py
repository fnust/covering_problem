from tqdm import tqdm
import math

from services.generation import Test
from services.visualization import Video, IMAGE_SIZE

INF = 100000000000


# class Test:
#     def __init__(self, covering_objects_costs, coverage_array, count_covering_objects, count_objects_to_be_covered):
#         self.covering_objects_costs = covering_objects_costs
#         self.coverage_array = coverage_array
#         self.count_covering_objects = count_covering_objects
#         self.count_objects_to_be_covered = count_objects_to_be_covered


class LagrangianHeuristics:
    def __init__(self, test: Test):
        self.name = 'lagrangian_heuristics'
        self.test = test
        self.z_max = -INF
        self.z_ub = INF
        self.costs = test.covering_objects_costs.copy()
        self.p = test.covering_objects_costs.copy()
        self.t = [min([a * b for a, b in zip(test.covering_objects_costs, coverage_of_obj) if b != 0]) for
                  coverage_of_obj in test.coverage_array]
        self.x = [0] * test.count_covering_objects

    def start(self, count_iteration, visualization=False):
        f = 2
        old_z_max = self.z_max
        consistency_of_result = 0
        masks = []
        for _ in tqdm(range(count_iteration), colour='GREEN'):
            z_lb, coefficients = self.calculate_z_lb()
            self.z_max = max(self.z_max, z_lb)
            if old_z_max == self.z_max:
                consistency_of_result += 1
            else:
                consistency_of_result = 0
            set_covering_objects = self.find_solution()
            masks.append([(0, 1)[i in set_covering_objects] for i in range(self.test.count_covering_objects)])
            self.z_ub = min(self.z_ub, self.calculate_costs(set_covering_objects))
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

        if visualization:
            file_name = f'{self.name}_{count_iteration}'
            video = Video(IMAGE_SIZE, self.test)
            video.create_video(masks, file_name)

        # print(self.z_max)
        return self.z_ub

    def calculate_z_lb(self):
        coefficients = [self.costs[j] - sum(
            [self.test.coverage_array[i][j] * self.t[i] for i in range(self.test.count_objects_to_be_covered)]) for j in
                        range(self.test.count_covering_objects)]
        self.x = [(0, 1)[c <= 0] for c in coefficients]
        return sum([a * b for a, b in zip(coefficients, self.x)]) + sum(self.t), coefficients

    def find_solution(self):
        s = [i for i in range(self.test.count_covering_objects) if self.x[i] == 1]
        # print(s)
        for object_to_be_covered in self.test.coverage_array:
            if 1 not in [object_to_be_covered[j] for j in s]:
                candidate = min([(self.costs[j], j) for j in object_to_be_covered if j == 1])
                s.append(candidate[1])
        s.sort(reverse=True)
        new_s = s.copy()
        for i in s:
            for object_to_be_covered in self.test.coverage_array:
                if 1 not in [object_to_be_covered[j] for j in new_s if i != j]:
                    break
            else:
                new_s.remove(i)
        return new_s

    def calculate_costs(self, s) -> int:
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
