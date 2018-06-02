import random, datetime, string
from pprint import pprint
from poke_data import *
version_id = 1
MISS_CHANCE = 1
BOX_SIZE = 25  #boxes will resize if this is reduced
SHINY_CHANCE = 441
XP_DIVISOR = 2
natures = ['hardy','lonely','brave','adamant','naughty','bold','docile','relaxed',
           'impish','lax','timid','hasty','serious','jolly','naive','modest',
           'mild','quiet','bashful','rash','calm','gentle','sassy','careful','quirky']
pic_file       = './data/pictures/male/'
pic_file_shiny = './data/pictures/maleshiny/'
pic_file_unown = './data/pictures/unown'
player_path    = '../players/'
unown_forms = list(string.ascii_lowercase)
unown_forms.append('exclamation')
unown_forms.append('question')
# make ! and ? more rare
unown_forms = unown_forms + list(string.ascii_lowercase) + list(string.ascii_lowercase)
class Pokemon:
    """An instance of a type of pokemon. In addition to
    the class stores data on its current attributes, moves, and owner.
    """
    def __init__(self, id, moves, ability, nature, happiness, name, is_shiny, level=1, xp=0, evs=[0,0,0,0,0,0], ivs=None, gender=None, item=None, form=None):
        self.id = id
        self.moves = moves
        self.ability = ability
        self.nature = nature
        self.happiness = happiness
        self.name = name
        self.level = level
        self.xp = xp
        self.evs = evs
        if ivs is None:
            self.ivs   = [random.randint(0,31) for a in range(6)]
        else:
            self.ivs = ivs
        self.is_shiny = is_shiny
        if gender==None:
            self.gender = 'Unset'
        else:
            self.gender = gender
        self.item = item
        self.form = form
        
    def get_pic(self):
        if int(self.id) == 201:
            if self.is_shiny:
                return pic_file_unown + '/shiny/' + str(self.form) +'.png'
            else:
                return pic_file_unown + '/default/' + str(self.form) +'.png'
                
            
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
        
    def get_base_xp(self):
        return int(get_poke(self.id)['base_experience'])
        
    def get_xp_next_level(self):
        return int(exp_for_level(self.level+1, get_poke_growth_type(self.id)) / XP_DIVISOR)
    
    def add_xp(self, deltaxp):
        deltaxp = int(deltaxp)
        self.xp += deltaxp
        while self.xp >= self.get_xp_next_level():
            diff = self.xp - self.get_xp_next_level()
            self.level += 1
            self.xp = diff
        print(self.name + ' gained ' + str(deltaxp) + ' xp. (' + str(self.xp) + '/' + str(self.get_xp_next_level()) + ')')
        
    def has_base_name(self):
        return get_poke_name(self.id) == self.name
    
    def find_new_moves(self, old_lvl):
        level_moves = get_levelup_moves(self.id)
        return [move[0] for move in level_moves if (move[2] > old_lvl and move[2] <= self.level)]
    
    def find_evo(self, trigger, loc, owner, item=None, tradewith=None):
        evos = get_poke_evos(self.id)
        if evos is None:
            return None
        for evo in evos:
            for det in evo['evolution_details']:
                valid = True
                #make sure this is the right time to evolve, and skip everything if so
                if det['trigger']['name'] != trigger:
                    print('wrong trigger: ' + det['trigger']['name'])
                    continue
                    
                #check every condition
                if det['gender'] != None:
                    if self.gender != det['gender']:
                        valid = False
                if det['held_item'] != None:
                    if det['held_item'] != self.item:
                        valid = False
                if det['item'] != None:
                    if det['trigger']['name'] == 'use-item':
                        if det['item']['name'] != item:
                            valid == False
                if det['known_move'] != None:
                    if det['known_move']['name'] not in self.moves:
                        valid = False
                if det['known_move_type'] != None:
                    if det['known_move_type']['name'] not in [get_move_type(move) for move in self.moves]:
                        valid = False
                if det['location'] != None:
                    if det['location'] != loc:
                        valid = False
                if det['min_affection'] != None:
                    pass#----------------------------------------
                if det['min_beauty'] != None:
                    #beauty evos are disabled.
                    valid = False
                if det['min_happiness'] != None:
                    if det['min_happiness'] > self.happiness:
                        valid = False
                if det['min_level'] != None:
                    if det['min_level'] > self.level:
                        valid = False
                if det['needs_overworld_rain'] != False:
                    pass #------------------------------------------
                if det['party_species'] != None:
                    if det['party_species'] not in [get_poke_species(p.id)['name'] for p in owner.party]:
                        valid = False
                if det['party_type'] != None:
                    if det['party_type'] not in [get_poke_types(p.id) for p in owner.party]:
                        valid = False
                if det['relative_physical_stats'] != None:
                    if self.get_att() > self.get_def():
                        rps = 1
                    elif self.get_att() < self.get_def():
                        rps = -1
                    else:
                        rps = 0
                    if det['relative_physical_stats'] != rps:
                        valid = False
                if det['time_of_day'] != '':
                    hour = datetime.datetime.now().hour
                    if hour < 5 or hour > 8:
                        tod = 'night'
                    else:
                        tod = 'day'
                    if det['time_of_day'] != tod:
                        valid = False
                if det['trade_species'] != None:
                    if det['trade_species']['name'] != tradewith_species:
                        valid = False
                if det['turn_upside_down'] != False:
                    valid = False #------------------------------
                if valid == True:
                    #found it!
                    spec = get_species(evo['species']['url'][42:-1])
                    if len(spec['varieties']) > 1:
                        if spec['forms_switchable']:
                            for v in spec['varieties']:
                                if v['is_default']:
                                    return v['pokemon']['url'][34:-1]
                        elif spec['name'] == 'wormadam':
                            pass #---------------------------------
                    return spec['varieties'][0]['pokemon']['url'][34:-1]
        return None
        
    def str_moves(self):
        output = ''
        if self.moves == []:
            return 'None!'
        for move in self.moves:
            output += move.title() + ', '
        return output[:-2]
    
    def approx_power(self):
        if self.moves == []:
            return 0
        #sum all the levels, giving leader double weight
        total = 0
        for move_name in self.moves:
            move = get_move(move_name)
            modifier = 1
            if move['damage_class']['name'] == 'physical':
                total += int((((2*self.level)/5 + 2) * move['power'] * self.get_att())/50 + 2) * modifier
            elif move['damage_class']['name'] == 'special':
                total += int((((2*self.level)/5 + 2) * move['power'] * self.get_sp_att())/50 + 2) * modifier
        return total
        
    def to_dict(self):
        return {'id':self.id, 'moves':self.moves, 
                'ability':self.ability, 'nature':self.nature, 'happiness':self.happiness,
                'name':self.name, 'level':self.level, 'xp':self.xp, 'evs':self.evs,
                'ivs':self.ivs, 'is_shiny':self.is_shiny, 'gender':self.gender, 'item':self.item,
                'form':self.form}
        
    #Basic overview of pokemon-- Name+Level
    def __str__(self):
        return str(self.name) + ', Lvl ' + str(self.level)

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
        if self.is_full():
            return False
        self.pokemon.append(poke)
        return True
    
    def is_full(self):
        return len(self.pokemon) >= BOX_SIZE
        
    def remove_poke(self, index):
        if index > len(self.pokemon):
            print('Error: Invalid Index.')
            return None
        return self.pokemon.pop(index)
    def __len__(self):
        return len(self.pokemon)
        
    def pop(self, index):
        return self.pokemon.pop(index)
        
    def __getitem__(self, key):
        return self.pokemon[key]
        
    def __setitem__(self, key, value):
        self.pokemon[key] = value
        
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
        
    def len_boxes(self):
        return len(boxes)
    
    def str_party(self):
        if self.party == []:
            return 'Party Empty!'
        
        output = '```-----'+self.name+'\'s Party-----'
        lines = []
        for index, poke in enumerate(self.party, 1):
            line = '\n'+ str(index) + ') ' + poke.name
            if poke.name != get_poke_name(poke.id):
                line += ' ('+get_poke_name(poke.id)+')'
                if poke.is_shiny == True:
                    line.append('*')
            lines.append(line)
        maximum = max([len(l) for l in lines])
        for index, line in enumerate(lines):
            line += ' ' * (maximum - len(line) + 1)
            output += line
            output += 'Lvl ' + str(self.party[index].level)
            output += ' (' + str(self.party[index].xp) + '/' + str(self.party[index].get_xp_next_level()) + ')'
        output += '\n-----------------------```'
        return output
    
    #function to judge the power of the party. this can easily improve
    def get_party_power(self):
        if self.party == []:
            return 0
        #sum all the levels, giving leader double weight
        total = 0
        for poke in self.party:
            total += poke.approx_power()
                
        return total
        
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
    
def read_boxdict(dic):
    name = dic['name']
    pokemon = [read_pokedict(poke) for poke in dic['pokemon']]
    return Box(name, pokemon)
    
def array_string_safe(array):
    output = '['
    for item in array:
        output += str(item) + '|'
    return output[:-1] + ']'
    
def read_pokedict(dic):
    id = dic['id']
    moves = dic['moves']
    ability = dic['ability']
    nature = dic['nature']
    name  = dic['name']
    level = dic['level']
    evs = dic['evs']
    ivs = dic['ivs']
    is_shiny = dic['is_shiny']
    gender = dic['gender']
    if gender == 'Unset':
        gender = get_rand_gender(id)
    try:
        xp = dic['xp']
    except Exception:
        xp = 0
    try:
        happiness = dic['happiness']
    except Exception:
        happiness = get_poke_base_happiness(id)
    try:
        form = dic['form']
    except Exception:
        if id == 201:
            form = 'a'
        else:
            form = None    
    try:
        item = dic['item']
    except Exception:
        item = None    
    return Pokemon(id, moves, ability, nature, happiness, name, is_shiny, level=level, xp=xp, evs=evs, ivs=ivs, gender=gender, item=item, form=form)

#return an instance of given pokemon at default level for the given area
def make_for_encounter(location_area_index):
    #the level of the pokemon is based off the area the pokemon was found in. 
    ids, level_range, chances = get_area_gen1_pokemon_data(location_area_index)
    ids.append((0))
    level_range.append([(0,0)])
    chances.append([MISS_CHANCE])
    id, level = encounter_chance_picker(ids, level_range, chances)
    if int(id) != 0 and int(id) <= 250:
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
        happiness = get_poke_base_happiness(id)
        name = get_poke_name(id)
        is_shiny = random.randint(1,SHINY_CHANCE) == 1
        gender = get_rand_gender(id)
        if int(id) == 201: #unown
            form = random.choice(unown_forms)
            print('form:' + form)
        else:
            form = None
            print('not unown')
        return Pokemon(id, moves, ability, nature, happiness, name, is_shiny, level=level, gender=gender, item=None, form=form)
    return None
    
    
def write_player(player):
    with open(player_path+str(player.id)+'.txt', 'w') as f:
        json.dump(player.to_dict(), f)
        
def exp_for_level(level, mode):
    if mode == 'slow':
        return int((5*level**3)/4)
    if mode == 'medium':
        return int(level**3)
    if mode == 'fast':
        return int((4*level**3)/5)
    if mode == 'medium-slow':
        return int((6*level**3)/5 - 15*level**2 + 100*level - 140)
    if mode == 'slow-then-very-fast':
        if level <= 50:
            return int((level**3*(100-level))/50)
        if level <= 68:
            return int((level**3*(150-level))/100)
        if level <= 98:
            return int((level**3*int((1911-10*level)/3))/500)
        return int((level**3*(160-level))/100)
    if mode == 'fast-then-very-slow':
        if level <= 15:
            return int(level**3*((int((n+1)/3)+24)/50))
        if level <= 36:
            return int(level**3*((level+14)/50))
        return int(level**3*((int(level/2)+32)/50))