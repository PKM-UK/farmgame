from settings import *
from sprites import TerrainTypes
import pygame as py
from random import uniform

vec = pg.math.Vector2

class ControlComponent:
    def __init__(self, game, mob):
        self.tick = pg.time.get_ticks()
        self.game = game
        self.mob = mob

    def get_control(self):
        pass


class HunterControlComponent(ControlComponent):
    def __init__(self, game, mob):
        super().__init__(game, mob)

    def get_control(self):
        # CONTROL
        aim_vec = self.game.player.pos - self.mob.pos
        rot = aim_vec.angle_to(vec(1, 0))

        # PHYSICS
        vel = self.mob.vel
        acc = vec(MOB_SPEED, 0).rotate(-rot)
        vel *= 0.98
        vel += acc * self.game.dt

        # Return what the mob wants: rot and vel vector (not the same if dorifto)
        return rot, vel


class DrifterControlComponent(ControlComponent):
    def __init__(self, game, mob):
        super().__init__(game, mob)
        self.speed = 40
        self.rot = 0
        self.vel = vec(0, 0)

    def get_control(self):
        if pg.time.get_ticks() - self.tick > 3000:
            self.tick = pg.time.get_ticks()
            self.rot = int(uniform(-179.0, 179.0))
            self.vel = vec(self.speed, 0).rotate(self.rot)

        return self.rot, self.vel

class GrazerControlComponent(ControlComponent):
    def __init__(self, game, mob):
        super().__init__(game, mob)
        self.speed = 40
        self.rot = 0
        self.vel = vec(0, 0)

        self.target_square = None
        self.target_type = TerrainTypes.longgrass
        self.hunt_radius = GOAT_VISION_DISTACE
        self.reached_food_tick = -1  # When did we get to the food?

    def get_control(self):
        now = pg.time.get_ticks()

        if self.reached_food_tick > 0 and now - self.reached_food_tick > GOAT_EAT_TIME:
            self.game.eat_grass(self.target_square.x, self.target_square.y)
            self.target_square = None
            self.reached_food_tick = -1

        if self.target_square is None:
            if now - self.tick > GOAT_ATTENTION_SPAN:
                self.tick = now
                # Find a food square
                # Look in local 9x9 square
                cx = int(self.mob.x // TILESIZE)
                cy = int(self.mob.y // TILESIZE)

                # Ask the map for a list of sprites within our hunt radius
                tiles = self.game.map.get_tile_circle(cx, cy, self.hunt_radius, 'terrain')

                # Filter to only longgrass tiles and sort by Manhattan distance
                target_tiles = list(filter(lambda tile: tile.terrain_type.name == TerrainTypes.longgrass, tiles))
                target_tiles.sort(key=lambda tile: (tile.x-self.mob.x) + (tile.y-self.mob.y))

                if len(target_tiles) > 0:
                    self.target_square = target_tiles[0]
                else:
                    # Random amble
                    self.target_square = None
                    self.rot = int(uniform(-179.0, 179.0))
                    self.vel = vec(self.speed * 0.5, 0).rotate(self.rot)

        if self.target_square is not None:
            # Now we have a target square, calculate vector to it
            target_pos = vec(self.target_square.x, self.target_square.y) * TILESIZE
            target_vec = (target_pos - self.mob.pos)

            if target_vec.magnitude() < (TILESIZE//2):
                # Within one square of target, stop and munch
                self.vel = vec(0, 0)
                if self.reached_food_tick < 0:
                    self.reached_food_tick = now
            else:
                self.vel = target_vec.normalize() * self.speed
                self.rot = self.vel.angle_to(vec(1, 0))

        return self.rot, self.vel


