from poke_data import *
import random, instances, discordmon
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
    def __init__(self, p1, p2, client):
        self.p1 = p1 #member/user
        self.p2 = p2 #member/user
        #Public channel of match. will PM members for moves.
        self.client = client
        
        
    #plays and finishes the battle. returns winner and updated playerclasses
    def play_battle(self):
        game_done = False
        while not game_done:
            ##repeat untill poke death:
            p1_move = p1.get_move_decision(p2.party[p2.active_poke])
            
            p2_move = p2.get_move_decision(p1.party[p1.active_poke])
            ##calculate first move
            self.execute_move(p1_move)
            if p2.curr_party[p2.active_poke].curr_hp <= 0:
                pass 
            self.execute_move(p2_move) #reorder me!
            if p1.curr_party[p1.active_poke].curr_hp <= 0:
                pass #swap to next
            ##Attempt to swap pokemon
        ##Declare winner
        ##Display AI endquote
        ##Award any XP/prizes
        ##Level pokemon and save to file
        
    def execute_move(self, acting_player, move):
        pass
        
        
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
            curr_party.append(BattleMon(poke))
        self.active_poke = 0
        self.remaining_pokemon = len(self.curr_party)
    
    #TOTALY NOT ROBOT
    def is_ai():
        return False
    
    def pm(self, client, message):
        await client.send_message(self.user, message)
        
    def get_input(self, client, valid_responses, question):
        done = False
        count = 0
        while not done:
            count += 0
            await cilent.send_message(self.user, question)
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
            response = lower(response)
            if response in valid_responses:
                return response  #good!
            if count > MAX_RETRYS:
                return None  #Too many retrys
            self.pm(client, "Invalid Response.")
        
    #asks the user (thru pm) what they want to do.
    #Returns Move string, "concede", or "swap_poke"
    #Options: Move, Swap, (Item?)
    #You cant run-- what are you, a puss puss
    async def get_move_decision(self, other_poke, client):
        moves = self.curr_party[self.active_poke].poke.moves
        while True:
            question = 'please select a move.```'
            for i, m in enumerate(moves):
                question += f'\n{i+1}  -- [{m}]'
            question += '\nswitch  -- change pokemon\nconcede  -- surrender```'
            #Move input loop (until a correct move is picked)
            response = self.get_input(client, ['1', '2', '3', '4', 'switch', 'concede'], question)
                #if player went 60 seconds without timeout, or too many err inputs, no moves
            elif response is None:
                return None  
                #This is if they didn't input a move.
                #Turn is skipped.
            if response   == "1":
                return moves[0]
            elif response == "2":
                return moves[1]
            elif response == "3":
                return moves[2]
            elif response == '4':
                return moves[3]
            elif response == 'switch':
                output = 'Select a pokemon to swap to:```'
                for i, poke in enumerate(self.curr_party):
                    if poke.dead:
                        output += f'\n{i+1} -- {poke.poke.name}'
                    else:
                        output += f'\n{i+1} -- {poke.poke.name}'
                output += 'cancel -- go back```'
                    
                response = self.get_input(client, ['1', '2', '3', '4', '5', '6', 'cancel'], output)
                if response == 'cancel':
                    pass #nothing to do here. loop will continue.
                else: #1-6
                    choice = int(response)-1
                    if self.curr_party[choice].dead:
                        self.pm('Selected pokemon has Fainted!')
                    else:
                        self.active_poke = choice
                        return 'swap_poke'
            elif response == 'concede':
                yn = self.get_input(client, ['y','n','yes','no'], "Really surrender?")
                if yn in ['y', 'yes']:
                    return 'concede'
                #else, go back to move choice
            else:
                self.pm("Invalid response.")
            
    def swap_poke_after_death(self):
        self.remaining_pokemon -= 1;
        if self.remaining_pokemon <= 0:
            return None
            
#Looks like a player to the Battle (yay duck typing)
#Party must be defined by creator
#Has a set reward and endquote, Reward can be set to None
#for exhibitions
class BattleAI:
    def __init__(self, party, strategy):
        self.curr_party = party #should be battlemon
        self.active_poke = 0
        self.endquote = endquote
        self.bounty = bounty
        self.strategy = strategy
        
    #AM ROBOT BEEP BOOP
    def is_ai():
        return True
        
    def get_move_decision(self, other_poke, client=None):
        if strategy=='RAND':
            return random.choice(self.curr_party[self.active_poke].moves)
        pass
        
    def swap_poke_after_death(self):
        pass
        
        