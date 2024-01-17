from PIL import Image, ImageDraw
from generation import Test

IMAGE_SIZE = 2000
FILE = 'data/tests/test_30_40_20.txt'


class VisualizeMap(Test):
    def __init__(self, image_size, file):
        super().__init__()
        self.image_size = image_size
        self.load(file)

        self.sprite_size = image_size // self.map_size
        self.sprite_objects_to_be_covered = Image.open('assets/objects_to_be_covered.png').convert("RGBA").resize(
            (self.sprite_size, self.sprite_size))
        self.sprite_covering_object = Image.open('assets/covering_object.png').convert("RGBA").resize(
            (self.sprite_size, self.sprite_size))

    def save_image(self, mask):
        map_image = Image.new("RGBA", (self.image_size, self.image_size), (93, 161, 48, 255))

        self.visualize_ranges(map_image, [i for i, v in enumerate(mask) if v == 1])
        self.visualize_covering_objects(map_image)
        self.visualize_objects_to_be_covered(map_image)

        # map_image.show()

        return map_image

    def visualize_ranges(self, map_image, indexes):
        circle = Image.new('RGBA',
                           size=(2 * self.radius * self.sprite_size + 1, 2 * self.radius * self.sprite_size + 1),
                           color=(0, 0, 0, 0))
        draw_circle = ImageDraw.Draw(circle)

        for i in indexes:
            x = self.covering_objects[i][0]
            y = self.covering_objects[i][1]
            draw_circle.ellipse((0, 0, 2 * self.radius * self.sprite_size, 2 * self.radius * self.sprite_size),
                                fill=(93, 161, 48, 50),
                                outline=(0, 0, 0), width=5)
            map_image.paste(circle, ((x - self.radius) * self.sprite_size, (y - self.radius) * self.sprite_size),
                            circle)

    def visualize_covering_objects(self, map_image):
        for i in range(self.count_covering_objects):
            x = self.covering_objects[i][0]
            y = self.covering_objects[i][1]
            map_image.paste(self.sprite_covering_object, (x * self.sprite_size, y * self.sprite_size),
                            self.sprite_covering_object)

    def visualize_objects_to_be_covered(self, map_image):
        for i in range(self.count_objects_to_be_covered):
            x = self.objects_to_be_covered[i][0]
            y = self.objects_to_be_covered[i][1]
            map_image.paste(self.sprite_objects_to_be_covered, (x * self.sprite_size, y * self.sprite_size),
                            self.sprite_objects_to_be_covered)


class Video(VisualizeMap):
    def __init__(self, image_size, file):
        super().__init__(image_size, file)

    def create_video(self, masks, name):
        frames = []
        for mask in masks:
            frames.append(self.save_image(mask))
        frames[0].save(f'data/videos/{name}.gif', save_all=True, append_images=frames[1:], optimize=True,
                       duration=[150] * (len(frames) - 1) + [10000], loop=0)
        frames[-1].save(f'data/maps/{name}.png')


# visualize_map = VisualizeMap(IMAGE_SIZE, FILE)
# visualize_map.save_image([0] * 50)
