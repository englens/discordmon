import poke_data, random
from poke_data import *
version_id = 1
class Pokemon:
    """An instance of a type of pokemon. In addition to
    the class stores data on its current attributes, moves, and owner.
    """
    def __init__(self, id, owner, moves, stats, name=None, level=1):
        self.id = id
        self.owner = owner
        if name is None:
            name = get_poke_name(id)
        self.name = name
        self.moves = moves
        self.stats = stats
        self.level = level
        self.evs   = [0, 0, 0, 0, 0, 0]
        self.ivs   = [random.randint(0,31) for a in xrange(6)]

    def __str__(self):
        output =    'ID:    ' + str(self.id) +
                    '\nOwner: ' + str(self.owner) +
                    '\nName:  ' + str(self.name) +
                    '\nMoves: ' + str(self.moves) +
                    '\nLevel: ' + str(self.level) +
                    '\nEVs:   ' + str(self.evs) +
                    '\nIVs:   ' + str(self.ivs)
        return output
        
    #return an instance of given pokemon at default stats and level for the given area
def make_for_encounter(location_area_index):
    #the level of the pokemon is based off the area the pokemon was found in. 
    ids, level_range, chances = get_area_gen1_pokemon_data(location_area_index)
    id, level = encounter_chance_picker(ids, level_range, chances)
    level_moves = get_levelup_moves(id)
    starter_moves = [move for move in level_moves if int(move[2]) <= level]
    minimum = 0
    while len(starter_moves) > 4:
        minimum = min([move[2] for move in starter_moves])
        starter_moves = [move for move in starter_moves if move[2] != minimum]
    moves = [move[0] for move in starter_moves]
    stats = get_stats(id)
    return Pokemon(id, 'WILD', moves, stats, level=level)
    