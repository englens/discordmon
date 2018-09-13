from poke_data import *
from instances import Pokemon
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
        self.p1 = p1
        self.p2 = p2
        
    #plays and finishes the battle. returns winner and updated playerclasses
    def play_battle(self):
        
    
#wrapper for player that has BattleMon Party
#If one player is an ai, then that player must be p2
#At end of match, will check if p2 was ai and call their end code  
class BattlePlayer:
    def __init__(self, player):
        self.player = player
        self.curr_party = []
        for poke in self.player.party:
            curr_party.append(BattleMon(poke))
    
    
    #TOTALY NOT ROBOT
    def is_ai():
        return False
        
    #asks the user (thru pm) what they want to do.
    #Options: Move, Swap, (Item?)
    #You cant run-- what are you, a puss puss
    def get_move_decision(self, channel):
        pass
        
        
        
        
#Looks like a player to the Battle (yay duck typing)
#Party must be defined by creator
#Has a set reward and endquote, Reward can be set to None
#for exhibitions
class BattleAI:
    def __init__(self, party):
        self.party = party #should be battlemon
        self.endquote = endquote
        self.bounty = bounty
    
    #AM ROBOT BEEP BOOP
    def is_ai():
        return True
        
        
        
        