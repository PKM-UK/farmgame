import pygame as pg

class Animator:
    def __init__(self, group):
        self.group = group
        self.lasttick = pg.time.get_ticks()
        self.update_interval = 250

    def tick(self):
        now = pg.time.get_ticks()
        if now - self.lasttick > self.update_interval:
            self.lasttick = now

            for sprite in self.group.sprites():
                sprite.animate_tick()