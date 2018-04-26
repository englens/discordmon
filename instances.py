import poke_data, random
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

    def display(self):
        print('ID:    ' + str(self.id))
        print('Owner: ' + str(self.owner))
        print('Name:  ' + str(self.name))
        print('Moves: ' + str(self.moves))
        print('
        
    #return an instance of given pokemon at default stats and level for the given area
def make_for_encounter(location_area_index):
    #the level of the pokemon is based off the area the pokemon was found in. 
    id, level = encounter_chance_picker(get_area_gen1_pokemon_data(location_area_index))
    level_moves = get_levelup_moves(id)
    starter_moves = [move for move in level_moves if int(move[2]) <= level]
    while len(starter_moves) > 4:
        min = min([move[2] for move in starter_moves])
        starter_moves = [move for move in starter_moves if move[2] != min]
    moves = [move[0] for move in starter_moves]
    stats = get_stats(id)
    return Pokemon(id, 'WILD', moves, level, stats, level=level)
    