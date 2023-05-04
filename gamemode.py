"""        self.spells = {'bolt': (self.magic_missile, 0.25),
                       'well': (self.dig_dirt, 2),
                       'hive': (self.build_hive, 3),
                       'compost': (self.fertilise, 1),
                       'sapling': (self.plant_tree, 2)}"""

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
            'well': (self.tengrasstiles, lambda a: self.unlocked('well')),
            'goat': (self.tenlonggrasstiles, lambda a: self.unlocked('goat')),
            'hive': (self.tengrassitems, lambda a: self.unlocked('hive')),
            'sapling': (self.tenpoopitems, lambda a: self.unlocked('sapling')),
            'compost': (self.tenpoopitems, None),
            'cat': (self.garden, lambda a: self.unlocked('cat'))
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
        elif spell == 'goat':
            message = 'This long grass is probably enough to feed a goat'
        elif spell == 'hive':
            message = 'I can weave a beehive from this grass, the flowers will like that'
        elif spell == 'sapling':
            message = 'This manure will fertilise the ground enough for trees'
        elif spell == 'cat':
            message = 'This place is looking great - all it needs is a cat!'

        print(message)

    def tengrasstiles(self):
        return False

    def tenlonggrasstiles(self):
        return False

    def tengrassitems(self):
        return False

    def tenpoopitems(self):
        return False

    def tenpoopitems(self):
        return False

    def garden(self):
        return False



