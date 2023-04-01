import pygame as pg
from settings import *


def collide_hit_rect(one, two):
    # Player, wall
    return one.hit_rect.colliderect(two.hit_rect)

class Map:
    def __init__(self, filename):
        self.data = []
        self.sprites = []
        self.effects = []

        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        # Number of tiles across map
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)

        # Number of pixels across map
        self.pixelwidth = self.tilewidth * TILESIZE
        self.pixelheight = self.tileheight * TILESIZE

        # Init map data arrays
        sprite_top_row = [None for x in range(self.tilewidth)]
        for y in range(self.tileheight):
            self.sprites.append(sprite_top_row.copy())
            self.effects.append(sprite_top_row.copy())
        print(f"Sprite array is now {len(self.sprites[0])} wide, {len(self.sprites)} high")

    def add_sprite(self, x, y, sprite):
        self.sprites[y][x] = sprite

    def get_sprite_at(self, x, y):
        return self.sprites[y][x]

    def get_affected_squares(self, effect_name):
        # STUB
        e_squares = []
        for x in range(self.tilewidth):
            for y in range(self.tileheight):
                if self.effects[y][x] is not None and effect_name in self.effects[y][x]:
                    e_squares.append((x,y))
        return e_squares

    def get_tile_circle(self, cx, cy, r, layer):
        tiles = []
        min_y = max(cy - r, 0)
        max_y = min(cy + r, self.tileheight-1)
        min_x = max(cx - r, 0)
        max_x = min(cx + r, self.tilewidth - 1)

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if ((x-cx)**2 + (y-cy)**2) >= r**2:
                    continue
                tiles.append(self.effects[y][x] if layer == 'fx' else self.sprites[y][x])

        return tiles

    def add_effect_circle(self, cx, cy, r, effect_name):
        tiles = []
        min_y = max(cy - r, 0)
        max_y = min(cy + r, self.tileheight-1)
        min_x = max(cx - r, 0)
        max_x = min(cx + r, self.tilewidth - 1)

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                effect_cell = self.effects[y][x]
                if effect_cell is not None and effect_name not in effect_cell:
                    self.effects[y][x].append(effect_name)
                else:
                    self.effects[y][x] = [effect_name]


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

    def unisofy(self, ix, iy):
        # (ix + 2.iy - W / 2) / 2 = x
        # (2.iy + W / 2 - ix) / 2 = y
        if self.iso_mode:
            world_x = (ix + (2 * iy) - (WIDTH/2)) / 2
            world_y = ((2 * iy) + (WIDTH/2) - ix) / 2
            return world_x-self.viewport.left, world_y-self.viewport.top
        else:
            return ix-self.viewport.left, iy-self.viewport.top


    def apply(self, entity):
        return self.apply_rect(entity.rect)

    def apply_rect(self, rect):
        # return entity.rect.move((self.viewport.left, self.viewport.top)) # Old 2d viewport
        return self.isofy(rect.move((self.viewport.left, self.viewport.top)))

    def get_hovered_tile(self, mousetuple):
        (mousex, mousey) = mousetuple
        # Reverse camera transform, divide by TILESIZE
        (worldx, worldy) = self.unisofy(mousex, mousey)
        ht =  (worldx // TILESIZE, worldy // TILESIZE)
        return ht

    def update(self, target):
        x = max(min(-target.rect.centerx + int(WIDTH / 2), 0), WIDTH - self.width)
        y = max(min(-target.rect.centery + int(HEIGHT / 2), 0), HEIGHT - self.height)
        self.viewport = pg.Rect(x, y, self.width, self.height)