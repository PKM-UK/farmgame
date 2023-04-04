# define some colors (R, G, B)
import pygame as pg
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 64, 255)

# game settings
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = DARKGREY

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

PLAYER_SPEED = 400
PLAYER_ACCEL = 1300
PLAYER_ROT_SPEED = 250
PLAYER_IMG = 'manBlue_gun.png'
ISO_PLAYER_IMG = 'isoPlayer.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, TILESIZE-10, TILESIZE-10)
GUN_SPREAD = 10
PLAYER_HEALTH = 100
PLAYER_INITIAL_REACH = 5

BULLET_IMG = "bullet.png"
BULLET_SPEED = 1000
BULLET_LIFETIME = 1000
BULLET_RATE = 250
BULLET_DMG = 10

MOB_SPEED = 100
MOB_ROT_SPEED = 0
MOB_IMG = 'zom.png'
MOB_HIT_RECT = pg.Rect(0, 0, TILESIZE-10, TILESIZE-10)
MOB_HEALTH = 100
MOB_DAMAGE = 5
MOB_RECOIL = 20
MOB_KNOCKBACK = 5

WALL_IMG = 'wallTile.png'
ISO_WALL_IMG = 'isowallTile.png'

EFFECT_FREQ = 3000
WATERED_EFFECT_R = 4
WATERED_EFFECT_P = 0.05

GOAT_EAT_TIME = 10000
GOAT_ATTENTION_SPAN = 2000
GOAT_VISION_DISTACE = 9