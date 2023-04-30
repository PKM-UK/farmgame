from imagecomponent import *
from controlcomponent import *


def comp(type, *comp_args):
    if type == 'HunterControlComponent':
        return HunterControlComponent(*comp_args)
    elif type == 'DrifterControlComponent':
        return DrifterControlComponent(*comp_args)
    elif type == 'GrazerControlComponent':
        return GrazerControlComponent(*comp_args)
    elif type == 'BumbleControlComponent':
        return BumbleControlComponent(*comp_args)
    elif type == 'PetControlComponent':
        return PetControlComponent(*comp_args)
    elif type == 'GoatImageComponent':
        return GoatImageComponent(*comp_args)
    elif type == 'BeeImageComponent':
        return BeeImageComponent(*comp_args)
    elif type == 'CatImageComponent':
        return CatImageComponent(*comp_args)
