import poke_data, random
version_id = 1
class Pokemon:
    """An instance of a type of pokemon. In addition to
    the class stores data on its current attributes, moves, and owner.
    """
    def __init__(self, id, owner, moves, stats, name=None, level=1):
        self.id = id
        self.owner = owner
        self.name = name
        self.level = level
        self.moves = moves
        self.evs   = [0, 0, 0, 0, 0, 0]
        self.ivs   = [random.randint(0,31) for a in xrange(6)]
    def copy(self):
        pass
    #return an instance of given pokemon at default stats and level for the given area
def make_for_encounter(location_area_index):
    #the level of the pokemon is based off the area the pokemon was found in. 
    id, level = encounter_chance_picker(get_area_gen1_pokemon_data(location_area_index))
    level_moves = get_levelup_moves(id)
    starter_moves = [move for move in level_moves if int(move[2]) <= level]
    if len(starter_moves) <= 4:
        print(starter_moves)
        moves = [move[0] for move in starter_moves]
    else:
        #cut down to the 4 highest
    return Pokemon(id, 'WILD', level)
    