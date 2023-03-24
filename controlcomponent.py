from settings import *
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


class GrazerControlComponent(ControlComponent):
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

