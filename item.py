from enum import Enum

class ItemTypes(Enum):
    grass = 1
    pie = 2

class Item:
    def __init__(self, type, image_path):
        self.type = type
        self.image_path = image_path



