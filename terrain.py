from enum import Enum

class TerrainTypes(Enum):
    dirt = 1
    shortgrass = 2
    longgrass = 3
    tree = 4
    wall = 5
    well = 6

class Terrain:
    def __init__(self, name, obstacle, imgpath, isotiles):
        self.name = name
        self.obstacle = obstacle
        self.tile = imgpath
        self.isotiles = isotiles
        self.img = None
        self.iso_images = []

        # sample effect: {type: 'grass_grow', radius: '5', p: 0.05}
        self.effects = []

