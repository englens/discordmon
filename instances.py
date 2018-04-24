import poke_data, random
version_id = 1
class Pokemon:
    """An instance of a type of pokemon. In addition to
    the class stores data on its current attributes, moves, and owner.
    """
    def __init__(self, id, owner, moves, name=None, level=1):
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
        #move stuff
    return Pokemon(id, 'WILD', level)
    