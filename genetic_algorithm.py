from random import randint, choice
from visualization import Video, IMAGE_SIZE

FILE = 'data/tests/test_25_50_20.txt'
COUNT_CHROMOSOMES = 50


class GeneticAlgorithm(Video):
    def __init__(self, image_size, file, count_chromosomes):
        super().__init__(image_size, file)
        self.name = 'genetic_algorithm'
        self.count_chromosomes = count_chromosomes
        self.chromosomes = []
        self.best_result = 0
        self.best_chromosome = []

    def start(self, count_iteration):
        self.create_chromosomes()
        masks = []
        max_cost = sum(self.covering_objects_costs)
        count = 0

        while count < count_iteration:
            self.mutate_chromosomes(max_cost)
            masks.append(self.chromosomes[0])
            result = max_cost - sum([a * b for a, b in zip(self.chromosomes[0], self.covering_objects_costs)]) + 1
            if result > self.best_result:
                self.best_result = result
                self.best_chromosome = self.chromosomes[0].copy()
            count += 1
        masks.append(self.best_chromosome)
        file_name = f'{self.name}_{self.count_objects_to_be_covered}_{self.count_covering_objects}_{self.radius}'
        self.create_video(masks, file_name)
        print(self.best_result)

    def create_chromosomes(self):
        for _ in range(self.count_chromosomes):
            chromosome = [randint(0, 1) for _ in range(self.count_covering_objects)]
            while (position := self.check_chromosome(chromosome)) >= 0:
                chromosome[position] = 1
            self.chromosomes.append(chromosome)

    def check_chromosome(self, chromosome):
        for object_to_be_covered in self.coverage_array:
            if 1 not in [a * b for a, b in zip(chromosome, object_to_be_covered)]:
                return choice([i for i, v in enumerate(object_to_be_covered) if v == 1])
        return -1

    def mutate_chromosomes(self, max_cost):
        new_chromosomes = []
        for i in range(0, self.count_chromosomes, 2):
            separation = randint(2, self.count_covering_objects - 3)
            chromosome = self.chromosomes[i][:separation] + self.chromosomes[i + 1][separation:]

            while (position := self.check_chromosome(chromosome)) >= 0:
                chromosome[position] = 1

            new_chromosomes.append(chromosome)
            chromosome = self.chromosomes[i + 1][:separation] + self.chromosomes[i][separation:]

            while (position := self.check_chromosome(chromosome)) >= 0:
                chromosome[position] = 1
            new_chromosomes.append(chromosome)

        self.chromosomes = new_chromosomes.copy()
        self.chromosomes.sort(key=lambda x: max_cost - sum([a * b for a, b in zip(x, self.covering_objects_costs)]) + 1,
                              reverse=True)


test = GeneticAlgorithm(IMAGE_SIZE, FILE, COUNT_CHROMOSOMES)
test.start(100)
