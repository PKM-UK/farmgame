import pygame as pg
from settings import *
from os import path


class Dialog():
    game_folder = path.dirname(__file__)
    img_folder = path.join(game_folder, "img")

    def __init__(self, x, y, w, h, screen, game):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.screen = screen
        self.surf = pg.Surface((w, h))
        self.game = game

        self.surf.fill((32,128,0))

        self.elements = []

        self.elements.append(Button(30, 30, 60, 60, self.surf, 'wellicon.png'))

        self.update()

    def update(self):
        for el in self.elements:
            el.draw()

    def draw(self):
        self.screen.blit(self.surf, (self.x, self.y))

class Button():
    def __init__(self, x, y, w, h, surf, icon):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.surf = surf

        # TODO: load button image from name in c'tor
        # self.image =
        self.image = pg.image.load(path.join(Dialog.img_folder, icon)).convert_alpha()

        self.image = pg.transform.scale(self.image, (w, h))
    def draw(self):
        button_rect = pg.Rect(self.x, self.y, self.w, self.h)
        pg.draw.rect(self.surf, GREEN, button_rect)
        # pg.blit(self.image, whatever)
        self.surf.blit(self.image, (self.x,self.y))


