import pygame as pg
from settings import *
from os import path
from item import item_types

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
    text_col = (0, 0, 0)
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
        self.text_col = Button.text_col

        self.caption = ''
        self.font = pg.font.Font('freesansbold.ttf', 32)

        self.click_callback = None


        # TODO: load button image from name in c'tor
        # self.image =
        self.image = pg.image.load(path.join(Dialog.img_folder, icon)).convert_alpha()
        self.image = pg.transform.scale(self.image, (w - (self.border_width * 2), h - (self.border_width * 2)))

    def draw(self):
        button_rect = pg.Rect(self.x, self.y, self.w, self.h)
        pg.draw.rect(self.surf, self.border_col, button_rect)

        text = self.font.render(self.caption, True, self.text_col, self.border_col)
        textRect = text.get_rect()
        textRect.right = self.x + self.w
        textRect.bottom = self.y + self.h

        self.surf.blit(self.image, (self.x + self.border_width, self.y + self.border_width))
        self.surf.blit(text, textRect)

    def mouse_click(self, pos):
        print('Button click!')
        self.click_callback()
        return True

    def set_caption(self, text):
        self.caption = text


class SpellDialog(Dialog):
    def __init__(self, x, y, w, h, screen, game):
        super().__init__(x, y, w, h, screen, game)

        boltbutton = Button(30, 30, 90, 90, self.surf, 'bolticon.png')
        wellbutton = Button(130, 30, 90, 90, self.surf, 'wellicon.png')
        hivebutton = Button(230, 30, 90, 90, self.surf, 'hiveicon.png')

        boltbutton.click_callback = (lambda: self.game.set_spell('bolt'))
        wellbutton.click_callback = (lambda: self.game.set_spell('well'))
        hivebutton.click_callback = (lambda: self.game.set_spell('hive'))

        self.elements.append(boltbutton)
        self.elements.append(wellbutton)
        self.elements.append(hivebutton)

        self.update()

class InventoryDialog(Dialog):
    def __init__(self, x, y, w, h, screen, game):
        super().__init__(x, y, w, h, screen, game)

        self.update()

    def update(self):
        self.elements = []
        self.add_inv_buttons()
        super().update()

    def add_inv_buttons(self):
        new_button_x = 30
        new_button_y = 30

        for key in self.game.player.inventory.keys():
            button = Button(new_button_x, new_button_y, 90, 90, self.surf, item_types[key].image_path)
            button.set_caption(str(self.game.player.inventory[key]))
            self.elements.append(button)

            new_button_x = new_button_x + 120
            if new_button_x > (self.w - 120):
                new_button_x = 30
                new_button_y = new_button_y + 120



