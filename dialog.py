import pygame as pg
from settings import *
from os import path


class Dialog():
    game_folder = path.dirname(__file__)
    img_folder = path.join(game_folder, "img")
    background_col = (96, 128, 96)

    def __init__(self, x, y, w, h, screen, game):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.screen = screen
        self.surf = pg.Surface((w, h))
        self.game = game

        self.surf.fill(Dialog.background_col)

        self.elements = []

        boltbutton = Button(30, 30, 90, 90, self.surf, 'bolticon.png')
        wellbutton = Button(130, 30, 90, 90, self.surf, 'wellicon.png')

        boltbutton.click_callback = (lambda: self.game.set_spell('bolt'))
        wellbutton.click_callback = (lambda: self.game.set_spell('well'))

        self.elements.append(boltbutton)
        self.elements.append(wellbutton)

        self.update()

    def update(self):
        for el in self.elements:
            el.draw()

    def draw(self):
        self.screen.blit(self.surf, (self.x, self.y))

    def hover(self, pos):
        # If hover overlaps a control, highlight
        pass

    def mouse_click(self, pos):
        # Translate screen pos to dialog coord space
        dialog_pos = (pos[0]-self.x, pos[1]-self.y)
        print(f"click in dlg at {dialog_pos}")

        for el in self.elements:
            if el.x < dialog_pos[0] < el.x + el.w:
                if el.y < dialog_pos[1] < el.y + el.h:
                    close_window = el.mouse_click(pos)
                    break

        if close_window:
            self.game.show_dialog(None)

class Button():

    border_col = (64, 255, 64)
    active_border_col = (64, 255, 255)
    border_width = 4

    def __init__(self, x, y, w, h, surf, icon):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.surf = surf

        self.border_width = Button.border_width
        self.border_col = Button.border_col
        self.active_border_col = Button.active_border_col

        self.click_callback = None


        # TODO: load button image from name in c'tor
        # self.image =
        self.image = pg.image.load(path.join(Dialog.img_folder, icon)).convert_alpha()
        self.image = pg.transform.scale(self.image, (w - (self.border_width * 2), h - (self.border_width * 2)))

    def draw(self):
        button_rect = pg.Rect(self.x, self.y, self.w, self.h)
        pg.draw.rect(self.surf, self.border_col, button_rect)
        # pg.blit(self.image, whatever)
        self.surf.blit(self.image, (self.x + self.border_width, self.y + self.border_width))

    def mouse_click(self, pos):
        print('Button click!')
        self.click_callback()
        return True


