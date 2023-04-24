from sprites import *

class Effect():
    def __init__(self, game, name, p):
        self.game = game
        self.name = name
        self.probability = p
        self.affected_types = []

    def do_thing(self, square, sprite):
        pass

class WateredEffect(Effect):
    def __init__(self, game, name, p):
        super().__init__(game, name, p)
        self.affected_types = [TerrainTypes.dirt, TerrainTypes.shortgrass]

    def do_thing(self, square, sprite):
        if sprite.terrain_type.name == TerrainTypes.dirt:
            self.game.killing(sprite)
            self.game.add_terrain(square[0], square[1], terrain_types[TerrainTypes.shortgrass])
        elif sprite.terrain_type.name == TerrainTypes.shortgrass:
            # long grass grows slower than short grass
            if uniform(0.0, 1.0) < 0.3:
                self.game.killing(sprite)
                self.game.add_terrain(square[0], square[1], terrain_types[TerrainTypes.longgrass])


class PollinateEffect(Effect):
    def __init__(self, game, name, p):
        super().__init__(game, name, p)
        self.affected_types = [TerrainTypes.longgrass]

    def do_thing(self, square, sprite):
        self.game.killing(sprite)
        self.game.add_terrain(square[0], square[1], terrain_types[TerrainTypes.flowers])


class FertileEffect(Effect):
    def __init__(self, game, name, p):
        super().__init__(game, name, p)
        self.affected_types = [TerrainTypes.sapling]

    def do_thing(self, square, sprite):
        self.game.killing(sprite)
        self.game.add_terrain(square[0], square[1], terrain_types[TerrainTypes.tree])
