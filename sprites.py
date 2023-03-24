import pygame as pg
from settings import *
from terrain import *
from map import collide_hit_rect
from random import uniform
vec = pg.math.Vector2

"""terrain_types = {
    "dirt": {"name": "dirt", "obstacle": False, "tile": "dirtTile.png", "isotiles": ["isodirtTile.png"], 'img': None, 'iso_images': []},
    "grass": {"name": "grass", "obstacle": False, "tile": "grassTile.png", "isotiles": ["isograssTile.png"], 'img': None, 'iso_images': []},
    "tree": {"name": "tree", "obstacle": True, "tile": "treeTile.png", "isotiles": ["isotreeTile1.png", "isotreeTile2.png"], 'img': None, 'iso_images': []},
    "wall": {"name": "wall", "obstacle": True, "tile": "wallTile.png", "isotiles": ["isowallTile.png"], 'img': None, 'iso_images': []}
}"""

terrain_types = {
    'dirt': Terrain('dirt', False, 'dirtTile.png', ['isodirtTile.png']),
    'grass': Terrain('grass', False, 'grassTile.png', ['isograssTile.png']),
    'tree': Terrain('tree', True, 'treeTile.png', ['isotreeTile1.png', 'isotreeTile2.png', 'isotreeTile1.png']),
    'wall': Terrain('wall', True, 'wallTile.png', ['isowallTile.png']),
    'well': Terrain('wall', True, 'wellTile.png', ['isowellTile.png'])
}

map_char_mapping = {
    ".": terrain_types["dirt"],
    "g": terrain_types["grass"],
    "t": terrain_types["tree"],
    "w": terrain_types["wall"],
    "W": terrain_types["well"]
}


def collide_with_walls(sprite, group, dirr):
    hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
    hits = list(filter(lambda x: x.is_obstacle, hits))
    if hits:
        if dirr == 'x':
            if sprite.hit_rect.centerx > hits[0].hit_rect.centerx:
                sprite.pos.x = hits[0].hit_rect.right
            elif sprite.hit_rect.centerx < hits[0].hit_rect.centerx:
                sprite.pos.x = hits[0].hit_rect.left - sprite.hit_rect.width

            sprite.vel.x = 0
            sprite.hit_rect.x = sprite.pos.x
        elif dirr == 'y':
            if sprite.hit_rect.centery > hits[0].hit_rect.centery:
                sprite.pos.y = (hits[0].hit_rect.bottom)
            elif sprite.hit_rect.centery < hits[0].hit_rect.centery:
                sprite.pos.y = hits[0].hit_rect.top - sprite.hit_rect.height
            sprite.vel.y = 0
            sprite.hit_rect.y = sprite.pos.y



class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.game.player_img
        self.iso_image = self.image

        self.rect = PLAYER_HIT_RECT
        self.hit_rect = PLAYER_HIT_RECT # this is the "physics object" - move this, draw the sprite rect
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.rot = 0
        self.speed = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH

    def get_keys(self):
        self.vel = vec(0, 0)
        self.rot_speed = 0

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.rot_speed = PLAYER_ROT_SPEED
        elif keys[pg.K_RIGHT]:
            self.rot_speed = -PLAYER_ROT_SPEED

        if keys[pg.K_UP]:
            self.speed = min(self.speed + (PLAYER_ACCEL * self.game.dt), PLAYER_SPEED)
        elif keys[pg.K_DOWN]:
            self.speed = max(self.speed - (PLAYER_ACCEL * 4 * self.game.dt), -PLAYER_SPEED/2)
        else:
            self.speed = max(self.speed - (PLAYER_ACCEL * 4 * self.game.dt), 0)
        self.vel = vec(self.speed, 0).rotate(-self.rot)

        if keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if now > self.last_shot + BULLET_RATE:
                self.last_shot = now

                # More spread when moving
                spread = uniform(-GUN_SPREAD, GUN_SPREAD) * (self.speed / PLAYER_SPEED)

                dir = vec(1,0).rotate(-self.rot + spread)
                Bullet(self.game, vec(self.pos), dir)

        if keys[pg.K_d]:
            self.game.dig_dirt(self.pos[0], self.pos[1])


        if keys[pg.K_t]:
            tiles_standing_on(self, self.game.walls)
            print(f"{self.x}, {self.y}")

    def update(self, gamestate):
        self.get_keys()

        self.rot = ( self.rot + ( self.rot_speed * self.game.dt ) ) % 360
        self.image = pg.transform.rotate( self.game.player_img, self.rot)
        self.iso_image = self.game.iso_player_img

        self.rect = self.iso_image.get_rect() if gamestate["iso_mode"] else self.hit_rect

        self.rect.topleft = self.pos

        self.pos += self.vel * self.game.dt
        self.hit_rect.left = self.pos.x

        # print(f"Rect at {self.rect.topleft} is {self.rect.width} wide, hitrect {self.hit_rect.topleft} is {self.hit_rect.width}")
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.top = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img
        self.iso_image = game.mob_img

        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.x = x
        self.y = y
        self.pos = vec(x, y) * TILESIZE
        self.rect.center = self.pos
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rot = 0
        self.health = MOB_HEALTH

        # Components
        self.ControlComponent = None
        self.ImageComponent = None

    def update(self, gamestate):

        # CONTROL
        self.rot, self.vel = self.ControlComponent.get_control()

        # POSITION
        # self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.image = self.ImageComponent.get_image(self.rot) if self.ImageComponent else self.game.mob_img
        self.iso_image = self.image

        self.rect = self.image.get_rect()
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

        # I know, DRY, but this makes the whole iso thing easier
        self.x = self.pos.x
        self.y = self.pos.y

        # COMBAT
        if self.health < 0:
            self.kill()

    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int((self.health * self.rect.width) / MOB_HEALTH)
        self.health_bar = pg.Rect(0,0,width,7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y, terrain_type, anim_frame=0):
        if len(terrain_type.iso_images) > 1:
            self.groups = game.all_sprites, game.walls, game.animated
        else:
            self.groups = game.all_sprites, game.walls

        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.is_obstacle = self.terrain_type.obstacle
        self.anim_frame = anim_frame

        self.image = self.terrain_type.img
        self.iso_image = self.terrain_type.iso_images[self.anim_frame]
        self.hit_rect = self.image.get_rect()
        self.hit_rect.x = x * TILESIZE
        self.hit_rect.y = y * TILESIZE
        self.rect = self.hit_rect

    def change_mode(self, gamestate):
        self.rect = self.iso_image.get_rect() if gamestate["iso_mode"] else self.image.get_rect()
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

    def animate_tick(self):
        self.anim_frame = self.anim_frame + 1
        if self.anim_frame >= len(self.terrain_type.iso_images):
            self.anim_frame = 0
        self.iso_image = self.terrain_type.iso_images[self.anim_frame]


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.transform.rotate(self.game.bullet_img,  dir.angle_to(vec(1, 0)))
        self.rect = self.image.get_rect()

        self.pos = pos
        self.rect.center = pos

        self.vel = dir * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self, gamestate):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.time.get_ticks() > self.spawn_time + BULLET_LIFETIME:
            self.kill()
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()