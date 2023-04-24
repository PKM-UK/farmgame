from enum import Enum

class ItemTypes(Enum):
    grass = 1
    pie = 2
    poop = 3

class Item:
    def __init__(self, type, image_path):
        self.type = type
        self.image_path = image_path

item_types = {
    ItemTypes.grass: Item(ItemTypes.grass, 'grassItem.png'),
    ItemTypes.pie: Item(ItemTypes.pie, 'pieItem.png'),
    ItemTypes.poop: Item(ItemTypes.poop, 'poopItem.png')
}


