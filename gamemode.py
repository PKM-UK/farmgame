"""        self.spells = {'bolt': (self.magic_missile, 0.25),
                       'well': (self.dig_dirt, 2),
                       'hive': (self.build_hive, 3),
                       'compost': (self.fertilise, 1),
                       'sapling': (self.plant_tree, 2)}"""

from terrain import TerrainTypes
from item import ItemTypes
from dialog import ProgressDialog

class GameMode():
    def __init__(self, game):
        self.unlocked_spells = []
        self.progression_points = {}
        self.game = game

    def spell_unlocked(self, spell):
        # Default to creative mode
        return True

    def check_progression(self):
        pass

class Creative(GameMode):
    def __init__(self, game):
        super().__init__(game)

class Story(GameMode):
    def __init__(self, game):
        super().__init__(game)
        self.progression_points = {
            'well': (self.tengrasstiles, lambda: self.unlocked('well')),
            'goat': (self.tenlonggrasstiles, lambda: self.unlocked('goat')),
            'hive': (self.tengrassitems, lambda: self.unlocked('hive')),
            'sapling': (self.tenpoopitems, lambda: self.unlocked('sapling')),
            'compost': (self.tenpoopitems, None),
            'cat': (self.garden, lambda: self.unlocked('cat'))
        }

    def spell_unlocked(self, spell):
        return spell in self.unlocked_spells

    def check_progression(self):
        print('Checking progression')
        for spell in self.progression_points.keys():
            if spell not in self.unlocked_spells:
                if self.progression_points[spell][0] and self.progression_points[spell][0]():
                    self.unlocked_spells.append(spell)
                    if self.progression_points[spell][1]:
                        self.progression_points[spell][1]()

    def unlocked(self, spell):
        message = ''
        if spell == 'well':
            message = 'I can dig a well to water more ground at once'
            butt = self.game.dialogs['spells'].wellbutton
        elif spell == 'goat':
            message = 'This long grass is probably enough to feed a goat'
            butt = self.game.dialogs['spells'].goatbutton
        elif spell == 'hive':
            message = 'I can weave a beehive from this grass, the flowers will like that'
            butt = self.game.dialogs['spells'].hivebutton
        elif spell == 'sapling':
            message = 'This manure will fertilise the ground enough for trees'
            butt = self.game.dialogs['spells'].fertilisebutton
            self.game.dialogs['spells'].planttreebutton.active = True
        elif spell == 'cat':
            message = 'This place is looking great - all it needs is a cat!'
            butt = self.game.dialogs['spells'].catbutton

        print(message)
        self.game.dialogs['progress'] = ProgressDialog(200, 200, 600, 100, self.game.screen, self.game, message)
        self.game.show_dialog('progress')
        butt.active = True

    def tengrasstiles(self):
        grasstiles = sum(1 for t in self.game.walls if t.terrain_type == TerrainTypes.shortgrass)
        print(f"{grasstiles} grass tiles")
        return grasstiles > 3

    def tenlonggrasstiles(self):
        grasstiles = sum(1 for t in self.game.walls if t.terrain_type == TerrainTypes.longgrass)
        return grasstiles > 9

    def tengrassitems(self):
        inv = self.game.player.inventory
        grassinv = inv[ItemTypes.grass] if ItemTypes.grass in inv else 0
        return grassinv > 10

    def tenpoopitems(self):
        inv = self.game.player.inventory
        poopinv = inv[ItemTypes.poop] if ItemTypes.poop in inv else 0
        return poopinv > 10

    def garden(self):
        grasstiles = sum(1 for t in self.game.walls if t.terrain_type == TerrainTypes.longgrass)
        flowertiles = sum(1 for t in self.game.walls if t.terrain_type == TerrainTypes.flowers)
        treetiles = sum(1 for t in self.game.walls if t.terrain_type == TerrainTypes.tree)

        return grasstiles > 10 and flowertiles > 5 and treetiles > 5



