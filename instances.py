class Pokemon:
    """An instance of a type of pokemon. In addition to
    the class stores data on its current attributes, moves, and owner.
    """
    def __init__(self, id, owner, name, level=1):
        self.id = id
        self.owner = owner
        self.name = name
        self.level = level
    #return an instance of given pokemon at default stats and level 1
    
    def make_for_encounter(id):
        