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

