from poke_data import *
from pathlib import Path
import random, discord, asyncio, math, regex, instances
MAX_RETRYS = 20
NPC_PATH = Path('./data/npcs/')
#wrapper for Pokemon that also has temp data
class BattleMon:
    def __init__(self, poke):
        self.poke = poke
        self.pp = []
        for move in self.poke.moves:
            self.pp.append(get_move_pp(move))
        self.curr_pp = self.pp[:]
        self.curr_hp = self.poke.get_hp()
        self.new_xp = 0
        self.dead = False

#Controls the entire battle.
#Output: The winner, the updated player classes (with updated pokemon)
#In discordmon.py, Make a battle object and then call play_battle()     
class Battle:
    def __init__(self, p1, p2, client, fight_channel):
        self.p1 = p1 #BattlePlayer
        self.p2 = p2 #BattlePlayer/BattleAI
        #Public channel of match. will PM members for moves.
        self.weather = 'clear'
        self.client = client
        self.fight_channel = fight_channel
        
    async def broadcast(self, msg):
        await self.client.send_message(self.fight_channel, msg)
        
    async def display(self):
        p1_poke = self.p1.curr_party[self.p1.active_poke]
        p1_hp_bars = math.floor((p1_poke.curr_hp/p1_poke.poke.get_hp()) * 10) #TODO: FIX
        p1_bar_str = '#'*p1_hp_bars + '-'*(10-p1_hp_bars)
        p1_status = [] #TODO
        p1_status_str = ''
        for s in p1_status:
            p1_status_str += '['+s+']'
        p1_poke_ln = f'Lvl.{p1_poke.poke.level} {p1_poke.poke.name} {p1_status_str}'
        p2_poke = self.p2.curr_party[self.p2.active_poke]
        p2_hp_bars = math.floor((p2_poke.curr_hp/p2_poke.poke.get_hp()) * 10) #TODO: FIX
        p2_bar_str = '-'*(10-p1_hp_bars) + '#'*p1_hp_bars
        p2_status = []  #TODO
        p2_status_str = ''
        for s in p2_status:
            p2_status_str += '['+s+']'
        p2_poke_ln = f'Lvl.{p2_poke.poke.level} {p2_poke.poke.name} {p2_status_str}'
        maxlen = max(len(p2_poke_ln),len(p2_bar_str),len(p1_poke_ln),len(p1_bar_str)) + 10
        p1_bar_str = p1_bar_str + ' '*(maxlen-len(p1_bar_str))
        p1_poke_ln = p1_poke_ln + ' '*(maxlen-len(p1_poke_ln))
        p2_bar_str = ' '*(maxlen-len(p2_bar_str)) + p2_bar_str 
        p2_poke_ln = ' '*(maxlen-len(p2_poke_ln)) + p2_poke_ln 
        battle_string = '|-Battle'+ '-'*(maxlen-7)
        bottom_string = '-'*maxlen
        output  = '```\n'
        output += battle_string+ '|\n|' 
        output += p2_poke_ln+'|\n|' 
        output += p2_bar_str+'|\n|' 
        output += ' '*maxlen + '|\n|'
        output += ' '*(math.floor(maxlen/2)-1) + 'VS' +' '*(math.ceil(maxlen/2)-1) + '|\n|'
        output += p1_poke_ln+'|\n|' 
        output += p1_bar_str+'|\n|' 
        output += bottom_string+'|\n' 
        output += 'Please Select a move in your DMs!```'
        await self.broadcast(output)
        
    #plays and finishes the battle. returns winner and updated playerclasses
    async def play_battle(self):
        game_done = False
        while not game_done:
            await self.display()
            p1_move = await self.p1.get_move_decision(self.p2.curr_party[self.p2.active_poke], self.client)
            p2_move = await self.p2.get_move_decision(self.p1.curr_party[self.p1.active_poke], self.client)
            #could be Move string, "concede", or "swap_poke"
            ###Concede###
            if   p2_move[0] == 'concede' and p1_move[0] == 'concede':
                pass
                #Double Concede! match ends in a tie. (Gym challenger loses)
                return
            elif p1_move[0] == 'concede':
                #p1 concedes
                winner = self.p2
                loser = self.p1
                break
            elif p2_move[0] == 'concede':
                #p2 concedes
                winner = self.p1
                loser = self.p2
                break
            #At this point, we can be sure that no player is conceding    
            ###Swap###
            if p1_move[0] == 'swap':   #p1 always swaps first, it doesnt really matter anyway
                await self.swap_display(self.p1, self.p1.curr_party[p1_move[1]], self.p1.curr_party[self.p1.active_poke])
            if p2_move[0] == 'swap':
                await self.swap_display(self.p2, self.p2.curr_party[p2_move[1]], self.p2.curr_party[self.p2.active_poke])

            ###Attack###
            if p1_move[0] == 'attack' and p2_move[0] == 'attack':
                #both attack
                #TODO: use speed to determine first
                order_num = 4 #just for testing
            elif p1_move[0] == 'attack':
                #only p1 attack
                order_num = 1
            elif p2_move[0] == 'attack':
                #only p2 attack
                order_num = 2
            else:
                order_num = 0

            #With this loop, order_num has 5 cases.
            #0: neither attack
            #1: p1 attack only
            #2: p2 attack only
            #3: both att, p1 first
            #4: both att, p2 first
            #In this way, using a small loop we can cover all attacking patterns.
            await asyncio.sleep(2)
            if order_num == 0:
                await self.broadcast('...Nobody does anything! (?)')
            while order_num > 0:
                if order_num % 2 == 0:
                    #self.execute_move(self.p2, self.p1, p2_move[1])
                    output = await self.execute_move(self.p2, self.p1, 'test_move')
                    await self.broadcast('```'+output+'```')
                    order_num -= 3
                    game_done = await self.check_for_death(self.p1)
                    if game_done:
                        winner = self.p2
                        loser = self.p1
                else: #odd
                    #self.execute_move(self.p1, self.p2, p1_move[1])
                    output = await self.execute_move(self.p1, self.p2, 'test_move')
                    await self.broadcast('```'+output+'```')
                    order_num -= 1
                    game_done = await self.check_for_death(self.p2)
                    if game_done:
                        winner = self.p1
                        loser = self.p2
                await asyncio.sleep(1.5)
        await self.broadcast(f'{winner.get_name()} Wins!')
        if winner.is_ai():
            await self.broadcast(f'{winner.get_name()}: "' + winner.endquote+ '"')
        if loser.is_ai():
            await self.broadcast(f'{loser.get_name()}: "' + loser.lossquote + '"')
        ##TODO: Award any XP/prizes
        ##TODO: Level pokemon and save to file
    
    #Checks for poke death, calls swtiching routines
    #Returns: False if game continues, True if game over
    #This method actually kills the pokemon
    async def check_for_death(self, player):
        if player.curr_party[player.active_poke].curr_hp <= 0:
            old = player.curr_party[player.active_poke]
            old.dead = True
            await self.broadcast(f'{old.poke.name} faints!')
            still_livin = False
            for poke in player.curr_party:
                if not poke.dead:
                    still_livin = True
            if still_livin:
                await player.swap_poke_after_death()
                await self.swap_display(player, old, player.curr_party[player.active_poke])
            else:
                await self.broadcast(f'{player.get_name()} Has no remaining pokemon!')
                return True   #game is over
            return False   #game continues
        
    #displays the string to swap two pokemon, and shows their pictures?
    async def swap_display(self, player, old_poke, new_poke):
        output = '```'
        output += f'{player.get_name()} Swaps pokemon!\n'
        output += f'"{old_poke.poke.name} Come back!"\n'
        output += f'"Go! {new_poke.poke.name}!"```'
        await self.broadcast(output)
        #TODO: Display the poke's image
        
    #execute a given move string, and reduce pp.
    async def execute_move(self, acting_player, receiving_player, move):
        a_poke = acting_player.curr_party[acting_player.active_poke]
        r_poke = receiving_player.curr_party[receiving_player.active_poke]
        old_hp = r_poke.curr_hp
        output = f'{a_poke.poke.name} uses {move}!\n'
        #this is gonna be a doozy to implement.
        if move=='test_move':
            r_poke.curr_hp -= random.randrange(1, 30)
            output += f'{r_poke.poke.name} takes {old_hp - r_poke.curr_hp} damage!'
            return output
            
        move_data = get_move(move)
        #vanilla damage move 
        if 'Inflicts regular damage.' in [e['effect'] for e in move_data['effect_entries']]:
            #source: https://bulbapedia.bulbagarden.net/wiki/Damage
            modifier = 1
            #STAB
            if move_data['type']['name'] in get_poke_types(a_poke.poke.id):
                if a_poke.poke.ability == 'adaptability':
                    modifier *= 2
                else:
                    modifier *= 1.5
            #random factor
            modifier *= random.uniform(0.85, 1.00)
            #type effectiveness
            modifier *= get_type_modifier(move_data['type']['name'],get_poke_types(r_poke.poke.id))
            #burn phys damage reduction
            #TODO
            #other?
            dmg = ((((2*a_poke.poke.level)/5 + 2) * move_data['power'])/50 + 2) * modifier
            r_poke.curr_hp -= dmg
        else:
            output += 'Unfortunatly, the dev has not implemented this move yet.'
        return output
        
    def get_type_modifier(movetype, other_poke_types):
        pass #TODO
        
#wrapper for player that has BattleMon Party
#If one player is an ai, then that player must be p2
#At end of match, will check if p2 was ai and call their end code  
class BattlePlayer:
    def __init__(self, client, player, user):
        self.player = player
        self.user = user
        #curr party will stay the same size, but pokemon in it will die.
        self.curr_party = []
        for poke in self.player.party:
            self.curr_party.append(BattleMon(poke))
        self.active_poke = 0
        self.remaining_pokemon = len(self.curr_party)
        self.client = client
    #TOTALY NOT ROBOT
    def is_ai(self):
        return False
        
    def get_name(self):
        return self.player.name 
        
    async def pm(self, message):
        await client.send_message(self.user, message)
        
    async def get_input(self, client, valid_responses, question):
        done = False
        count = 0
        while not done:
            count += 0
            await client.send_message(self.user, question)
            #find the private channel
            p_channel = None
            for pc in client.private_channels:
                if self.user in pc.recipients:
                    p_channel = pc
                    break
            if p_channel is None:
                return
            response = await client.wait_for_message(author=self.user, channel=p_channel, timeout=60)
            if response is None:
                return None  #Let timeout run out
            response = response.content.lower()
            if response in valid_responses:
                await client.send_message(self.user, 'Good!')
                return response  #good!
            if count > MAX_RETRYS:
                return None  #Too many retrys
            await self.pm("Invalid Response.")
    
    async def swap_poke_after_death(self):
        await self.pm('please select a pokemon to put out.')
        response = await swap_menu(force=True)
        return old
    #sets a new poke as curr_poke, returns previous pokemon
    #set force to true if cancel is not an option
    async def swap_menu(self, force):
        done = False
        while not done:
            output = '```Select a pokemon to swap to:'
            #display current party pokemon (and if they're dead)
            for i, poke in enumerate(self.curr_party):
                if poke.dead:
                    output += f'\n{i+1} -- {poke.poke.name} (DEAD)'
                else:
                    output += f'\n{i+1} -- {poke.poke.name}'
            if not force:
                output += '\ncancel -- go back```'
                response = await self.get_input(client, ['1', '2', '3', '4', '5', '6', 'cancel'], output)
            else:
                response = await self.get_input(client, ['1', '2', '3', '4', '5', '6'], output)
            if response == 'cancel':
                return 'cancel'
            else: #1-6
                choice = int(response)-1
                if self.curr_party[choice].dead:
                    await self.pm('Selected Pokemon has fainted! Please select a valid Pokemon.')
                else:
                    old = self.active_poke
                    self.active_poke = choice
                    return old
                    
    #asks the user (thru pm) what they want to do.
    #Returns a list: first item is 'attack', 'swap', or 'concede'
    #   if attck, second is attack name
    #   if swap, second is last poke pos (curr is now selected)
    #You cant run-- what are you, a puss puss
    async def get_move_decision(self, other_poke, client):
        moves = self.curr_party[self.active_poke].poke.moves
        while True:
            question = 'please select a move.```'
            for i, m in enumerate(moves):
                question += f'\n{i+1}  -- [{m}]'
            question += '\nswitch  -- change pokemon\nconcede  -- surrender```'
            #Move input loop (until a correct move is picked)
            response = await self.get_input(client, ['1', '2', '3', '4', 'switch', 'concede'], question)
                #if player went 60 seconds without timeout, or too many err inputs, no moves
            if response is None:
                return ['skip'] 
                #This is if they didn't input a move.
                #Turn is skipped.
            if response   == '1':
                return ['attack', moves[0]]
            elif response == '2':
                return ['attack', moves[1]]
            elif response == '3':
                return ['attack', moves[2]]
            elif response == '4':
                return ['attack', moves[3]]
            elif response == 'switch':
                response = swap_menu(False)
                if response == 'cancel':
                    #nothing to do but let the player pick another option
                    pass 
                else: #response will be the old poke
                    return ['swap', response]
            elif response == 'concede':
                yn = await self.get_input(client, ['y','n','yes','no'], "Really surrender? (y/n)")
                if yn in ['y', 'yes']:
                    return ['concede']
                #else, go back to move choice
            else:
                await self.pm("Invalid response.")
            
#Looks like a player to the Battle (yay duck typing)
#Party must be defined by creator
#Has a set reward and endquote, Reward can be set to None
#for exhibitions
class BattleAI:
    def __init__(self, name, party, strategy, endquote, lossquote):
        self.name = name
        self.curr_party = []
        for p in party:
            self.curr_party.append(BattleMon(p))
        self.active_poke = 0
        self.strategy = strategy
        self.endquote = endquote
        self.lossquote = lossquote
        
    #AM ROBOT BEEP BOOP
    def is_ai(self):
        return True
        
    #this is different than the Battleplayer method
    def get_name(self):
        return self.name
    
    #based on the chosen strategy, choose a move
    async def get_move_decision(self, other_poke, client=None):
        if self.strategy=='RAND':
            moves = self.curr_party[self.active_poke].poke.moves
            response = random.choice(moves)
            return ['attack', response]
        
    async def swap_poke_after_death(self):
        while not self.curr_party[self.active_poke].dead:
            self.active_poke = random.choice(range(len(self.curr_party)))
            print(f'Swapped to: {self.active_poke}')
            #TODO: Fix infinite loop on last dead

#loads a json file describing an npc ai. 
#id is their name in lowercase, puct removed, spaces replaced with _, numbers after duplicates
def load_npc_file(ai_id):
    if ai_id not in [name.stem for name in NPC_PATH.iterdir()]:
        raise FileNotFoundError
        return
    with open( NPC_PATH / (ai_id + '.txt')) as f:
        data = json.load(f)
    name = data['name']
    winquote = data['winquote']
    lossquote = data['lossquote']
    bounty = data['bounty']
    ai_mode = data['ai_mode']
    party = [instances.read_pokedict(p) for p in data['party']]
    return BattleAI(name, party, ai_mode, winquote, lossquote)
    
async def ai_exhibition(client, message, ai_id):
    ai_id = regex.sub(r'[ \t]+$','', ai_id)
    ai_id = regex.sub(r'[^\w\s]','',ai_id)
    ai_id = regex.sub(r'[\s]','_',ai_id)
    ai_id = ai_id.lower()
    try:
        npc = load_npc_file(ai_id)
    except FileNotFoundError:
        await client.send_message(message.channel, f"Error. Tried to fight someone that doesn't exist\n(Tried: {ai_id}")
        return
    try:
        player = BattlePlayer(client, instances.read_playerfile(message.author.id), message.author)
    except Exception:
        await client.send_message(message.channel, 'Error...you dont exist?')
        return
    bat = Battle(player, npc, client, message.channel)
    await bat.play_battle()
    
    
    
    