import pygame as pg
from settings import *


def collide_hit_rect(one, two):
    # Player, wall
    return one.hit_rect.colliderect(two.hit_rect)

class Map:
    def __init__(self, filename):
        self.data = []
        self.sprites = [[]]
        self.effects = [[]]

        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        # Number of tiles across map
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)

        # Number of pixels across map
        self.pixelwidth = self.tilewidth * TILESIZE
        self.pixelheight = self.tileheight * TILESIZE

    def add_sprite(self, x, y, sprite):
        self.sprites[x][y] = sprite

class Camera:
    def __init__(self, width, height, iso):
        self.viewport = pg.Rect(0, 0, width, height)
        self.height = height
        self.width = width
        self.iso_mode = iso

    def set_iso(self, newmode):
        self.iso_mode = newmode

    def isofy(self, rect):
        if self.iso_mode:
            iso_x = (rect.left - rect.top) + (WIDTH/2) - (rect.width/2)
            iso_y = (rect.left + rect.top) / 2
            # Expect tiles TILESIZE high, shift up if taller
            iso_y = iso_y + TILESIZE - rect.height
            iso_width = rect.width
            iso_height = rect.height

            return pg.Rect(iso_x, iso_y,iso_width, iso_height)
        else:
            return rect

    def apply(self, entity):
        return self.apply_rect(entity.rect)

    def apply_rect(self, rect):
        # return entity.rect.move((self.viewport.left, self.viewport.top)) # Old 2d viewport
        return self.isofy(rect.move((self.viewport.left, self.viewport.top)))

    def applyrect(self, rect):
        return rect.move(self.viewport.topleft)

    def update(self, target):
        x = max(min(-target.rect.centerx + int(WIDTH / 2), 0), WIDTH - self.width)
        y = max(min(-target.rect.centery + int(HEIGHT / 2), 0), HEIGHT - self.height)
        self.viewport = pg.Rect(x, y, self.width, self.height)