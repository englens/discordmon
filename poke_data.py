import requests

url = 'http://pokeapi.co/api/v2/'

#grab all a pokemon's data
def fetch_poke(name):
    return requests.get(url+'pokemon/'+str(name)).json()

def get_move_list(pokemon):
    return [move['move']['name'] for move in pokemon['moves']]

#grab api data for a particular move
def fetch_move(name):
    return requests.get(url+'move/'+str(name)).json()

