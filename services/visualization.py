from PIL import Image, ImageDraw

from services.common import DirectoryCreator
from services.generation import Test

IMAGE_SIZE = 2000


class VisualizeMap:
    def __init__(self, image_size: int, test: Test):
        self.image_size = image_size
        self.test = test

        self.sprite_size = image_size // self.test.map_size
        self.sprite_objects_to_be_covered = Image.open('services/assets/objects_to_be_covered.png').convert(
            "RGBA").resize(
            (self.sprite_size, self.sprite_size))
        self.sprite_covering_object = Image.open('services/assets/covering_object.png').convert("RGBA").resize(
            (self.sprite_size, self.sprite_size))

    def save_image(self, mask: list[int]) -> Image:
        map_image = Image.new("RGBA", (self.image_size, self.image_size), (93, 161, 48, 255))

        self.__visualize_ranges(map_image, [i for i, v in enumerate(mask) if v == 1])
        self.__visualize_covering_objects(map_image)
        self.__visualize_objects_to_be_covered(map_image)

        # map_image.show()

        return map_image

    def __visualize_ranges(self, map_image: Image, indexes: list[int]) -> None:
        circle = Image.new('RGBA',
                           size=(
                               2 * self.test.radius * self.sprite_size + 1,
                               2 * self.test.radius * self.sprite_size + 1),
                           color=(0, 0, 0, 0))
        draw_circle = ImageDraw.Draw(circle)

        for i in indexes:
            x = self.test.covering_objects[i][0]
            y = self.test.covering_objects[i][1]
            draw_circle.ellipse(
                (0, 0, 2 * self.test.radius * self.sprite_size, 2 * self.test.radius * self.sprite_size),
                fill=(93, 161, 48, 50),
                outline=(0, 0, 0), width=5)
            map_image.paste(circle,
                            ((x - self.test.radius) * self.sprite_size, (y - self.test.radius) * self.sprite_size),
                            circle)

    def __visualize_covering_objects(self, map_image: Image) -> None:
        for i in range(self.test.count_covering_objects):
            x = self.test.covering_objects[i][0]
            y = self.test.covering_objects[i][1]
            map_image.paste(self.sprite_covering_object, (x * self.sprite_size, y * self.sprite_size),
                            self.sprite_covering_object)

    def __visualize_objects_to_be_covered(self, map_image: Image) -> None:
        for i in range(self.test.count_objects_to_be_covered):
            x = self.test.objects_to_be_covered[i][0]
            y = self.test.objects_to_be_covered[i][1]
            map_image.paste(self.sprite_objects_to_be_covered, (x * self.sprite_size, y * self.sprite_size),
                            self.sprite_objects_to_be_covered)


class Video(VisualizeMap):
    def __init__(self, image_size: int, test: Test):
        super().__init__(image_size, test)

    def create_video(self, masks: list[list[int]], file_name: str) -> None:
        frames = []
        test_name = f'test_{self.test.count_objects_to_be_covered}_{self.test.count_covering_objects}_{self.test.radius}'
        masks = masks[:masks.index(
            min(masks, key=lambda x: sum([a * b for a, b in zip(x, self.test.covering_objects_costs)]))) + 1]
        for mask in masks:
            frames.append(self.save_image(mask))
        path = DirectoryCreator().new_directory('videos', test_name)
        frames[0].save(f'{path}/{file_name}.gif', save_all=True, append_images=frames[1:], optimize=True,
                       duration=[150] * (len(frames) - 1) + [10000], loop=0)
        path = DirectoryCreator().new_directory('maps', test_name)
        frames[-1].save(f'{path}/{file_name}.png')

# visualize_map = VisualizeMap(IMAGE_SIZE, FILE)
# visualize_map.save_image([0] * 50)
