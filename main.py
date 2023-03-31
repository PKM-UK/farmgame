# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 1
# Project setup
# Video link: https://youtu.be/3UxnelT9aCo
import pygame as pg
import sys
from settings import *
from sprites import *
from imagecomponent import *
from controlcomponent import *
from map import *
from animator import *
from terrain import *
from effect import *
from os import path
from math import fmod, floor

def draw_player_health(surf, x, y, health):
    health = max(health, 0)

    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    filled_length = health * BAR_LENGTH

    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, filled_length, BAR_HEIGHT)

    if health > 0.60:
        col = GREEN
    elif health > 0.30:
        col = YELLOW
    else:
        col = RED

    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2) # specified width = outline rect

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)

        self.terrain_images = {}
        self.terrain_iso_images = {}
        self.load_data()

        self.gamestate = {}
        self.gamestate["iso_mode"] = False

        self.effect_update_interval = 3000
        self.z_sort_interval = 250

        self.last_effect_tick = pg.time.get_ticks()
        self.last_z_sort_tick = self.last_effect_tick




    def load_data(self):
        # Load external stuff for game
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, "img")

        print('Initing Map')
        self.map = Map(path.join(game_folder, "map.txt"))
        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.iso_player_img = pg.image.load(path.join(img_folder, ISO_PLAYER_IMG)).convert_alpha()
        self.iso_player_img = pg.transform.scale(self.iso_player_img, (TILESIZE * 2, floor((self.iso_player_img.get_rect().height / self.iso_player_img.get_rect().width) * TILESIZE * 2)))
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()

        for tkey in terrain_types.keys():
            ttype = terrain_types[tkey]
            # name from ttype
            tname = ttype.name
            # load and transform, put in appropriate map
            img = pg.image.load(path.join(img_folder, ttype.tile)).convert_alpha()
            img = pg.transform.scale(img, (TILESIZE, TILESIZE))
            # self.terrain_images[tname] = img
            terrain_types[tkey].img = img

            for isotilepath in ttype.isotiles:
                iso_img = pg.image.load(path.join(img_folder, isotilepath)).convert_alpha()
                iso_img = pg.transform.scale(iso_img, (TILESIZE * 2, floor(
                    (iso_img.get_rect().height / iso_img.get_rect().width) * TILESIZE * 2)))
                # self.terrain_iso_images[tname] = iso_img
                terrain_types[tkey].iso_images.append(iso_img)

        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()

        pass

    def new(self):
        # initialize all variables and do all the setup for a new game
        print('New game')
        self.all_sprites = pg.sprite.Group()
        self.ordered_sprites = []
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.animated = pg.sprite.Group()

        # Give us row index and line of file
        print('Adding sprites')
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == 'z':
                    mob_sprite = Mob(self, col, row)
                    mob_sprite.ImageComponent = GoatImageComponent(self, mob_sprite)
                    mob_sprite.ControlComponent = GrazerControlComponent(self, mob_sprite)
                    self.ordered_sprites.append(mob_sprite)

                    tile = '.'   # Dirty hax to put dirt under mobs
                terrain_type = map_char_mapping[tile]
                wall_sprite = Wall(self, col, row, terrain_type)
                self.map.add_sprite(col, row, wall_sprite)
                self.ordered_sprites.append(wall_sprite)

        self.player = Player(self, 6, 1)

        # Now sort walls by Z
        self.sort_sprites()

        self.camera = Camera(self.map.pixelwidth, self.map.pixelheight, self.gamestate["iso_mode"])

        self.anim = Animator(self.animated)

        self.effects = {'water': WateredEffect(self, 'water', WATERED_EFFECT_P)}


        self.change_mode()

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update(self.gamestate)
        self.camera.update(self.player)

        # Mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            self.player.health -= MOB_DAMAGE
            recoilvect = vec(MOB_RECOIL,0).rotate(180-hit.rot)
            hit.vel += recoilvect

            knockbackvect = vec(MOB_KNOCKBACK,0).rotate(-hit.rot)
            self.player.pos += knockbackvect
            # hit.vel = vec(0, 0)

        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            hit.vel += hits[hit][0].vel * 0.05
            hit.health -= BULLET_DMG

        # Do things that tick
        self.anim.tick()

        now = pg.time.get_ticks()
        if now - self.last_effect_tick > self.effect_update_interval:
            self.last_effect_tick = now
            print('doing fx')
            for effect_name in ['water']:
                effect = self.effects[effect_name]
                e_squares = self.map.get_affected_squares(effect_name)
                for square in e_squares:
                    # STUB
                    x = square[0]
                    y = square[1]

                    rnd = uniform(0.0,1.0)
                    if self.map.sprites[y][x] and self.map.sprites[y][x].terrain_type.name in effect.affected_types and rnd < effect.probability:
                        effect.do_thing(square, self.map.sprites[y][x])

        if now - self.last_z_sort_tick > self.z_sort_interval:
            self.sort_sprites()

    def draw_grid(self):
        for x in range(0, WIDTH+TILESIZE, TILESIZE):
            xfloat = x + fmod(self.camera.viewport.left, TILESIZE)
            line_rect = pg.Rect(x, 0, 0, 0)
            line_rect2 = pg.Rect(x, HEIGHT, 0, 0)
            camera_rect = self.camera.apply_rect(line_rect)
            camera_rect2 = self.camera.apply_rect(line_rect2)

            # pg.draw.line(self.screen, LIGHTGREY, (xfloat, 0), (xfloat, HEIGHT))
            pg.draw.line(self.screen, WHITE, camera_rect.topleft, camera_rect2.topleft)
        for y in range(0, HEIGHT+TILESIZE, TILESIZE):
            yfloat = y + fmod(self.camera.viewport.top, TILESIZE)

            line_rect = pg.Rect(0, y, 0, 0)
            line_rect2 = pg.Rect(WIDTH, y, 0, 0)
            camera_rect = self.camera.apply_rect(line_rect)
            camera_rect2 = self.camera.apply_rect(line_rect2)

            pg.draw.line(self.screen, WHITE, camera_rect.topleft, camera_rect2.topleft)



        for x in range (0,5*TILESIZE, TILESIZE):
            for y in range (0,5*TILESIZE, TILESIZE):
                iso_gridpoint = self.camera.apply_rect(pg.Rect(x, y, 5, 5))

                pg.draw.line(self.screen, RED, (iso_gridpoint.left, iso_gridpoint.top),(iso_gridpoint.right, iso_gridpoint.bottom))

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(BGCOLOR)

        # self.draw_grid()

        for sprite in self.ordered_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()

            self.screen.blit(sprite.iso_image if self.gamestate["iso_mode"] else sprite.image, self.camera.apply(sprite))

            if self.gamestate.get("debug_draw"):
                pg.draw.rect(self.screen, BLUE, self.camera.apply(sprite), 1)

        self.screen.blit(self.player.iso_image if self.gamestate["iso_mode"] else self.player.image, self.camera.apply(self.player))
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)

        # self.draw_grid()
        # draw_player_heading(self.screen)




        # Draw hitboxes
        for sprite in self.mobs:
            pg.draw.rect(self.screen, RED, self.camera.apply_rect(sprite.hit_rect), 2)
            pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(sprite.rect), 2)

        pg.draw.rect(self.screen, RED, self.camera.apply_rect(self.player.hit_rect), 2)
        pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(self.player.rect), 2)


        pg.display.flip()

    def change_mode(self):
        self.gamestate["iso_mode"] = not self.gamestate["iso_mode"]
        self.camera.set_iso(self.gamestate["iso_mode"])
        for wall in self.walls:
            wall.change_mode(self.gamestate)

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                elif event.key == pg.K_i:
                    self.change_mode()


    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

    def tiles_standing_on(self, sprite, group):
        stands = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        return stands

    def add_terrain(self, col, row, terrain_type):
        wall_sprite = Wall(self, col, row, terrain_type)
        wall_sprite.change_mode(self.gamestate)
        self.ordered_sprites.append(wall_sprite)
        self.sort_sprites()

        self.map.add_sprite(col, row, wall_sprite)

    def sort_sprites(self):
        self.ordered_sprites.sort(key=lambda s: s.x + s.y)

    def killing(self, sprite):
        self.ordered_sprites.remove(sprite)
        sprite.kill()

    def dig_dirt(self, x, y):
        stands = self.tiles_standing_on(self.player, self.walls)
        grid_ref_x = int((x + (TILESIZE / 2)) // TILESIZE)
        grid_ref_y = int((y + (TILESIZE / 2)) // TILESIZE)
        print(f"We'r at grid {grid_ref_x}, {grid_ref_y}")

        for stand in stands:
            print(f"{stand.x}, {stand.y}, {stand.terrain_type}")
            if stand.x == grid_ref_x and stand.y == grid_ref_y and stand.terrain_type.name == TerrainTypes.dirt:

                self.add_terrain(grid_ref_x, grid_ref_y, terrain_types[TerrainTypes.well])

                # Add effect
                self.map.add_effect_circle(stand.x, stand.y, WATERED_EFFECT_R, 'water')

    def eat_grass(self, x, y):
        eat_sprite = self.map.get_sprite_at(x, y)
        if eat_sprite.terrain_type.name == TerrainTypes.longgrass:
            self.killing(eat_sprite)
            self.add_terrain(x, y, terrain_types[TerrainTypes.shortgrass])



# create the game object
g = Game()
g.show_start_screen()#
while True:
    g.new()
    g.run()
    g.show_go_screen()