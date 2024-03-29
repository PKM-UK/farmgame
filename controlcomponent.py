from settings import *
from sprites import TerrainTypes
from item import ItemTypes
import pygame as py
from random import uniform
from map import tile_from_vec

vec = pg.math.Vector2

class ControlComponent:
    def __init__(self, game, mob):
        self.tick = pg.time.get_ticks()
        self.game = game
        self.mob = mob

    def get_control(self):
        pass

class ClockCC(ControlComponent):
    def __init__(self, game, mob):
        super().__init__(game, mob)
        self.rot = 0
        self.vel = vec(0, 0)

    def get_control(self):
        now = pg.time.get_ticks()
        if now > self.tick + 600:
            self.tick = now
            self.rot = self.rot + 10
            if self.rot > 180:
                self.rot = self.rot - 360
            self.vel = vec(40, 0).rotate(self.rot)
            print(f"Moving at {self.rot}")
        # return self.rot, self.vel

class HunterControlComponent(ControlComponent):
    def __init__(self, game, mob):
        super().__init__(game, mob)

    def get_control(self):
        # CONTROL
        aim_vec = self.game.player.pos - self.mob.pos
        rot = vec(1, 0).angle_to(aim_vec)

        # PHYSICS
        vel = self.mob.vel
        acc = vec(MOB_SPEED, 0).rotate(rot)
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
        self.saw_food_tick = -1
        self.reached_food_tick = -1  # When did we get to the food?
        self.poop_tick = pg.time.get_ticks()


    def get_control(self):
        now = pg.time.get_ticks()
        cx = int(self.mob.pos.x // TILESIZE)
        cy = int(self.mob.pos.y // TILESIZE)

        if self.reached_food_tick > 0 and now - self.reached_food_tick > GOAT_EAT_TIME:
            self.game.eat_grass(self.target_square.tile_x, self.target_square.tile_y)
            self.target_square = None
            self.reached_food_tick = -1

        if now - self.poop_tick > GOAT_POOP_FREQ:
            self.game.add_item(cx, cy, ItemTypes.poop)
            self.poop_tick = now

        if self.target_square is None:
            if now - self.tick > GOAT_ATTENTION_SPAN:
                self.tick = now
                # Find a food square
                # Ask the map for a list of sprites within our hunt radius
                tiles = self.game.map.get_tile_circle(cx, cy, self.hunt_radius, 'terrain')

                # Filter to only longgrass tiles and sort by Manhattan distance
                target_tiles = list(filter(lambda tile: tile.terrain_type == TerrainTypes.longgrass, tiles))
                target_tiles.sort(key=lambda tile: (tile.pos - self.mob.pos).magnitude())

                if len(target_tiles) > 0:
                    self.target_square = target_tiles[0]
                    self.saw_food_tick = now
                else:
                    # Random amble
                    self.target_square = None
                    self.rot = int(uniform(-179.0, 179.0))
                    self.vel = vec(self.speed * 0.5, 0).rotate(self.rot)

        if self.target_square is not None:
            # Now we have a target square, calculate vector to it
            target_vec = (self.target_square.pos - self.mob.pos)

            if target_vec.magnitude() < (TILESIZE//2):
                # Within one square of target, stop and munch
                self.vel = vec(0, 0)
                if self.reached_food_tick < 0:
                    self.reached_food_tick = now
                    self.saw_food_tick = -1
            else:
                self.vel = target_vec.normalize() * self.speed
                self.rot = vec(1, 0).angle_to(self.vel)

            if self.saw_food_tick > 0 and now - self.saw_food_tick > GOAT_TENACITY:
                # We've been hunting this food tile for ages, forget it
                self.target_square = None
                self.rot = int(uniform(-179.0, 179.0))
                self.vel = vec(self.speed * 0.5, 0).rotate(self.rot)
                self.tick = now  # Amble for another attention span

        return self.rot, self.vel


class BumbleControlComponent(ControlComponent):
    def __init__(self, game, mob):
        super().__init__(game, mob)
        self.speed = 40
        self.rot = uniform(-179, 179)
        self.vel = vec(1, 0)
        self.flying = True

        self.home_square = self.game.map.get_sprite_at(*tile_from_vec(self.mob.pos))
        self.target_square = None
        self.target_type = TerrainTypes.flowers
        self.hunt_radius = GOAT_VISION_DISTACE * 2
        self.reached_food_tick = -1  # When did we get to the food?
        self.bumble_start = 0
        self.bumble_time = uniform(1000, 3000)
        self.bumble_dir = 1

    def get_control(self):
        now = pg.time.get_ticks()
        if now - self.bumble_start > self.bumble_time:
            self.bumble_start = now
            self.bumble_dir = self.bumble_dir * -1

            # When we reach target, set a new one
            if self.target_square is None or (self.target_square.pos - self.mob.pos).magnitude() < (TILESIZE):
                cx = int(self.mob.pos.x // TILESIZE)
                cy = int(self.mob.pos.y // TILESIZE)

                cx, cy = tile_from_vec(self.mob.pos)

                tiles = self.game.map.get_tile_circle(cx, cy, self.hunt_radius, 'terrain')

                # Filter to only flowers and sort by furthest
                target_tiles = list(filter(lambda tile: tile.terrain_type == TerrainTypes.flowers, tiles))
                if len(target_tiles) == 0: # TODO: or hive distance > vision distance
                    self.target_square = self.home_square
                else:
                    target_tiles.sort(key=lambda tile: (tile.pos - self.mob.pos).magnitude(), reverse=True)
                    self.target_square = target_tiles[int(uniform(0, len(target_tiles)-1))]


            target_vec = (self.target_square.pos - self.mob.pos)
            # Make sure target vec isn't (0,0)
            while target_vec.magnitude() < 1:
                target_vec = target_vec + vec(int(uniform(-10,10)), int(uniform(-10,10)))

            self.vel = target_vec.normalize() * self.speed
            self.rot = 0 - self.vel.angle_to(vec(1, 0)) - (self.bumble_dir * 10)

        # Every tick, adjust angle
        self.rot = self.rot + self.bumble_dir
        self.vel = vec(self.speed, 0).rotate(self.rot)


        return self.rot, self.vel


class PetControlComponent(ControlComponent):
    def __init__(self, game, mob, loyalty):
        super().__init__(game, mob)
        self.speed = 40
        self.rot = 0
        self.vel = vec(0, 0)

        self.huntMode = HunterControlComponent(game, mob)
        self.ambleMode = DrifterControlComponent(game, mob)
        self.activeMode = self.huntMode

        self.loyalty = loyalty
        self.attentionspan = 5000
        self.tick = pg.time.get_ticks()

    def get_control(self):
        now = pg.time.get_ticks()
        if now - self.tick > self.attentionspan:
            if uniform(0, 1) < self.loyalty:
                print('Meow!')
                self.activeMode = self.huntMode
            else:
                print('prrrr')
                self.activeMode = self.ambleMode
            self.tick = now


        return self.activeMode.get_control()