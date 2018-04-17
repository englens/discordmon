import requests, json

url = 'http://pokeapi.co/api/v2/'
pokemon_path = './data/pokemon_reference/'
#grab all a pokemon's data
def fetch_poke(name):
    return requests.get(url+'pokemon/'+str(name)).json()

def get_move_list(pokemon):
    return [move['move']['name'] for move in pokemon['moves']]

#grab api data for a particular move
def fetch_move(name):
    return requests.get(url+'move/'+str(name)).json()

def write_pokemon(name):
    txt = fetch_poke(name)
    print('working on:' + txt['name'])
    with open(pokemon_path+str(name)+'.txt', 'w+') as f:
        f.write(json.dumps(txt))
        
        
def write_all_pokemon():
    for i in xrange(1,151):
        write_pokemon(i)
        
write_pokemon(151)