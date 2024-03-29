# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 1
# Project setup
# Video link: https://youtu.be/3UxnelT9aCo
import pygame as pg
import sys
import pickle
import copy

from settings import *
from sprites import *
from imagecomponent import *
from controlcomponent import *
from componentfactory import comp
from map import *
from animator import *
from terrain import *
from effect import *
from task import *
from dialog import *
from gamemode import *
from os import path
from math import fmod, floor


def draw_player_mp(surf, x, y, health):
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
        self.img_folder = ''
        self.load_data()

        self.gamestate = {}
        self.gamestate["iso_mode"] = False
        self.gamestate["debug_draw"] = False

        self.effect_update_interval = 3000
        self.z_sort_interval = 250

        self.last_effect_tick = pg.time.get_ticks()
        self.last_z_sort_tick = self.last_effect_tick

        # Should this all belong to Player?
        self.active_task = None
        # These should be members of Task we get when needed?
        self.task_continuing = False
        self.task_progress = 0

        self.active_dialog = None

        self.dialogs = {}
        self.spells = {}

        self.hx = 0
        self.hy = 0

    def show_dialog(self, name):
        if name is not None and self.active_dialog != self.dialogs[name]:
            self.dialogs[name].update()
            self.active_dialog = self.dialogs[name]
        else:
            self.active_dialog = None

    def load_data(self):
        # Load external stuff for game
        game_folder = path.dirname(__file__)
        self.img_folder = path.join(game_folder, "img")

        print('Initing Map')
        self.map = Map(path.join(game_folder, "map.txt"))
        self.player_img = pg.image.load(path.join(self.img_folder, PLAYER_IMG)).convert_alpha()
        self.iso_player_img = pg.image.load(path.join(self.img_folder, ISO_PLAYER_IMG)).convert_alpha()
        # self.iso_player_img = pg.transform.scale(self.iso_player_img, (TILESIZE * 2, floor((self.iso_player_img.get_rect().height / self.iso_player_img.get_rect().width) * TILESIZE * 2)))
        self.mob_img = pg.image.load(path.join(self.img_folder, MOB_IMG)).convert_alpha()

        for tkey in terrains.keys():
            ttype = terrains[tkey]
            # name from ttype
            tname = ttype.name
            # load and transform, put in appropriate map
            img = pg.image.load(path.join(self.img_folder, ttype.tile)).convert_alpha()
            img = pg.transform.scale(img, (TILESIZE, TILESIZE))
            # self.terrain_images[tname] = img
            terrains[tkey].img = img

            for isotilepath in ttype.isotiles:
                iso_img = pg.image.load(path.join(self.img_folder, isotilepath)).convert_alpha()
                iso_img = pg.transform.scale(iso_img, (TILESIZE * 2, floor(
                    (iso_img.get_rect().height / iso_img.get_rect().width) * TILESIZE * 2)))
                # self.terrain_iso_images[tname] = iso_img
                terrains[tkey].iso_images.append(iso_img)

        for ikey in item_types.keys():
            itype = item_types[ikey]
            image = pg.image.load(path.join(self.img_folder, itype.image_path)).convert_alpha()
            # self.terrain_images[tname] = img
            item_types[ikey].image = image

        # Misc images
        self.poop_overlay_image = pg.image.load(path.join(self.img_folder, "poopOverlay.png")).convert_alpha()
        self.poop_overlay_image = pg.transform.scale(self.poop_overlay_image, (TILESIZE * 2, floor(
            (self.poop_overlay_image.get_rect().height / self.poop_overlay_image.get_rect().width) * TILESIZE * 2)))


        self.bullet_img = pg.image.load(path.join(self.img_folder, BULLET_IMG)).convert_alpha()
        self.iso_bullet_img = pg.image.load(path.join(self.img_folder, ISO_BULLET_IMG)).convert_alpha()

        pass

    def new(self):
        # initialize all variables and do all the setup for a new game
        print('New game')
        self.all_sprites = pg.sprite.Group()
        self.ordered_sprites = []
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.hostile_mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.animated = pg.sprite.Group()
        self.items = pg.sprite.Group()

        # Give us row index and line of file
        print('Adding sprites')
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == 'z':
                    self.add_mob(col, row, 'GoatImageComponent', 'GrazerControlComponent')
                    tile = '.'   # Dirty hax to put dirt under mobs
                elif tile == 'p':
                    self.player = Player(self, col, row)
                    tile = '.'

                terrain_type = map_char_mapping[tile]
                wall_sprite = Wall(self, col, row, terrain_type)
                self.map.add_sprite(col, row, wall_sprite)
                self.ordered_sprites.append(wall_sprite)


        # Now sort walls by Z
        self.sort_sprites()

        self.camera = Camera(self.map.pixelwidth, self.map.pixelheight, self.gamestate["iso_mode"])

        self.anim = Animator(self.animated)

        self.effects = {'water': WateredEffect(self, 'water', WATERED_EFFECT_P),
                        'pollinate': PollinateEffect(self, 'pollinate', POLLINATE_EFFECT_P),
                        'fertile': FertileEffect(self, 'fertile', FERTILE_EFFECT_P)}

        # Set up UI now we have player etc.
        self.dialogs = {'spells': SpellDialog(100, 50, 400, 360, self.screen, self),
                        'inventory': InventoryDialog(100, 50, 400, 300, self.screen, self),
                        'quests': QuestsDialog(100, 50, 400, 300, self.screen, self),
                        'menu': MenuDialog(100, 50, 400, 300, self.screen, self)}

        self.spells = {'bolt': (self.magic_missile, 0.25),
                       'well': (self.dig_dirt, 2),
                       'hive': (self.build_hive, 3),
                       'compost': (self.fertilise, 1),
                       'sapling': (self.plant_tree, 2),
                       'spawngoat': (self.spawngoat, 1),
                       'spawncat': (self.spawncat, 0.5)}

        self.gamemode = Story(self)

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
        # What are we waiting to see this tick?
        self.task_continuing = False
        # update portion of the game loop
        self.all_sprites.update(self.gamestate)
        self.camera.update(self.player)

        # Mouse input
        self.mouse_hover()

        # Mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.hostile_mobs, False, collide_hit_rect)
        for hit in hits:
            self.player.mp -= MOB_DAMAGE
            recoilvect = vec(MOB_RECOIL,0).rotate(180-hit.rot)
            hit.vel += recoilvect

            knockbackvect = vec(MOB_KNOCKBACK,0).rotate(-hit.rot)
            self.player.pos += knockbackvect
            # hit.vel = vec(0, 0)

        # Don't hit mobs while in flight, have to hit their square
        """hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            hit.vel += hits[hit][0].vel * 0.05
            hit.health -= BULLET_DMG"""

        # Player picks up item
        hits = pg.sprite.spritecollide(self.player, self.items, False, collide_hit_rect)
        for hit in hits:
            hit.pickup()

        # Do things that tick
        self.anim.tick()

        now = pg.time.get_ticks()
        if now - self.last_effect_tick > self.effect_update_interval:
            self.last_effect_tick = now
            did_effect = False
            for effect_name in self.effects.keys():
                effect = self.effects[effect_name]
                e_squares = self.map.get_affected_squares(effect_name)
                for square in e_squares:
                    # STUB
                    x = square[0]
                    y = square[1]

                    rnd = uniform(0.0,1.0)
                    if self.map.sprites[y][x] and self.map.sprites[y][x].terrain_type in effect.affected_types and rnd < effect.probability:
                        effect.do_thing(square, self.map.sprites[y][x])
                        did_effect = True

            if did_effect:
                self.gamemode.check_progression()

        if now - self.last_z_sort_tick > self.z_sort_interval:
            self.sort_sprites()

        # End of update - close Tasks not updated this tick
        if self.active_task is not None and self.task_continuing is False:
            self.active_task = None

    def mouse_hover(self):
        # Highlight game elements if no dialog
        # Highlight buttons if dialog
        if self.active_dialog is None:
            (self.hx, self.hy) = self.camera.get_hovered_tile(pg.mouse.get_pos())
        else:
            self.active_dialog.hover(pg.mouse.get_pos())

    def mouse_click(self):
        clickpos = pg.mouse.get_pos()
        if self.active_dialog is not None:
            self.active_dialog.mouse_click(clickpos)

    def draw_tile_boundaries(self, tx, ty, colour):
        # Isofy a tile, draw the resultant rhombus
        wrect = pg.Rect(tx*TILESIZE, ty*TILESIZE, TILESIZE*2 if self.gamestate["iso_mode"] else TILESIZE, TILESIZE)
        trect = self.camera.apply_rect(wrect)

        if self.gamestate["iso_mode"]:
            # Connect middles of sides
            # midtop, midleft, midbottom, midright
            pg.draw.line(self.screen, colour, trect.midtop, trect.midright, 2)
            pg.draw.line(self.screen, colour, trect.midbottom, trect.midright, 2)
            pg.draw.line(self.screen, colour, trect.midtop, trect.midleft, 2)
            pg.draw.line(self.screen, colour, trect.midbottom, trect.midleft, 2)
        else:
            pg.draw.rect(self.screen, colour, trect, 2)



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

    def draw_pos_cross(self, pos):
        pos_rect = self.camera.apply_rect(pg.Rect(pos[0], pos[1], 0, 0))
        pg.draw.line(self.screen, WHITE, pos_rect.topleft-vec(5,5), pos_rect.topleft+vec(5,5))
        pg.draw.line(self.screen, WHITE, pos_rect.topleft - vec(-5, 5), pos_rect.topleft + vec(-5, 5))

    def draw_pos_plus(self, pos):
        pos_rect = self.camera.apply_rect(pg.Rect(pos[0], pos[1], 0, 0))
        pg.draw.line(self.screen, RED, pos_rect.topleft-vec(0,5), pos_rect.topleft+vec(0,5))
        pg.draw.line(self.screen, RED, pos_rect.topleft - vec(5, 0), pos_rect.topleft + vec(5, 0))

    def draw_progress_indicator(self, x, y, progress):
        BAR_LENGTH = 50
        BAR_HEIGHT = 10
        filled_length = progress * BAR_LENGTH

        srect = self.camera.apply_rect(pg.Rect(x*TILESIZE, y*TILESIZE, 0, 0))
        sx = srect.x
        sy = srect.y

        outline_rect = pg.Rect(sx-(BAR_LENGTH//2), sy-(TILESIZE//2), BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pg.Rect(sx-(BAR_LENGTH//2), sy-(TILESIZE//2), filled_length, BAR_HEIGHT)

        pg.draw.rect(self.screen, WHITE, fill_rect)
        pg.draw.rect(self.screen, WHITE, outline_rect, 2)  # specified width = outline rect

    def draw_game_ui(self):
        # Draw cursor on hovered tile
        cursor_colour = RED
        if (self.can_do_task()):
            cursor_colour = BLUE
        self.draw_tile_boundaries(self.hx, self.hy, cursor_colour)

        # Draw UI
        draw_player_mp(self.screen, 10, 10, self.player.mp / self.player.max_mp)

        

        if self.task_continuing:
            self.draw_progress_indicator(self.hx, self.hy, self.task_progress)
        # self.draw_grid()
        # draw_player_heading(self.screen)

    def draw_dialog_ui(self):
        if self.active_dialog is not None:
            self.active_dialog.draw()

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(BGCOLOR)

        # self.draw_grid()

        screen_window_rect = pg.Rect(0, 0, WIDTH, HEIGHT)
        for sprite in self.ordered_sprites:

            sprite_screen_pos = self.camera.apply(sprite)
            if pg.Rect.colliderect(sprite_screen_pos, screen_window_rect):

                if isinstance(sprite, Mob):
                    sprite.draw_health()

                self.screen.blit(sprite.iso_image if self.gamestate["iso_mode"] else sprite.image, self.camera.apply(sprite))

                if isinstance(sprite, Wall):
                    tile_fx = self.map.get_effects(sprite.tile_x, sprite.tile_y)
                    ttype = sprite.terrain_type
                    if tile_fx and ((ttype == TerrainTypes.dirt and 'water' in tile_fx) or \
                                    (ttype in [TerrainTypes.shortgrass, TerrainTypes.longgrass] and 'fertile' in tile_fx)):
                        self.screen.blit(self.poop_overlay_image, self.camera.apply(sprite))

        self.screen.blit(self.player.iso_image if self.gamestate["iso_mode"] else self.player.image, self.camera.apply(self.player))

        if self.gamestate.get("debug_draw"):
            for sprite in self.ordered_sprites:
                self.draw_pos_cross(sprite.rect.topleft)
                self.draw_pos_plus((sprite.pos))
                pg.draw.rect(self.screen, BLUE, self.camera.apply(sprite), 1)

        self.draw_game_ui()

        self.draw_dialog_ui()

        pg.display.flip()

    def can_do_task(self):
        if self.player.active_ability == self.build_hive and self.player.inventory[ItemTypes.grass] < 10:
            return False
        # TODO: other logic for correct hover type

        cursor_distance = (self.player.pos.x // TILESIZE - self.hx) ** 2 + (
                    self.player.pos.y // TILESIZE - self.hy) ** 2
        return cursor_distance <= PLAYER_INITIAL_REACH**2

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
                    self.show_dialog('menu')
                elif event.key == pg.K_TAB:
                    self.show_dialog('spells')
                elif event.key == pg.K_e:
                    self.show_dialog('inventory')
                elif event.key == pg.K_q:
                    self.show_dialog('quests')
                elif event.key == pg.K_i:
                    self.change_mode()
                elif event.key == pg.K_d:
                    self.gamestate["debug_draw"] = not self.gamestate["debug_draw"]
                elif event.key == pg.K_s:
                    self.savegame("quicksave.sav")
                elif event.key == pg.K_l:
                    self.loadgame("quicksave.sav")
            if event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_click()



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

    def add_item(self, col, row, item_type):
        grass = Item(self, col, row, item_types[item_type])
        self.ordered_sprites.append(grass)

    def add_mob(self, col, row, ic_type, cc_type):
        mob_sprite = Mob(self, col, row)
        mob_sprite.imageComponent = comp(ic_type, self, mob_sprite)
        mob_sprite.controlComponent = comp(cc_type, self, mob_sprite)
        self.all_sprites.add(mob_sprite)
        self.mobs.add(mob_sprite)
        self.ordered_sprites.append(mob_sprite)

    def sort_sprites(self):
        self.ordered_sprites.sort(key=lambda s: s.pos.x + s.pos.y + ((TILESIZE*2) if isinstance(s, Mob) or isinstance(s, Bullet) else 0))

    def killing(self, sprite):
        self.ordered_sprites.remove(sprite)
        sprite.kill()

    # I should make the Task ahead of time with its duration, completion function and "can do this?" callback
    def do_task(self, func, duration):
        if self.can_do_task():
            if self.active_task is None:
                self.active_task = Task(duration, func, floor(self.hx), floor(self.hy))
                self.task_continuing = True
            else:
                complete = self.active_task.update(self.dt)

                if complete:
                    self.active_task = None
                    self.gamemode.check_progression()
                else:
                    self.task_progress = self.active_task.progress / self.active_task.duration
                    self.task_continuing = True





    # Stuff affecting ground tiles

    def eat_grass(self, x, y):
        eat_sprite = self.map.get_sprite_at(x, y)
        if eat_sprite.terrain_type == TerrainTypes.longgrass:
            self.killing(eat_sprite)
            self.add_terrain(x, y, TerrainTypes.shortgrass)

    def missile_hit_ground(self, x, y):
        target_sprite = self.map.get_sprite_at(x, y)
        if target_sprite.terrain_type == TerrainTypes.dirt:
            self.map.add_effect(x, y, 'water')
        elif target_sprite.terrain_type in [TerrainTypes.longgrass, TerrainTypes.flowers]:
            self.killing(target_sprite)
            self.add_terrain(x, y, TerrainTypes.shortgrass)
            self.add_item(x, y, ItemTypes.grass)

    def missile_hit_mob(self, x, y):
        target_pos = vec(((x + 0.5) * TILESIZE), ((y + 0.5) * TILESIZE))

        #lmobs = list(self.mobs)
        #hits = filter(lmobs, (lambda m: (m.pos - target_pos).magnitude() < TILESIZE))

        hits = [m for m in list(self.mobs) if (m.pos - target_pos).magnitude() < TILESIZE]
        if len(hits) > 0:
            hits[0].health -= BULLET_DMG
            return True
        else:
            return False





    # Spell effects: must take tile co-ords as arguments

    def magic_missile(self, x, y):
        target_pos = vec((x + 0.5) * TILESIZE, (y + 0.5) * TILESIZE)
        target_vec_dir = (target_pos - self.player.pos).normalize()
        missile = Bullet(self, vec(self.player.pos), target_vec_dir, (x, y))
        self.ordered_sprites.append(missile)

    def dig_dirt(self, x, y):
        target_sprite = self.map.get_sprite_at(x, y)
        if target_sprite.terrain_type in [TerrainTypes.dirt, TerrainTypes.shortgrass, TerrainTypes.longgrass]:
            self.killing(target_sprite)
            self.add_terrain(x, y, TerrainTypes.well)
            # Add effect
            self.map.add_effect_circle(x, y, WATERED_EFFECT_R, 'water')

    def build_hive(self, x, y):
        target_sprite = self.map.get_sprite_at(x, y)
        if target_sprite.terrain_type in [TerrainTypes.shortgrass, TerrainTypes.longgrass] and self.player.inventory[ItemTypes.grass] >= 10:
            self.player.add_inv(ItemTypes.grass, -10)
            self.killing(target_sprite)
            self.add_terrain(x, y, TerrainTypes.hive)
            for p in range(3):
                col = x + int(uniform(0, 4) - 2)
                row = y + int(uniform(0, 4) - 2)
                self.add_mob(col, row, 'BeeImageComponent', 'BumbleControlComponent')

            # Add effect
            self.map.add_effect_circle(x, y, POLLINATE_EFFECT_R, 'pollinate')

    def fertilise(self, x, y):
        target_sprite = self.map.get_sprite_at(x, y)
        if target_sprite.terrain_type in [TerrainTypes.dirt, TerrainTypes.shortgrass, TerrainTypes.longgrass]:
            self.map.add_effect(x, y, 'fertile')

    def plant_tree(self, x, y):
        target_sprite = self.map.get_sprite_at(x, y)
        if target_sprite.terrain_type in [TerrainTypes.dirt, TerrainTypes.shortgrass, TerrainTypes.longgrass]:
            if 'fertile' in self.map.get_effects(x, y):
                self.killing(target_sprite)
                self.add_terrain(x, y, TerrainTypes.sapling)

    # Untested!
    def spawngoat(self, x, y):
        self.add_mob(x, y, 'GoatImageComponent', 'GrazerControlComponent')

    def spawncat(self, x, y):
        self.add_mob(x, y, 'CatImageComponent', 'PetControlComponent')

    def set_spell(self, name):
        self.player.set_spell(*self.spells[name])

    def add_inv(self, itemtype, count):
        pickedup = self.player.add_inv(itemtype, count)
        if pickedup:
            self.gamemode.check_progression()
        return pickedup


    """ Write out:
    map.sprites
    map.effects
    self.player
    self.ordered_sprites (might have to reset sprite groups when loading)
    local state: self.active_spell, timers etc"""

    def savegame(self, savefile):
        # Serialising Player is a faff, just do props
        # Not doing active_ability because having a callback to game requires game
        # TODO: replace self.active_ability with enum index into a dict so we can serialise it
        player_info = (self.player.pos, self.player.vel, self.player.rot, self.player.inventory, self.player.max_mp )

        # Wall info for each wall
        ts_infos = []
        for s in self.walls:
            tinfo = {}
            tinfo['type'] = s.terrain_type
            tinfo['tile_x'] = s.tile_x
            tinfo['tile_y'] = s.tile_y
            ts_infos.append(tinfo)

        # Mob info struct for each mob
        mobs_infos = []
        for s in self.mobs:
            mob_info = {}
            mob_info['pos'] = s.pos
            mob_info['vel'] = s.vel
            mob_info['rot'] = s.rot
            mob_info['health'] = s.health
            mob_info['ic_type'] = type(s.imageComponent).__name__
            mob_info['cc_type'] = type(s.controlComponent).__name__

            mobs_infos.append(mob_info)

        # Serialization
        game_folder = path.dirname(__file__)
        save_folder = path.join(game_folder, "save")

        with open(path.join(save_folder, "test.pickle"), "wb") as outfile:
            # pickle.dump((player_info, self.map.sprites, mobs_infos), outfile)
            # ts_infos
            pickle.dump((player_info, ts_infos, mobs_infos, self.map.effects), outfile)
        print(f"Written {len(ts_infos)}, {len(mobs_infos)}, {len(self.map.effects)}x{len(self.map.effects[0])} objects")

        print(f"Currently {len(self.ordered_sprites)}={len(self.all_sprites)} sprites ({len(self.walls)} terrain, {len(self.mobs)} mobs)")

    def loadgame(self, savefile):

        # Preparation: nuke and repave
        for s in self.ordered_sprites:
            s.kill()
        self.ordered_sprites = []

        # Deserialization
        game_folder = path.dirname(__file__)
        save_folder = path.join(game_folder, "save")

        with open(path.join(save_folder, "test.pickle"), "rb") as infile:
            # (self.map.sprites, self.map.effects, self.player, self.ordered_sprites) = pickle.load(infile)
            (player_info, tinfos, mobs_infos, self.map.effects) = pickle.load(infile)

        print(f"Read {len(tinfos)}, {len(mobs_infos)}, {len(self.map.effects)}x{len(self.map.effects[0])} objects")

            # self.debug_goat = pickle.load(infile)

        # Restoration
        for tinfo in tinfos:
            col = tinfo['tile_x']
            row = tinfo['tile_y']
            wall_sprite = Wall(self, col, row, tinfo['type'])
            self.map.add_sprite(col, row, wall_sprite)
            wall_sprite.change_mode(self.gamestate)
            self.ordered_sprites.append(wall_sprite)
            self.all_sprites.add(wall_sprite)

        (self.player.pos, self.player.vel, self.player.rot, self.player.inventory, self.player.max_mp) = player_info

        for info in mobs_infos:
            (col, row) = tile_from_vec(info['pos'])
            self.add_mob(col, row, info['ic_type'], info['cc_type'])

        print("Reconstructed objects")
        print(
            f"Loaded {len(self.ordered_sprites)}={len(self.all_sprites)} sprites ({len(self.walls)} terrain, {len(self.mobs)} mobs)")


# create the game object
g = Game()
g.show_start_screen()#
while True:
    g.new()
    g.run()
    g.show_go_screen()