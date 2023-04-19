import pygame as pg
from settings import *
from terrain import *
from item import *
from map import collide_hit_rect
from random import uniform
from math import sin

vec = pg.math.Vector2
from math import floor

# TerrainTypes = Enum('TerrainTypes', ['dirt', 'shortgrass', 'longgrass', 'wall', 'well'])



terrain_types = {
    TerrainTypes.dirt: Terrain(TerrainTypes.dirt, False, 'dirtTile.png', ['isodirtTile.png']),
    TerrainTypes.shortgrass: Terrain(TerrainTypes.shortgrass, False, 'grassTile.png', ['isoshortgrassTile.png']),
    TerrainTypes.longgrass: Terrain(TerrainTypes.longgrass, False, 'grassTile.png', ['isolonggrassTile.png']),
    TerrainTypes.tree: Terrain(TerrainTypes.tree, True, 'treeTile.png', ['isotreeTile1.png', 'isotreeTile2.png', 'isotreeTile1.png']),
    TerrainTypes.wall: Terrain(TerrainTypes.wall, True, 'wallTile.png', ['isowallTile.png']),
    TerrainTypes.well: Terrain(TerrainTypes.wall, True, 'wellTile.png', ['isowellTile.png'])
}

map_char_mapping = {
    ".": terrain_types[TerrainTypes.dirt],
    "g": terrain_types[TerrainTypes.shortgrass],
    "t": terrain_types[TerrainTypes.tree],
    "w": terrain_types[TerrainTypes.wall],
    "W": terrain_types[TerrainTypes.well]
}




def collide_with_walls(sprite, group, dirr):
    hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
    hits = list(filter(lambda x: x.is_obstacle, hits))
    if hits:
        if dirr == 'x':
            if sprite.hit_rect.centerx > hits[0].hit_rect.centerx:
                print(f"Bump up x because {sprite.hit_rect.left} < {hits[0].hit_rect.right}")
                sprite.pos.x = max( hits[0].hit_rect.right + 1, sprite.pos.x + 1)
            elif sprite.hit_rect.centerx < hits[0].hit_rect.centerx:
                print(f"Bump down x because {sprite.hit_rect.right} > {hits[0].hit_rect.left}")
                sprite.pos.x = min(hits[0].hit_rect.left - sprite.hit_rect.width - 1, sprite.pos.x - 1)

            sprite.vel.x = 0
            sprite.hit_rect.x = sprite.pos.x
        elif dirr == 'y':
            if sprite.hit_rect.centery > hits[0].hit_rect.centery:
                print(f"Bump up y because {sprite.hit_rect.top} < {hits[0].hit_rect.bottom}")
                sprite.pos.y = hits[0].hit_rect.bottom + 1
            elif sprite.hit_rect.centery < hits[0].hit_rect.centery:
                print(f"Bump down y because {sprite.hit_rect.bottom} > {hits[0].hit_rect.top}")
                sprite.pos.y = hits[0].hit_rect.top - sprite.hit_rect.height - 1
            sprite.vel.y = 0
            sprite.hit_rect.y = sprite.pos.y



class Player(pg.sprite.Sprite):
    def __init__(self, game, tile_x, tile_y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.image = self.game.player_img
        self.iso_image = self.image

        self.rect = PLAYER_HIT_RECT
        self.hit_rect = PLAYER_HIT_RECT # this is the "physics object" - move this, draw the sprite rect
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(tile_x, tile_y) * TILESIZE
        self.rot = 179
        self.speed = 0
        self.last_shot = 0
        self.max_mp = PLAYER_MP
        self.mp = self.max_mp

        # Select with UI
        self.active_ability = self.game.magic_missile
        self.active_ability_duration = 0.5

        # Inventory: map item type id to count
        self.inventory = {}

    def get_keys(self):
        self.vel = vec(0, 0)
        self.rot_speed = 0

        # This function is for key control of the player
        # Key press events for game stuff (dialogs etc.) goes in game.events()

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
            self.game.do_task(self.active_ability, self.active_ability_duration)



    def set_spell(self, activity, duration):
        self.active_ability = activity
        self.active_ability_duration = duration


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

    def add_inv(self, itemtype, count):
        self.inventory[itemtype] = self.inventory.get(itemtype, 0) + count
        print(f"Now have {self.inventory[itemtype]} items of type {itemtype}")
        return True  # yes we did pick it up - false for inventory limits or weight or whatever


class Mob(pg.sprite.Sprite):
    def __init__(self, game, tile_x, tile_y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img
        self.iso_image = game.mob_img

        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.pos = vec(tile_x, tile_y) * TILESIZE
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
        if self.ControlComponent is not None:
            self.rot, self.vel = self.ControlComponent.get_control()
        else:
            self.rot = 0
            self.vel = vec(0,0)

        # POSITION
        # self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.image = self.ImageComponent.get_image(self.rot) if self.ImageComponent else self.game.mob_img
        self.iso_image = self.image

        self.rect = self.image.get_rect()
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.hit_rect.left = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.top = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

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
    def __init__(self, game, tile_x, tile_y, terrain_type, anim_frame=0):
        if len(terrain_type.iso_images) > 1:
            self.groups = game.all_sprites, game.walls, game.animated
        else:
            self.groups = game.all_sprites, game.walls

        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.terrain_type = terrain_type
        self.is_obstacle = self.terrain_type.obstacle
        self.anim_frame = anim_frame

        self.pos = vec(tile_x, tile_y) * TILESIZE
        self.image = self.terrain_type.img
        self.iso_image = self.terrain_type.iso_images[self.anim_frame]
        self.hit_rect = self.image.get_rect()
        self.hit_rect.topleft = self.pos
        self.rect = self.hit_rect

        self.tile_x = tile_x
        self.tile_y = tile_y

    def change_mode(self, gamestate):
        self.rect = self.iso_image.get_rect() if gamestate["iso_mode"] else self.image.get_rect()
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

    def animate_tick(self):
        self.anim_frame = self.anim_frame + 1
        if self.anim_frame >= len(self.terrain_type.iso_images):
            self.anim_frame = 0
        self.iso_image = self.terrain_type.iso_images[self.anim_frame]


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, target_tile):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.transform.rotate(self.game.bullet_img,  dir.angle_to(vec(1, 0)))
        self.iso_image = self.game.iso_bullet_img
        self.rect = self.image.get_rect()

        self.pos = pos
        self.rect.center = pos
        self.target_tile = target_tile
        self.target_pos = vec((target_tile[0] + 0.5) * TILESIZE, (target_tile[1] + 0.5) * TILESIZE)

        self.vel = dir * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self, gamestate):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.time.get_ticks() > self.spawn_time + BULLET_LIFETIME:
            self.game.killing(self)
        elif (self.pos - self.target_pos).magnitude() < TILESIZE//4:
            # spritecollide targetpos TILESIZE, bullet hit mob
            # else
            if not self.game.missile_hit_mob(self.target_tile[0], self.target_tile[1]):
                self.game.missile_hit_ground(self.target_tile[0], self.target_tile[1])
            self.game.killing(self)

        #if pg.sprite.spritecollideany(self, self.game.walls):
        #    self.kill()

        # If mob in target square, hit
        # else plough target square

class Item(pg.sprite.Sprite):
    def __init__(self, game, tile_x, tile_y, item_type):
        self.game = game
        self.pos = vec(tile_x, tile_y) * TILESIZE
        self.item_type = item_type

        self.groups = game.all_sprites, game.items

        pg.sprite.Sprite.__init__(self, self.groups)

        # Image/rect boilerplate
        self.image = self.item_type.image
        self.iso_image = self.image
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect

        self.bob_tick = uniform(0.0, 1.0)

    def update(self, gamestate):
        self.bob_tick = self.bob_tick + self.game.dt
        bob = sin(self.bob_tick * 6.3) * ITEM_BOB_AMOUNT
        if gamestate["iso_mode"]:
            self.rect.topleft = self.pos + vec(bob, bob)
        else:
            self.rect.topleft = self.pos + vec(0, bob)

    def pickup(self):
        if self.game.add_inv(self.item_type.type, 1):
            self.game.killing(self)
