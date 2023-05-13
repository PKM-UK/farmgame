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
        self.surf.fill(Dialog.background_col)
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

        close_window = False

        for el in self.elements:
            if el.x < dialog_pos[0] < el.x + el.w:
                if el.y < dialog_pos[1] < el.y + el.h:
                    close_window = el.mouse_click(pos)
                    break

        # close on click outside
        if dialog_pos[0] < 0 or dialog_pos[0] > self.w or dialog_pos[1] < 0 or dialog_pos[1] > self.h:
            close_window = True

        if close_window:
            self.game.show_dialog(None)

class Button():

    border_col = (64, 255, 64)
    active_border_col = (64, 255, 255)
    disabled_border_col = (96, 96, 96)
    text_col = (0, 0, 0)
    border_width = 4

    def __init__(self, x, y, w, h, surf, icon):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.surf = surf
        self.active = True

        self.border_width = Button.border_width
        self.border_col = Button.border_col
        self.disabled_border_col = Button.disabled_border_col
        self.active_border_col = Button.active_border_col
        self.text_col = Button.text_col

        self.caption = ''
        self.font = pg.font.Font('freesansbold.ttf', 32)

        self.click_callback = None

        self.set_image(icon, w, h)

    def draw(self):

        button_rect = pg.Rect(self.x, self.y, self.w, self.h)

        if self.active:
            pg.draw.rect(self.surf, self.border_col, button_rect)
            if self.image:
                self.surf.blit(self.image, (self.x + self.border_width, self.y + self.border_width))
        else:
            pg.draw.rect(self.surf, self.disabled_border_col, button_rect)

        if self.caption != '':
            text = self.font.render(self.caption, True, self.text_col, self.border_col)
            textRect = text.get_rect()
            textRect.right = self.x + self.w
            textRect.bottom = self.y + self.h

            self.surf.blit(text, textRect)

    def mouse_click(self, pos):
        if self.active and self.click_callback:
            self.click_callback()
        return self.active

    def set_caption(self, text):
        self.caption = text

    def set_image(self, icon, w, h):
        # TODO: don't load duplicate images etc.
        if icon:
            self.image = pg.image.load(path.join(Dialog.img_folder, icon)).convert_alpha()
            self.image = pg.transform.scale(self.image, (w - (self.border_width * 2), h - (self.border_width * 2)))
        else:
            self.image = None


class SpellDialog(Dialog):
    def __init__(self, x, y, w, h, screen, game):
        super().__init__(x, y, w, h, screen, game)

        self.boltbutton = Button(30, 30, 90, 90, self.surf, 'bolticon.png')
        self.wellbutton = Button(130, 30, 90, 90, self.surf, 'wellicon.png')
        self.hivebutton = Button(230, 30, 90, 90, self.surf, 'hiveicon.png')
        self.fertilisebutton = Button(30, 130, 90, 90, self.surf, 'poopItem.png')
        self.planttreebutton = Button(130, 130, 90, 90, self.surf, 'saplingTile.png')
        self.goatbutton = Button(30, 230, 90, 90, self.surf, 'lgoat.png')
        self.catbutton = Button(130, 230, 90, 90, self.surf, 'lcat.png')

        self.boltbutton.click_callback = (lambda: self.game.set_spell('bolt'))
        self.wellbutton.click_callback = (lambda: self.game.set_spell('well'))
        self.hivebutton.click_callback = (lambda: self.game.set_spell('hive'))
        self.fertilisebutton.click_callback = (lambda: self.game.set_spell('compost'))
        self.planttreebutton.click_callback = (lambda: self.game.set_spell('sapling'))
        self.goatbutton.click_callback = (lambda: self.game.set_spell('spawngoat'))
        self.catbutton.click_callback = (lambda: self.game.set_spell('spawncat'))

        self.wellbutton.active = False
        self.hivebutton.active = False
        self.fertilisebutton.active = False
        self.planttreebutton.active = False
        self.goatbutton.active = False
        self.catbutton.active = False

        self.elements.append(self.boltbutton)
        self.elements.append(self.wellbutton)
        self.elements.append(self.hivebutton)
        self.elements.append(self.fertilisebutton)
        self.elements.append(self.planttreebutton)
        self.elements.append(self.goatbutton)
        self.elements.append(self.catbutton)

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

class ProgressDialog(Dialog):
    def __init__(self, x, y, w, h, screen, game, text):
        super().__init__(x, y, w, h, screen, game)

        textlabel = Button(20, 20, w-40, h-40, self.surf, None)
        textlabel.caption = text
        textlabel.font = pg.font.Font('freesansbold.ttf', 20)

        self.elements.append(textlabel)
        self.update()

class QuestsDialog(Dialog):
    def __init__(self, x, y, w, h, screen, game):
        super().__init__(x, y, w, h, screen, game)

        self.active_quests = {}
        self.complete_quests = {}

    def addquest(self, name, text):
        self.active_quests[name] = text
        self.updatelists()
        self.update()

    def completequest(self, name):
        if name in self.active_quests:
            self.complete_quests[name] = self.active_quests[name]
            self.active_quests.pop(name, None)
            self.updatelists()
            self.update()

    def updatelists(self):
        self.elements = []

        y = 20
        quest_font = pg.font.Font('freesansbold.ttf', 20)
        complete_color = (0, 0, 0)
        active_color = (255, 200, 25)

        for cq in self.complete_quests.values():
            textlabel = Button(20, y, self.w - 40, 25, self.surf, None)
            textlabel.caption = cq
            textlabel.font = quest_font
            textlabel.text_col = complete_color

            self.elements.append(textlabel)
            y = y + 35

        y = y + 10

        for aq in self.active_quests.values():
            textlabel = Button(20, y, self.w - 40, 25, self.surf, None)
            textlabel.caption = aq
            textlabel.font = quest_font
            textlabel.text_col = active_color

            self.elements.append(textlabel)
            y = y + 35





