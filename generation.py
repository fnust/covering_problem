from random import randint

SIGN_EMPTY = 0
SIGN_OBJECT_TO_COVERED = 1
SIGN_COVERING_OBJECTS = 2

COUNT_OBJECTS_TO_BE_COVERED = 25
COUNT_COVERING_OBJECTS = 50
MAP_SIZE = 100
RADIUS = 20


class Test:
    def __init__(self):
        self.map_size = 0
        self.radius = 0
        self.count_objects_to_be_covered = 0
        self.count_covering_objects = 0
        self.objects_to_be_covered = []
        self.covering_objects = []
        self.coverage_array = [[]]
        self.covering_objects_costs = []

    def load(self, file):
        with open(file, 'r') as f:
            lines = f.readlines()
            self.count_objects_to_be_covered, self.count_covering_objects, self.radius, self.map_size = map(int, lines[
                0].split())
            self.coverage_array = [list(map(int, x.split())) for x in lines[1:self.count_objects_to_be_covered + 1:]]
            self.covering_objects_costs = list(map(int, lines[self.count_objects_to_be_covered + 1].split()))
            begin = self.count_objects_to_be_covered + 2
            end = begin + self.count_objects_to_be_covered
            self.objects_to_be_covered = [tuple(map(int, x.split())) for x in lines[begin:end:]]
            begin = end
            end = begin + self.count_covering_objects
            self.covering_objects = [tuple(map(int, x.split())) for x in lines[begin:end:]]

    def save_data(self):
        with (open(
                f'data/tests/test_{self.count_objects_to_be_covered}_{self.count_covering_objects}_{self.radius}.txt',
                'w')
              as f):
            f.write(' '.join([str(self.count_objects_to_be_covered), str(self.count_covering_objects),
                              str(self.radius), str(self.map_size)]) + '\n')
            for line in self.coverage_array:
                f.write(' '.join(map(str, line)) + '\n')
            f.write(' '.join(map(str, self.covering_objects_costs)) + '\n')
            for line in self.objects_to_be_covered:
                f.write(' '.join(map(str, line)) + '\n')
            for line in self.covering_objects:
                f.write(' '.join(map(str, line)) + '\n')


class GenerateMap(Test):
    def __init__(self, map_size, count_objects_to_be_covered, count_covering_objects, radius):
        super().__init__()
        self.map_size = map_size
        self.map = [[0] * map_size for _ in range(map_size)]

        self.generate_objects_to_be_covered(count_objects_to_be_covered)
        self.generate_covering_objects(count_covering_objects)
        self.generate_covering_objects_costs()
        self.radius = self.generate_coverage_array(radius)

    def generate_objects_to_be_covered(self, count_objects_to_be_covered):
        count = 0
        self.count_objects_to_be_covered = count_objects_to_be_covered
        while count < count_objects_to_be_covered:
            x = randint(0, self.map_size - 1)
            y = randint(0, self.map_size - 1)

            if self.map[y][x] == SIGN_EMPTY:
                self.map[y][x] = SIGN_OBJECT_TO_COVERED
                self.objects_to_be_covered.append((x, y))
                count += 1

    def generate_covering_objects(self, count_covering_objects):
        count = 0
        self.count_covering_objects = count_covering_objects
        while count < count_covering_objects:
            x = randint(0, self.map_size - 1)
            y = randint(0, self.map_size - 1)

            if self.map[y][x] == SIGN_EMPTY:
                self.map[y][x] = SIGN_COVERING_OBJECTS
                self.covering_objects.append((x, y))
                count += 1

    def generate_covering_objects_costs(self):
        self.covering_objects_costs = [randint(5, 100) for _ in range(self.count_covering_objects)]

    def generate_coverage_array(self, radius):
        is_valid = False

        while not is_valid:
            is_valid = True
            self.coverage_array = [[0] * self.count_covering_objects for _ in range(self.count_objects_to_be_covered)]
            for i in range(self.count_objects_to_be_covered):
                for j in range(self.count_covering_objects):
                    distance = ((self.covering_objects[j][0] - self.objects_to_be_covered[i][0]) ** 2 +
                                (self.covering_objects[j][1] - self.objects_to_be_covered[i][1]) ** 2) ** 0.5
                    if distance <= radius:
                        self.coverage_array[i][j] = 1

                if 1 not in self.coverage_array[i]:
                    is_valid = False
                    radius += 1
                    break
        return radius

#
# objects_map = GenerateMap(MAP_SIZE, COUNT_OBJECTS_TO_BE_COVERED, COUNT_COVERING_OBJECTS, RADIUS)
# objects_map.save_data()
