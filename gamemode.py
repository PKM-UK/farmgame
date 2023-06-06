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
        self.unlocked_spells = ['well','goat','hive','sapling','compost','cat']

        self.game.dialogs['spells'].wellbutton.active = True
        self.game.dialogs['spells'].hivebutton.active = True
        self.game.dialogs['spells'].fertilisebutton.active = True
        self.game.dialogs['spells'].planttreebutton.active = True
        self.game.dialogs['spells'].goatbutton.active = True
        self.game.dialogs['spells'].catbutton.active = True

class Story(GameMode):
    def __init__(self, game):
        super().__init__(game)
        self.completed_quests = []

        self.progression_points = {
            'bolt': (lambda: True, None, self.tengrasstiles, lambda: self.completed('bolt')),
            'well': (self.tengrasstiles, lambda: self.unlocked('well'), self.welltile, lambda: self.completed('well')),
            'goat': (self.tenlonggrasstiles, lambda: self.unlocked('goat'), self.havegoat, lambda: self.completed('goat')),
            'hive': (self.tengrassitems, lambda: self.unlocked('hive'), self.hivetile, lambda: self.completed('hive')),
            'sapling': (self.poopitems, lambda: self.unlocked('sapling'), self.saplingtile, lambda: self.completed('sapling')),
            'compost': (self.poopitems, None, None, None),
            'cat': (self.garden, lambda: self.unlocked('cat'), self.havecat, lambda: self.completed('cat')),
        }

        # Starter quest
        self.game.dialogs['quests'].addquest('bolt', 'Dig some ground to let grass grow')

        # self.game.dialogs['progress'] = ProgressDialog(200, 200, 600, 100, self.game.screen, self.game, 'I should grow some plants...')
        self.game.show_dialog('menu')

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
            if spell not in self.completed_quests:
                if self.progression_points[spell][2] and self.progression_points[spell][2]():
                    self.completed_quests.append(spell)
                    if self.progression_points[spell][3]:
                        self.progression_points[spell][3]()

    def unlocked(self, spell):
        message = ''
        quest_name = ''
        quest_text = ''


        if spell == 'well':
            message = 'I can dig a well to water more ground at once'
            quest_name = 'well'
            quest_text = 'Dig a well to water more area'

            butt = self.game.dialogs['spells'].wellbutton
        elif spell == 'goat':
            message = 'This long grass could feed a goat, or make useful straw'
            quest_name = 'goat'
            quest_text = 'Summon a goat to trim the grass'

            butt = self.game.dialogs['spells'].goatbutton
        elif spell == 'hive':
            message = 'I can weave a beehive from this grass'
            quest_name = 'hive'
            quest_text = 'Build a hive to encourage pollinators'

            butt = self.game.dialogs['spells'].hivebutton
        elif spell == 'sapling':
            message = 'This manure will fertilise the ground enough for trees'
            quest_name = 'sapling'
            quest_text = 'Fertilise some ground and plant some trees'

            butt = self.game.dialogs['spells'].fertilisebutton
            self.game.dialogs['spells'].planttreebutton.active = True
        elif spell == 'cat':
            message = 'This place is looking great - all it needs is a cat!'
            quest_name = 'cat'
            quest_text = 'Summon a pet to complete the garden'

            butt = self.game.dialogs['spells'].catbutton

        print(message)

        self.game.dialogs['quests'].addquest(quest_name, quest_text)

        self.game.dialogs['progress'] = ProgressDialog(200, 200, 600, 100, self.game.screen, self.game, message)
        self.game.show_dialog('progress')
        butt.active = True

    def completed(self, spell):

        self.game.dialogs['quests'].completequest(spell)
        self.game.dialogs['progress'] = ProgressDialog(200, 200, 600, 100, self.game.screen, self.game, f'Quest completed: {spell}')
        self.game.show_dialog('progress')

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

    def poopitems(self):
        inv = self.game.player.inventory
        poopinv = inv[ItemTypes.poop] if ItemTypes.poop in inv else 0
        return poopinv > 1

    def garden(self):
        grasstiles = sum(1 for t in self.game.walls if t.terrain_type == TerrainTypes.longgrass)
        flowertiles = sum(1 for t in self.game.walls if t.terrain_type == TerrainTypes.flowers)
        treetiles = sum(1 for t in self.game.walls if t.terrain_type == TerrainTypes.tree)

        return grasstiles > 10 and flowertiles > 5 and treetiles > 5

    def welltile(self):
        for t in self.game.walls:
            if t.terrain_type == TerrainTypes.well:
                return True
        return False

    def hivetile(self):
        for t in self.game.walls:
            if t.terrain_type == TerrainTypes.hive:
                return True
        return False

    def saplingtile(self):
        treetiles = sum(1 for t in self.game.walls if t.terrain_type == TerrainTypes.tree)
        return treetiles > 5

    def havegoat(self):
        for m in self.game.mobs:
            if type(m.imageComponent).__name__ == 'GoatImageComponent':
                return True
        return False

    def havecat(self):
        for m in self.game.mobs:
            if type(m.imageComponent).__name__ == 'CatImageComponent':
                return True
        return False


