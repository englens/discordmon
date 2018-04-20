import requests, json
"""Various Scripts dealing with the pokeapi database
and local copies of the data."""

url = 'http://pokeapi.co/api/v2/'
pokemon_path = './data/pokemon_reference/'
#grab all a pokemon's data
def fetch_poke(name):
    return requests.get(url+'pokemon/'+str(name)).json()

def get_poke(id):
    with open(pokemon_path+str(id)+'.txt') as f:
        data = json.load(f)
    return data
    
def get_move_list(pokemon):
    return [move['move']['name'] for move in pokemon['moves']]

#grab api data for a particular move
def fetch_move(name):
    return requests.get(url+'move/'+str(name)).json()

def write_pokemon_reference(name):
    txt = fetch_poke(name)
    print('working on:' + txt['name'])
    with open(pokemon_path+str(name)+'.txt', 'w+') as f:
        f.write(json.dumps(txt))
        
def write_all_pokemon_reference():
    for i in xrange(1,151):
        write_pokemon(i)
        
def get_stats(id):
    poke = get_poke(id)
    return [stat['base_stat'] for stat in poke['stats']]
    
def get_name(id):
    poke = get_poke(id)
    return poke['name']
    
def fetch_location(id):
    return requests.get(url+'location/'+str(id)).json()
    
def fetch_kanto_locations():
    kanto = requests.get(url+'region/1/').json()
    return [requests.get(l['url']).json() for l in kanto['locations']]
    
def get_loc_areas(loc):
    return [requests.get(area['url']).json() for area in loc['areas']]
    
#get the ids of pokemon, with assosiated level ranges and chances
def get_area_gen1_pokemon_data(area):
    names = [a['pokemon']['name'] for a in area['pokemon_encounters']]
    ids = [a['pokemon']['url'][34:-1] for a in area['pokemon_encounters']]
    encounter_list = [a['version_details'][0]['encounter_details'] for a in area['pokemon_encounters']]
    #list of list of tuples: pokemon in the area, 
    encounter_data = [[(encounter_type['max_level'], encounter_type['min_level']) for encounter_type in poke_encounter] for poke_encounter in encounter_list]
    range_chances = [
    return zip(ids, level_ranges)
    
names, ranges = get_area_gen1_pokemon_data(get_loc_areas(fetch_kanto_locations()[0])[0])
