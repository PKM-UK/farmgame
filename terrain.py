from enum import Enum

class TerrainTypes(Enum):
    dirt = 1
    shortgrass = 2
    longgrass = 3
    tree = 4
    wall = 5
    well = 6
    flowers = 7
    hive = 8
    sapling = 9

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

terrain_types = {
    TerrainTypes.dirt: Terrain(TerrainTypes.dirt, False, 'dirtTile.png', ['isodirtTile.png']),
    TerrainTypes.shortgrass: Terrain(TerrainTypes.shortgrass, False, 'grassTile.png', ['isoshortgrassTile.png']),
    TerrainTypes.longgrass: Terrain(TerrainTypes.longgrass, False, 'grassTile.png', ['isolonggrassTile.png']),
    TerrainTypes.flowers: Terrain(TerrainTypes.flowers, False, 'grassTile.png', ['isoflowersTile.png']),
    TerrainTypes.sapling: Terrain(TerrainTypes.sapling, True, 'saplingTile.png', ['isosaplingTile.png']),
    TerrainTypes.tree: Terrain(TerrainTypes.tree, True, 'treeTile.png', ['isotreeTile1.png', 'isotreeTile2.png', 'isotreeTile1.png']),
    TerrainTypes.wall: Terrain(TerrainTypes.wall, True, 'wallTile.png', ['isowallTile.png']),
    TerrainTypes.well: Terrain(TerrainTypes.well, True, 'wellTile.png', ['isowellTile.png']),
    TerrainTypes.hive: Terrain(TerrainTypes.hive, True, 'hiveTile.png', ['isohiveTile.png'])
}