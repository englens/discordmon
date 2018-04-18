import requests, json

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