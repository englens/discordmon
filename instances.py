class Pokemon:
    """An instance of a type of pokemon. In addition to
    the class stores data on its current attributes, moves, and owner.
    """
    def __init__(self, id, owner, name=None, level=1):
        self.id = id
        self.owner = owner
        self.name = name
        self.level = level
        
    #return an instance of given pokemon at default stats and level for the given area
    def make_for_encounter(id, level):
        #the level of the pokemon is based off the area the pokemon was found in. 
        return Pokemon(id, 'WILD', level)