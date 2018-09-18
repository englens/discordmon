from poke_data import *
import random, instances, discordmon
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

#Controls the entire battle.
#Output: The winner, the updated player classes (with updated pokemon)
#In discordmon.py, Make a battle object and then call play_battle()     
class Battle:
    def __init__(self, p1, p2, channel):
        self.p1 = p1 #member/user
        self.p2 = p2 #member/user
        #Public channel of match. will PM members for moves.
        self.channel = channel
        
        
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
        self.curr_party = []
        for poke in self.player.party:
            curr_party.append(BattleMon(poke))
        self.active_poke = 0
        self.remaining_pokemon = len(self.curr_party)
    
    #TOTALY NOT ROBOT
    def is_ai():
        return False
    
    def pm(self, message):
        a
    def get_input(self, client, valid_responses, question):
        await cilent.send_message(self.user, question)
        await client.wait_for_message(author=self.user, 
    #asks the user (thru pm) what they want to do.
    #Options: Move, Swap, (Item?)
    #You cant run-- what are you, a puss puss
    def get_move_decision(self, other_poke, client=None):
        
        
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
        
        