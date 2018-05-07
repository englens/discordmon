import random
from pprint import pprint
from poke_data import *
version_id = 1
MISS_CHANCE = 1
BOX_SIZE = 25  #boxes will resize if this is reduced
SHINY_CHANCE = 441
natures = ['hardy','lonely','brave','adamant','naughty','bold','docile','relaxed',
           'impish','lax','timid','hasty','serious','jolly','naive','modest',
           'mild','quiet','bashful','rash','calm','gentle','sassy','careful','quirky']
pic_file       = './data/pictures/male/'
pic_file_shiny = './data/pictures/maleshiny'
player_path    = './data/players/'

def exp_for_level(level):
    return int((5*level**3)/4) #slow

class Pokemon:
    """An instance of a type of pokemon. In addition to
    the class stores data on its current attributes, moves, and owner.
    """
    def __init__(self, id, owner, moves, ability, nature, name=None, level=1, evs=None, ivs=None, is_shiny=True, gender=None):
        self.id = id
        self.owner = owner
        
        self.name = name
        self.moves = moves
        self.ability = ability
        self.nature = nature
        if name is None:
            self.name = get_poke_name(id)
        else:
            self.name = name
        self.level = level
        if evs is None:
            self.evs   = [0, 0, 0, 0, 0, 0]
        else:
            self.evs = evs
        if ivs is None:
            self.ivs   = [random.randint(0,31) for a in range(6)]
        else:
            self.ivs = ivs
        if is_shiny == None:
            self.is_shiny = False
        else:
            self.is_shiny = is_shiny
        if gender==None:
            self.gender = 'Unset'
        else:
            self.gender = gender
    
    def get_pic(self):
        if self.is_shiny == True:
            return pic_file_shiny  + str(self.id)+'.png'
        else:
            return pic_file + str(self.id)+'.png'
            
    def get_base_stats(self):
        return get_stats(self.id)
        
    def get_speed(self):
        output = int(((2*self.get_base_stats()[0] + self.ivs[0] + int(self.evs[0]/4))*self.level)/100) + 5
        if self.nature in ['timid','hasty','jolly','naive']:
            return int(output * 1.1)
        if self.nature in ['sassy','quiet','relaxed','brave']:
            return int(output * 0.9)
        return output
        
    def get_sp_def(self):
        output = int(((2*self.get_base_stats()[1] + self.ivs[1] + int(self.evs[1]/4))*self.level)/100) + 5
        if self.nature in ['calm','gentle','careful','sassy']:
            return int(output * 1.1)
        if self.nature in ['naughty','lax','rash','naive']:
            return int(output * 0.9)
        return output
        
    def get_sp_att(self):
        output = int(((2*self.get_base_stats()[2] + self.ivs[2] + int(self.evs[2]/4))*self.level)/100) + 5
        if self.nature in ['modest','mild','rash','quiet']:
            return int(output * 1.1)
        if self.nature in ['adamant','impish','careful','jolly']:
            return int(output * 0.9)
        return output
        
    def get_def(self):
        output = int(((2*self.get_base_stats()[3] + self.ivs[3] + int(self.evs[3]/4))*self.level)/100) + 5
        if self.nature in ['bold','impish','lax','relaxed']:
            return int(output * 1.1)
        if self.nature in ['hasty','gentle','mild','lonely']:
            return int(output * 0.9)
        return output
        
    def get_att(self):
        output = int(((2*self.get_base_stats()[4] + self.ivs[4] + int(self.evs[4]/4))*self.level)/100) + 5
        if self.nature in ['lonely','brave','adamant','naughty']:
            return int(output * 1.1)
        if self.nature in ['bold','modest','calm','timid']:
            return int(output * 0.9)
        return output
        
    def get_hp(self):
        return int(((2*self.get_base_stats()[5] + self.ivs[5] + int(self.evs[5]/4))*self.level)/100) + self.level + 10
   
    def get_species(self):
        return get_poke_name(self.id)

    def str_moves(self):
        output = ''
        if self.moves == []:
            return 'None!'
        for move in self.moves:
            output += move.title() + ', '
        return output[:-2]

    def to_dict(self):
        return {'id':self.id,       'owner':self.owner,     'moves':self.moves, 
                'ability':self.ability, 'nature':self.nature, 'name':self.name, 
                'level':self.level, 'evs':self.evs, 'ivs':self.ivs, 
                'is_shiny':self.is_shiny, 'gender':self.gender}
        
    #Basic overview of pokemon-- Name+Level
    def __str__(self):
        return str(self.name) + ', Lvl ' + str(self.level)

#return an instance of given pokemon at default level for the given area
def make_for_encounter(location_area_index):
    #the level of the pokemon is based off the area the pokemon was found in. 
    ids, level_range, chances = get_area_gen1_pokemon_data(location_area_index)
    ids.append((0))
    level_range.append([(0,0)])
    chances.append([MISS_CHANCE])
    id, level = encounter_chance_picker(ids, level_range, chances)
    if id != 0:
        level_moves = get_levelup_moves(id)
        starter_moves = [move for move in level_moves if int(move[2]) <= level]
        minimum = 0
        while len(starter_moves) > 4:
            minimum = min([move[2] for move in starter_moves])
            starter_moves = [move for move in starter_moves if move[2] != minimum]
        moves = [move[0] for move in starter_moves]
        abilites = get_poke_abilites(id)
        if abilites == []:
            ability = None
        else:
            ability = random.choice(abilites)
        nature = random.choice(natures)
        
        is_shiny = random.randint(1,SHINY_CHANCE) == 1
        gender = 'Unset'
        return Pokemon(id, 'WILD', moves, ability, nature, level=level, is_shiny=is_shiny)
    return None

def read_pokedict(dic):
    id = dic['id']
    owner = dic['owner']
    moves = dic['moves']
    ability = dic['ability']
    nature = dic['nature']
    name  = dic['name']
    level = dic['level']
    evs = dic['evs']
    ivs = dic['ivs']
    is_shiny = dic['is_shiny']
    gender = dic['gender']
    return Pokemon(id, owner, moves, ability, nature, name=name, level=level, evs=evs, ivs=ivs, is_shiny=is_shiny, gender=gender)

class Box:
    """Box of pokemon. Contains Page name, and 25 pokemon slots.
    """
    def __init__(self, name, pokemon):
        if name == '0':
            self.name = get_random_word()
        else:
            self.name = name
        self.pokemon = pokemon
        
    def add_poke(self, poke):
        if len(self.pokemon) >= BOX_SIZE:
            return False
        self.pokemon.append(poke)
        return True
    
    def remove_poke(self, index):
        if index > len(self.pokemon):
            print('Error: Invalid Index.')
            return None
        return self.pokemon.pop(index)

    def __str__(self):
        output = '-----------------------'
        lines = []
        for index, poke in enumerate(self.pokemon, 1):
            line = '\n' + str(index) + ') ' + poke.name
            if poke.name != get_poke_name(poke.id):
                line += ' ('+get_poke_name(poke.id)+')'
                if poke.is_shiny == True:
                    line.append('*')
            lines.append(line)
        maximum = max([len(l) for l in lines])
        for index, line in enumerate(lines):
            line += ' ' * (maximum - len(line) + 1)
            output += line
            output += 'Lvl ' + str(self.pokemon[index].level)
        output += '\n-----------------------'
        return output
        
    #recursive
    def to_dict(self):
        return {'name':self.name, 'pokemon':[poke.to_dict() for poke in self.pokemon if poke is not None]}

def read_boxdict(dic):
    name = dic['name']
    pokemon = [read_pokedict(poke) for poke in dic['pokemon']]
    return Box(name, pokemon)
    
class Player: 
    """Representation of a player. Includes methods for saving and reading from files.
    """
    def __init__(self, id, name, boxes, party):
        self.id = id        #discord ID
        self.name = name
        self.boxes = boxes  #1D array of 'Box' objects
        self.party = party
        for box in self.boxes:
            while len(box.pokemon) > BOX_SIZE:
                poke = box.remove_poke(len(box.pokemon)-1)
                self.add_poke(poke)
          #1D array of max 6 pokemon
        
    def add_poke(self, poke):
        if len(self.boxes) == 0:
            #if first poke, make a new box
            self.boxes.append(Box(get_random_word(), [poke]))
        else:
            #look through all boxes and find a slot
            finished = False
            for box in self.boxes:
                finished = box.add_poke(poke)
                if finished:
                    break
            #if no slots, make a new box and add the poke
            if finished==False:
                self.boxes.append(Box(get_random_word(), [poke]))
        write_player(self)
        
    def len_boxes(self):
        return len(boxes)
    
    def __str__(self):
        return name
    
    #this is recursive
    def to_dict(self):
        return {'id':self.id, 'name':self.name, 'boxes':[box.to_dict() for box in self.boxes], 'party':[poke.to_dict() for poke in self.party]}     
    
def read_playerfile(id):
    with open(player_path+str(id)+'.txt', 'r') as f:
        data = json.load(f)
    id = data['id']
    name = data['name']
    boxes = [read_boxdict(box) for box in data['boxes']]
    party = [read_pokedict(poke) for poke in data['party']]
    return Player(id, name, boxes, party)
    
def array_string_safe(array):
    output = '['
    for item in array:
        output += str(item) + '|'
    return output[:-1] + ']'
    
def write_player(player):
    with open(player_path+str(player.id)+'.txt', 'w') as f:
        json.dump(player.to_dict(), f)