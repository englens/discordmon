import requests, json, random, os
"""Various Scripts dealing with the pokeapi database
and local copies of the data."""

url = 'http://pokeapi.co/api/v2/'
pokemon_path = './data/pokemon_reference/'
location_path = './data/locations/'
FISH_REDUCTION = 4 #divided by this number


#write specific pokemon to storage, stored as <id>.txt
def write_pokemon_reference(name):
    txt = fetch_poke(name)
    print('working on:' + txt['name'])
    with open(pokemon_path+str(name)+'.txt', 'w+') as f:
        f.write(json.dumps(txt))

#write every kanto pokemon to storage
def write_all_pokemon_reference():
    for i in range(1,151):
        write_pokemon(i)

#write a list of areas to files 
def write_areas(areas):
    for area in areas:
        write_area(area)

#write area data to file, must provide
def write_area(area):
    #location = area['location']['url'][35:-1]
    id = area['id']
    print('working on:' + str(area['name']))
    #filename = location_path+str(location)+'/'+str(id)+'.txt'
    filename = location_path+str(id)+'.txt'
    #create file if it doesn't exist. Found this script on StackExchange :-)
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    with open(filename, 'w+') as f:
        f.write(json.dumps(area))

#grab pokemon data from local storage, must use id
def get_poke(id):
    with open(pokemon_path+str(id)+'.txt') as f:
        data = json.load(f)
    return data
    
def  fetch_species(id):
    poke = get_poke(id)
    url = poke['species']['url']
    return requests.get(url).json()
    
def get_random_word():
    with open('./data/medium_words.txt', 'r') as f:
        words = [line.rstrip() for line in f]
    return random.choice(words).title()
def get_poke_abilites(id):
    poke = get_poke(id)
    return [ability['ability']['name'] for ability in poke['abilities'] if ability['is_hidden'] == False]
    
def get_area(id):
    with open(location_path+str(id)+'.txt') as f:
        data = json.load(f)
    return data

#returns names of all moves a pokemon can learn    
def get_move_list(pokemon):
    return [move['move']['name'] for move in pokemon['moves']]

#find all api stats for given poke id, from local storage        
def get_stats(id):
    poke = get_poke(id)
    return [stat['base_stat'] for stat in poke['stats']]

#find the name of given pokemon id, from local storage    
def get_poke_name(id):
    poke = get_poke(id)
    return poke['name']
    
def get_poke_kanto_moves(id):
    poke = get_poke(id)
    moves = poke['moves']
    kanto_moves = []
    for move in moves:
        for version in move['version_group_details']:
            if version['version_group']['name'] == 'firered-leafgreen':
                kanto_moves.append([move['move']['name'], version['move_learn_method']['name'], version['level_learned_at']])
    return kanto_moves
    
def get_egg_moves(id):
    moves = get_poke_kanto_moves(id)
    return [move for move in moves if move[1] == 'egg']
    
def get_levelup_moves(id):
    moves = get_poke_kanto_moves(id)
    return [move for move in moves if move[1] == 'level-up']
    
def get_machine_moves(id):
    moves = get_poke_kanto_moves(id)
    return [move for move in moves if move[1] == 'machine']

def get_tutor_moves(id):
    moves = get_poke_kanto_moves(id)  
    return [move for move in moves if move[1] == 'tutor']

#returns name of location area exists in
def get_area_loc_name(id):
    return get_area(id)['location']['name']

#get the ids of pokemon, with assosiated level ranges and chances
def get_area_gen1_pokemon_data(area_id):
    area = get_area(area_id)
    #ids = [a['pokemon']['url'][34:-1] for a in area['pokemon_encounters']]
    ids = []
    encounter_list = []
    for poke in area['pokemon_encounters']:
        for version in poke['version_details']:
            if version['version']['name'] == 'firered' or version['version']['name'] == 'leafgreen':
                #this is a valid poke. record this encounter and this poke, and check next poke
                encounter_list.append(version['encounter_details'])
                ids.append(poke['pokemon']['url'][34:-1])
                break;
            #if no version in version details is a gen1 remake, this pokemon is not valid and not added.
            #also, only the first valid version is added (thanks to the break)
    #encounter_list = [a['version_details'][0]['encounter_details'] for a in area['pokemon_encounters']]
    #list of list of tuples: pokemon in the area, 
    level_ranges = [[(encounter_type['min_level'], encounter_type['max_level']) for encounter_type in poke_encounter] for poke_encounter in encounter_list]
    range_chances = []
    for poke_encounter in encounter_list:
        types = []
        for type in poke_encounter:
            if type['method']['name'] not in ['old-rod', 'good-rod']:
                types.append(int(type['chance']))
        range_chances.append(types)
    #range_chances = [[encounter_type['chance'] for encounter_type in poke_encounter] for poke_encounter in encounter_list]
    return ids, level_ranges, range_chances

def fetch_picture(id):
    with open('./data/pictures/male/'+str(id)+'.png', 'wb+') as handle:
        response = requests.get('https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/'+str(id)+'.png', stream=True)
        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

#get all data about all areas in a location
def fetch_loc_areas(loc):
    return [requests.get(area['url']).json() for area in loc['areas']]

#grab api data for a particular move
def fetch_move(name):
    return requests.get(url+'move/'+str(name)).json()

#grab pokemon data from api, works with either name or id    
def fetch_poke(name):
    return requests.get(url+'pokemon/'+str(name)).json()

#grab location (route, cave, town, etc) from api    
def fetch_location(id):
    return requests.get(url+'location/'+str(id)).json()

#grab specific pokemon-spawning area from api
def fetch_area(id):
    return requests.get(url+'location-area/'+str(id)).json()

#return all kanto locations    
def fetch_kanto_locations():
    kanto = requests.get(url+'region/1/').json()
    return [requests.get(l['url']).json() for l in kanto['locations']]

#weighted random choice, returns index of choice
def choose_weighted(weights):
    total = sum(weights) - 1
    summed_weights = []
    running_total = 0
    #make a list of each weight+everything below it.
    for w in weights:
        running_total += w
        summed_weights.append(running_total)
    #choose a number between 0 and total
    choice = random.randint(0,total)
    for  i in range(len(weights)):
        if choice < summed_weights[i] and choice >= summed_weights[i]-weights[i]:
            return i
    print('error: choose_weighted fucked up')

#takes in list of poke  ids and encounter chances (from get_area_gen1_poke_data()), returns id and level, weighted correctly
def encounter_chance_picker(ids, level_ranges, encounter_chances):
    #find max chance for each poke
    sums = [sum(a) for a in encounter_chances]
    index = choose_weighted(sums)
    range = level_ranges[index][choose_weighted(encounter_chances[index])]
    level = random.randint(range[0], range[1])
    return ids[index], level
