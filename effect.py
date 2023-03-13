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
        self.affected_types = ['dirt']

    def do_thing(self, square, sprite):
        sprite.kill
        new_sprite = Wall(self.game, square[0], square[1], terrain_types['grass'])