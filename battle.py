from poke_data import *
import random, discord, asyncio
MAX_RETRYS = 20

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
        self.p1 = p1 #member/user
        self.p2 = p2 #member/user
        #Public channel of match. will PM members for moves.
        self.client = client
        self.fight_channel = fight_channel
        
    async def broadcast(self, msg):
        await self.client.send_message(self.fight_channel, msg)
        
    #plays and finishes the battle. returns winner and updated playerclasses
    async def play_battle(self):
        game_done = False
        while not game_done:
            p1_move = await self.p1.get_move_decision(self.p2.curr_party[self.p2.active_poke], self.client)
            p2_move = await self.p2.get_move_decision(self.p1.curr_party[self.p1.active_poke], self.client)
            print(f'P1 Decision: {p1_move[0]}')
            print(f'P2 Decision: {p2_move[0]}')
            #could be Move string, "concede", or "swap_poke"
            ###Concede###
            if   p2_move[0] == 'concede' and p1_move == 'concede':
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
                await self.swap_display(self.p1, p1_move[1], self.p1.curr_party[self.p1.active_poke])
            if p2_move[0] == 'swap':
                await self.swap_display(self.p2, p2_move[1], self.p2.curr_party[self.p2.active_poke])

            ###Attack###
            if p1_move[0] == 'attack' and p2_move == 'attack':
                #both attack
                #TODO: use speed to determine first
                order_num == 4 #just for testing
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
            if order_num == 0:
                await self.broadcast('...Nobody does anything! (?)')
            while order_num > 0:
                if order_num % 2 == 0:
                    #self.execute_move(self.p2, self.p1, p2_move[1])
                    await self.execute_move(self.p2, self.p1, 'test_move')
                    order_num -= 3
                    game_done = await self.check_for_death(self.p1)
                    if game_done:
                        winner = self.p2
                        loser = self.p1
                else: #odd
                    #self.execute_move(self.p1, self.p2, p1_move[1])
                    await self.execute_move(self.p1, self.p2, 'test_move')
                    order_num -= 1
                    game_done = await self.check_for_death(self.p2)
                    if game_done:
                        winner = self.p1
                        loser = self.p2
        await self.broadcast(f'{winner.player.name} Wins!')
        if winner.is_ai():
            await self.broadcast(f'{winner.player.name}: "' + winner.endquote+ '"')
        if loser.is_ai():
            await self.broadcast(f'{loser.player.name}: "' + loser.lossquote + '"')
        ##TODO: Display AI losing endquote
        ##TODO: Award any XP/prizes
        ##TODO: Level pokemon and save to file
    
    #Checks for poke death, calls swtiching routines
    #Returns: False if game continues, True if game over
    async def check_for_death(self, player):
        if player.curr_party[player.active_poke].curr_hp <= 0:
            old = player.curr_party[player.active_poke]
            await self.broadcast(f'{old.poke.name} faints!')
            still_livin = False
            for poke in player.curr_party:
                if not poke.dead:
                    still_livin = True
            if still_livin:
                await player.swap_poke_after_death()
                await self.swap_display(player, old, player.curr_party[player.active_poke])
            else:
                await self.broadcast(f'{player.player.name} Has no remaining pokemon!')
                return True   #game is over
            return False   #game continues
        
    #says the string to swap two pokemon, and shows their pictures
    async def swap_display(self, player, old_poke, new_poke):
        await self.broadcast(f'{player.name()} Swaps pokemon!')
        await self.broadcast(f'"{old_poke.poke.name} Come back!"')
        await self.broadcast(f'"Go! {new_poke.poke.name}!"')
        #TODO: Display the poke's image
        
    #execute a given move string, and reduce pp.
    async def execute_move(self, acting_player, receiving_player, move):
        #this is gonna be a doozy to implement.
        #For now, just do 1-30 damage
        await self.broadcast(f'{acting_player.curr_party[acting_player.active_poke].poke.name} uses {move}!')
        if move=='test_move':
            receiving_player.curr_party[receiving_player.active_poke].curr_hp -= random.randrange(1, 30)
        
#wrapper for player that has BattleMon Party
#If one player is an ai, then that player must be p2
#At end of match, will check if p2 was ai and call their end code  
class BattlePlayer:
    def __init__(self, player, user):
        self.player = player
        self.user = user
        #curr party will stay the same size, but pokemon in it will die.
        self.curr_party = []
        for poke in self.player.party:
            self.curr_party.append(BattleMon(poke))
        self.active_poke = 0
        self.remaining_pokemon = len(self.curr_party)
    
    #TOTALY NOT ROBOT
    def is_ai():
        return False
        
    def name(self):
        return self.player.name 
        
    async def pm(self, client, message):
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
            self.pm(client, "Invalid Response.")
    
    async def swap_poke_after_death(self):
        pass #TODO: Dialog to send out a new pokemon
        #May make a general swapping dialog for reuse for the normal swap funct
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
                output = 'Select a pokemon to swap to:```'
                #display current party pokemon (and if they're dead)
                for i, poke in enumerate(self.curr_party):
                    if poke.dead:
                        output += f'\n{i+1} -- {poke.poke.name} (DEAD)'
                    else:
                        output += f'\n{i+1} -- {poke.poke.name}'
                output += 'cancel -- go back```'
                    
                response = await self.get_input(client, ['1', '2', '3', '4', '5', '6', 'cancel'], output)
                if response == 'cancel':
                    pass #nothing to do here. loop will continue.
                else: #1-6
                    choice = int(response)-1
                    if self.curr_party[choice].dead:
                        self.pm('Selected pokemon has Fainted!')
                    else:
                        old = self.active_poke
                        self.active_poke = choice
                        return ['swap', old]
            elif response == 'concede':
                yn = await self.get_input(client, ['y','n','yes','no'], "Really surrender?")
                if yn in ['y', 'yes']:
                    return ['concede']
                #else, go back to move choice
            else:
                self.pm("Invalid response.")
            
#Looks like a player to the Battle (yay duck typing)
#Party must be defined by creator
#Has a set reward and endquote, Reward can be set to None
#for exhibitions
class BattleAI:
    def __init__(self, name, party, strategy, endquote, lossquote):
        self.curr_party = []
        for p in party:
            self.curr_party.append(BattleMon(p))
        self.active_poke = 0
        self.strategy = strategy
        self.endquote = endquote
        self.lossquote = lossquote
        
    #AM ROBOT BEEP BOOP
    def is_ai():
        return True
    def name(self):
        return self.name
        
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
        