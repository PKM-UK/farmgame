from os import path
import pygame as pg
from settings import *

LGOAT_IMG = 'lgoat.png'
RGOAT_IMG = 'rgoat.png'

# muhammad_ali = new Boxer()
# muhammad_ali.addComponent(new ButterflyFloatComponent())
# muhammad_ali.addComponent(new BeeStingComponent())

class ImageComponent:
    game_folder = path.dirname(__file__)
    img_folder = path.join(game_folder, "img")

    def __init__(self, game, mob):
        self.game = game
        self.mob = mob

    def get_image(self, heading):
        pass

class GoatImageComponent(ImageComponent):
    # Class variables, lazily loaded in ctor to avoid duplication
    left_goat_img = None
    right_goat_img = None

    def __init__(self, game, mob):
        super().__init__(game, mob)
        if GoatImageComponent.left_goat_img is None:
            GoatImageComponent.left_goat_img = pg.image.load(path.join(ImageComponent.img_folder, LGOAT_IMG)).convert_alpha()
            GoatImageComponent.right_goat_img = pg.image.load(path.join(ImageComponent.img_folder, RGOAT_IMG)).convert_alpha()
            GoatImageComponent.left_goat_img = pg.transform.scale(GoatImageComponent.left_goat_img, (TILESIZE, TILESIZE))
            GoatImageComponent.right_goat_img = pg.transform.scale(GoatImageComponent.right_goat_img, (TILESIZE, TILESIZE))

    def get_image(self, heading):
        if -45 < heading < 135:
            return GoatImageComponent.right_goat_img
        else:
            return GoatImageComponent.left_goat_img




