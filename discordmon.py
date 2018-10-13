import discord, os, instances, json, asyncio, traceback, pprint, regex
import math, random, time, datetime
import battle
from poke_data import *
from pathlib import Path
cooldown = 3600 #seconds, == 1 hour
exits = ['exit', 'e x i t', 'c', 'cancel', 'exiT', '"exit"', ';exit', ';cancel', 'close', 'exit\\']
client = discord.Client()
prefix = ';'

PLAYER_PATH    = Path('../players/')
TIMESTAMP_FILE = Path('./data/timestamps.txt')
CURRLOC_FILE = Path('./data/currloc.txt')
LOC_PATH = Path('./data/locations/')
locations = [Path(name).stem for name in LOC_PATH.iterdir()]
try:
    players = [Path(name).stem for name in os.listdir(PLAYER_PATH)]
except FileNotFoundError:
    with open(PLAYER_PATH / 'dummy.txt', 'w+') as f:
        f.write('[]')
KEY_PATH = Path('../key.txt')
PC_TIMEOUT = 60
HOURS_LOC_DELAY = 4
WILD_FIGHT_TIME = 3 #seconds

players_in_session = []

@client.event
async def on_ready():
    print('Online.')

#handles incoming commands, and sends them to the relevant function
@client.event
async def on_message(message):
    if message.author != client.user and message.author.id not in players_in_session:
        players_in_session.append(message.author.id)
        if message.content.startswith(';'):
            cmd = message.content[1:].lower()
            try:
                if   cmd in ['encounter', 'e', 'wild', 'w']:
                    await encounter_poke(message)
                elif cmd == 'join':
                    await join_member(message)
                elif cmd == 'pc':
                    await show_boxes(message)
                elif cmd.startswith('pc '):  #quick pc to show specific box
                    await pc_wrapper(message)
                elif cmd.startswith('details ') or cmd.startswith('d '):
                    await quick_details(message)
                elif cmd == 'give me points':
                    await client.send_message(message.channel, 'no')
                elif cmd == 'help':
                    pass
                elif cmd in ['location', 'loc']:
                    await show_loc(message)
                elif cmd == 'party':
                    await show_party(message)
                elif cmd.startswith('pdetails '):
                    await party_details(message)
                elif cmd == 'testfight':
                    await test_fight(message)
                elif cmd.startswith('fight'):
                    await npc_test(message)
            except KeyboardInterrupt as k:
                raise k
            except Exception as e:
                #we catch this so it doesn't hang that user's session on error,
                #but we still want to see what went wrong so:
                print(traceback.format_exc())
        players_in_session.remove(message.author.id)  
    return

#Command to attempt to find a wild poke. Will send to catch_poke or
#fight_wild depending on player choice
#Params: NONE
async def encounter_poke(message):
    #check if current user is a player
    if not await is_player(message):
        return
    player = instances.read_playerfile(message.author.id)
    #check if the correct amount of time has passed
    with open(TIMESTAMP_FILE, 'r') as f:
        time_data = json.load(f)
    if player.id in time_data:
        last_time = time_data[player.id]
        diff = int(time.time()) - last_time
        if diff < cooldown:
            remain = cooldown-diff
            if remain > 40:
                remain = await seconds_to_minutes(remain)
                await client.send_message(message.channel, 'Please wait ' + str(remain) + ' minute(s) before finding another!')
            else:
                await client.send_message(message.channel, 'Please wait ' + str(remain) + ' seconds(s) before finding another!')
            return
    #-------END OF CHECKS-------        
    #set up pokemon. Keeps trying if none found, and if location contains none,
    #keep going to new locations until a poke is found.
    poke = None
    tries = 5
    while poke == None:
        while poke == None and tries >= 0:
            poke = instances.make_for_encounter(await get_location())
            print(poke)
            tries -= 1
            
        if poke == None:
            poke = instances.make_for_encounter(await get_location(force=True))
            
    output = 'A wild ' + str(poke.name).title() + ' Appears!'
    output += '\nLevel:    ' + str(poke.level)
    await client.send_message(message.channel, output)
    await send_pic(message, poke)
    output =  '----------------'
    
    #check if the player even has a party.
    #if no party, always catch pokemon and never fight

    if  player.party == []:
        await client.send_message(message.channel, output)
        await catch_poke(message, player, poke)
        done = True
    else:
        done = False
    while not done:
        output += '\nCatch or Fight? (c/f)'
        await client.send_message(message.channel, output)
        response = await client.wait_for_message(author=message.author, channel=message.channel)
        try:
            response = response.content.lower()
        except Exception: #the response is in a fucky wucky format
            output = 'Invalid Response.\n'
        else:
            if response == 'c':
                done = True
                await catch_poke(message, player, poke)
            elif response == 'f':
                done = True
                await fight_wild(message, player, poke)
            else:
                output = 'Invalid Response.'
    #player should have encountered a poke to get here
    #update the players timeout, they will have to wait through the timeout again after
    with open(TIMESTAMP_FILE, 'r') as f:
        time_data = json.load(f)
    time_data[player.id] = int(time.time())
    with open(TIMESTAMP_FILE, 'w') as f:
        json.dump(time_data, f)
    instances.write_player(player)

    
#Add a poke to the players inventory
async def catch_poke(message, player, poke):
    output = 'You caught ' + str(poke.name) + '!'
    done = False
    while not done:
        choice = await yes_or_no(message, 'Give it a name?', can_cancel=False)
        if choice == 'y':
            name_valid = False
            while not name_valid:
                await client.send_message(message.channel, 'Please enter name for your ' + poke.name + '.')
                response = await client.wait_for_message(author=message.author, channel=message.channel)
                response = response.content.replace(',', '')
                response = response.replace('"', '')
                if len(response) > 42:
                    await client.send_message(message.channel, 'Name too long, please pick a shorter one.')
                else:
                    name_valid = True
            poke.name = response
            done = True
        elif choice == 'n':
            done = True
        else:
            await client.send_message(message.channel, 'Invalid Response.')
        player.add_poke(poke)
    await client.send_message(message.channel, poke.name + ' added!')
 
#Attempt to fight the wild poke for xp. Uses a simplified fighting model. 
async def fight_wild(message, player, poke):
    player_power = player.get_party_power()
    diff = player_power - poke.approx_power()
    await client.send_message(message.channel, 'Simulating Battle...')
    await asyncio.sleep(WILD_FIGHT_TIME) #wait for dramatic tension
    if diff > 1:
        output = poke.name.title() + ' Defeated!'
        await client.send_message(message.channel, output)
        xp = wild_poke.get_base_xp() * wild_poke.level
        #distibute the wild pokemon's xp amung the party
        await distribute_xp(message, player, xp)
        #Now that pokemon have leveled, check if any evo's are valid by level up
        await check_apply_evo(message, player, trigger='level-up', item=None, tradewith=None)
    else:
        await client.send_message(message.channel, 'You lost the battle...')

#Distributes xp amung a players party, and displays appropirate level messages
#TODO: Seperate message code from here (put in add xp code, then return message).
async def distribute_xp(message, player, xp):
    if player.party == []:
        return
    output = ''
    await client.send_message(message.channel, str(xp) + ' XP Gained!')
    #Level pokemon 1:
    og_level = player.party[0].level
    if len(player.party) == 1:
        player.party[0].add_xp(xp)
    else:
        player.party[0].add_xp(int(xp/2))
        xp = int(xp/2)
    if og_level != player.party[0].level:
        if player.party[0].level - og_level == 1:
            msg = player.party[0].name + ' leveled up!'
            msg += '\nThey are now level ' + str(player.party[0].level) + '!'
            await client.send_message(message.channel, msg)
        else:
            msg = player.party[0].name + ' Gained ('+str(player.party[0].level - og_level)+') levels!'
            msg += '\nThey are now level ' + str(player.party[0].level) + '!'
            await client.send_message(message.channel, msg)
        await learn_new_moves(message, player.party[0], player.party[0].find_new_moves(og_level))
    if len(player.party) > 1:
        for poke in player.party[1:]:
            og_level = poke.level
            poke.add_xp(int(xp/len(player.party[1:])))
            if og_level != poke.level:
                if poke.level - og_level == 1:
                    msg = poke.name + ' leveled up!'
                    msg += '\nThey are now level ' + str(poke.level) + '!'
                    await client.send_message(message.channel, msg)
                else:
                    msg = poke.name + ' Gained ('+str(poke.level - og_level)+') levels!'
                    msg += '\nThey are now level ' + str(poke.level) + '!'
                    await client.send_message(message.channel, msg)
                await learn_new_moves(message, poke, poke.find_new_moves(og_level))

#Checks for any new moves to learn (post leveling)
#Will play the animation, and give the player the ability to cancel                
async def learn_new_moves(message, poke, moves):
    for move in moves:
        if len(poke.moves) < 4:
            poke.moves.append(move)
            client.send_message(message.channel, poke.name + ' learned ' + move)
        else:
            done = False
            while not done:
                output = poke.name + ' wants to learn <' + move + '> but '+ poke.name
                output += ' already knows 4 moves! Should a move be forgotten to make space for <' + move + '>?'
                response = await yes_or_no(message, output)
                if response == 'y':
                    output = poke.name + '\'s moves:'
                    for index, m in enumerate(poke.moves):
                        output += '\n' + str(index+1) + ') ' + m
                    output += '\nWhat move will be replaced with <' + move + '>?'
                    output += '\nsay the index of the move to delete, or "cancel" to cancel.'
                    await client.send_message(message.channel, output)
                    done2 = False
                    while not done2:
                        response2 = await client.wait_for_message(author=message.author, channel=message.channel)
                        response2 = response2.content.lower()
                        if response2 == 'cancel':
                            break
                        try:
                            index = int(response2)-1
                        except Exception:
                            await client.send_message(message.channel, 'Invalid Response.')
                        else:
                            if index > 5:
                                await client.send_message(message.channel, 'Index out of bounds.')
                            else:
                                
                                output = '1, 2 and... Poof! ' + poke.name + ' forgot <'+ poke.moves[index] + '>'
                                output += '\nand... ' + poke.name + ' learned <' + move + '>!'
                                poke.moves[index] = move
                                await client.send_message(message.channel, output)
                                done = True
                                done2 = True
                elif response == 'n':
                    response2 = await yes_or_no(message, 'Stop learning <' + move +'>?')
                    if response2 == 'y':
                        await client.send_message(message.channel, poke.name + ' did not learn <' + move + '>.')
                        done = True
                elif response == 'o':
                    await client.send_message(message.channel, 'Error, Invalid Response.')

#Adds a new member to the system, asking for basic identity info                
async def join_member(message):
    if message.author.id in players:
        await client.send_message(message.channel, 'You already joined!')
        return
    await client.send_message(message.channel, 'Welcome to pokemon! what is your name?')
    done = False
    while done == False:
        response = await client.wait_for_message(author=message.author, channel=message.channel)
        choice = await yes_or_no(message, 'Are you sure you want to be named "' + response.content + '"?')
        if choice == 'y':
            player = instances.Player(message.author.id, response.content, [], [])
            instances.write_player(player)
            await client.send_message(message.channel, 'Registration successful. type ";catch" to catch your first pokemon!')
            done = True
        elif choice == 'n':
            await client.send_message(message.channel, 'Please enter the correct name:')
        elif choice == 'c':
            done = True
            await client.send_message(message.channel, 'Registration canceled.')
        else:
            await client.send_message(message.channel, 'Invalid response.')

#Wrapper command for the pc, accepting command line boot commands
#(Such as starting on a specifc page)
#Params: BootPc_Index
async def pc_wrapper(message):
    try:
        num = int(message.content.lower()[3:])
    except Exception:
        await client.send_message(message.channel, 'Invalid Index.')
    else:
        await show_boxes(message, curr_box=num-1)

#Command to boot up pc.
#Params: NONE
#The pc allows players to access they're full inventory of pokemon.
#Each page of pc has a set size, and allows players to do various actions.
#Can have infinite pages
async def show_boxes(message, curr_box=0):
    if not await is_player(message):
        return
    await client.send_message(message.channel, 'Booting PC...')
    player = instances.read_playerfile(message.author.id)
    if player.boxes == []:
        await client.send_message(message.channel, 'You have no boxes! catch some pokemon first!')
        return
    if curr_box >= len(player.boxes):
        await client.send_message(message.channel, 'Box index out of range. Opening Box 1.')
        curr_box = 0
    done = False
    disp_pc = True
    disp_party = True
    disp_cmds = True
    fails = 0
    while not done:
        #Pc list:
        if disp_pc:
            output = '```---- ' + player.name +'\'s PC ----'
            output +=  '\nBox ' + player.boxes[curr_box].name
            output += ' (' + str(curr_box+1) + '/' + str(len(player.boxes)) + '):\n'
            output += str(player.boxes[curr_box])
            output += '```'
            await client.send_message(message.channel, output)
            disp_pc = False
        if disp_party:
            await client.send_message(message.channel, player.str_party())
            disp_party = False
        if disp_cmds:
            #Commands:
            output = '```\nCommands:'
            output += '\n"help" --- Show this command list'
            output += '\n"show" --- Reshow the pc'
            output += '\n"details <index>" --- Show more details on specified pokemon'
            output += '\n"party" --- Show current party'
            output += '\n"take <index> <partyindex>" --- Add box pokemon at given index to party, swapping with the existing pokemon.'
            output += '\n"deposit <partyindex>" --- deposit a pokemon into the box.'
            if curr_box < len(player.boxes)-1:
                output += '\n">" -- next box'
            if curr_box > 0:
                output += '\n"<" -- previous box'
            output +=  '\n"exit" or "c" -- close pc'
            output += '```'
            await client.send_message(message.channel, output)
            disp_cmds = False
        response = await client.wait_for_message(author=message.author, channel=message.channel, timeout=PC_TIMEOUT)
        if response != None:
            response = response.content.lower()
            if response == None:
                done = True
            elif response == '>' and curr_box < len(player.boxes)-1:
                curr_box += 1
                disp_pc = True
            elif response == '<' and curr_box > 0:
                curr_box -= 1
                disp_pc = True
            elif response in exits:
                done = True
            elif response == 'help':
                show_cmds = True
            elif response == 'details':
                disp_pc = True
            elif response == 'party':
                disp_party = True
            elif response.startswith('details '):
                num = None
                try:
                    num = int(response[8:])
                except Exception:
                    await client.send_message(message.channel, 'Invalid Index/Format.')
                else:
                    try:
                        await show_poke_details(message, player.boxes[curr_box].pokemon[num-1])
                    except Exception:
                        await client.send_message(message.channel, 'Invalid Index/Format.')
            elif response.startswith('*'):
                num = None
                try:
                    num = int(response[1:])
                except Exception:
                    await client.send_message(message.channel, 'Invalid Index/Format.')
                else:
                    try:
                        await show_poke_details(message, player.boxes[curr_box].pokemon[num-1])
                    except Exception:
                        await client.send_message(message.channel, 'Invalid Index/Format.')
            elif response.startswith('take '):
                try:
                    params = response.split()
                    if len(params) == 2:
                        pc_index = int(params[1])-1
                        party_index = len(player.party)
                    elif len(params) == 3:
                        pc_index = int(params[1])-1
                        party_index = int(params[2])-1
                    else:
                        raise Exception
                    
                except Exception as e:
                    print(e)
                    await client.send_message(message.channel, 'Invalid Index/Format.')
                else:
                    if pc_index > len(player.boxes[curr_box])-1 or party_index > 5:
                        await client.send_message(message.channel, 'Index too large!')
                    else:
                        if party_index > len(player.party)-1:
                            player.party.append(player.boxes[curr_box].pop(pc_index))
                        else:
                            temp = player.party[party_index]
                            player.party[party_index] = player.boxes[curr_box][pc_index]
                            player.boxes[curr_box][pc_index] = temp
                        disp_party = True
            elif response.startswith('deposit '):
                try:
                    params = response.split()
                    party_index = int(params[1])-1
                except Exception as e:
                    print(e)
                    await client.send_message(message.channel, 'Invalid Index/Format.')
                else:
                    if party_index > len(player.party)-1:
                        await client.send_message(message.channel, 'Party index out of range!')
                    else:
                        if player.boxes[curr_box].is_full():
                            curr_box += 1
                        player.add_poke(player.party.pop(party_index))
                        disp_party = True
            else:
                fails += 1
                if fails == 3:
                    done = True
            
        else:
            done = True
    await client.send_message(message.channel, player.name + '\'s PC closed.')
    instances.write_player(player)

#Shows all the realevant data for a specific pokemon.
#Some data is intentionally hidden: ivs, evs mainly.
async def show_poke_details(message, poke):
    await client.send_message(message.channel, '```Details for ' + poke.name + ':```')
    await send_pic(message, poke)
    output =  '\n```Lvl ' + str(poke.level) + ' ' + poke.get_species() + ' <' + poke.gender.title() + '>'
    output += '\n('+ str(poke.xp) + '/' + str(poke.get_xp_next_level()) + ')'
    output += '\n[' + poke.nature.title() + ']'
    output += '\nMoves:   ' + poke.str_moves()
    output += '\nAbility: ' + str(poke.ability).title()
    output += '\n--Stats--'
    output += '\nHP:         ' + str(poke.get_hp())
    output += '\nAttack:     ' + str(poke.get_att())
    output += '\nS. Attack:  ' + str(poke.get_sp_att())
    output += '\nDefense:    ' + str(poke.get_def())
    output += '\nS. Defense: ' + str(poke.get_sp_def())
    output += '\nSpeed:      ' + str(poke.get_speed())
    output += '\n--------------```'
    await client.send_message(message.channel, output)

#Command to show details of a box pokemon without opening the pc.
#Params: Box_number, Pokemon_box_index
async def quick_details(message):
    params =  message.content.split()
    try:
        box = int(params[1])
        index = int(params[2])
    except Exception:
        try:
            if params[1] == '-1':
                #return the latest poke
                box = 0
                index = 0
            else:
                raise IndexError
        except:
            await client.send_message(message.channel, 'Invalid Format.')
            return
    if not await is_player(message):
        return
    await client.send_message(message.channel, 'Accessing PC...')
    player = instances.read_playerfile(message.author.id)
    try:
        await show_poke_details(message, player.boxes[box-1].pokemon[index-1])
        await client.send_message(message.channel, 'PC Closed.')
    except Exception:
        await client.send_message(message.channel, 'Box index out of bounds.')

#Shortcut command to display a party pokemons details.
#Params: Party_index.
async def party_details(message):
    params = message.content.split()
    try:
        index = int(params[1])
    except Exception:
        await client.send_message(message.channel, 'Invalid Format.')
        return
    if not await is_player(message):
        return
    player = instances.read_playerfile(message.author.id)
    try:
        await show_poke_details(message, player.party[index-1])
    except Exception:
        await client.send_message(message.channel, 'Party index out of bounds.')

#test command to fight a simple AI.
#Params: NONE
async def test_fight(message):
    player = instances.read_playerfile(message.author.id)
    p1 = battle.BattlePlayer(client, player, message.author)
    robot_poke = p1.curr_party[0].poke.to_dict()
    robot_poke['name'] += '_bot'
    robot_poke = instances.read_pokedict(robot_poke)
    p2 = battle.BattleAI('Mr. Roboto',
                      [robot_poke],
                      'RAND',
                      'Hey, I won!',
                      'Hey, You won!')
    battle_instance = battle.Battle(p1, p2, client, message.channel)
    await battle_instance.play_battle()

#fight a specific npc for no money or xp    
async def npc_test(message):
    npc_id = message.content[7:]
    await battle.ai_exhibition(client, message, npc_id)
    
#Helper funct to display the current catching location
async def show_loc(message):
    location_name, timeleft = await get_location(return_timeleft=True)
    location_name = get_area_loc_name(location_name)
    await client.send_message(message.channel, 'Current Location: ' + location_name.replace('-',' ').title() + '\nHours Remaining: '+str(timeleft))

#Helper funct to display an overview of the players party
async def show_party(message):
    if not await is_player(message):
        return
    player = instances.read_playerfile(message.author.id)
    await client.send_message(message.channel, player.str_party())
    
#check if user registered, if not let them know to register    
async def is_player(message):
    global players
    players = [name[:-4] for name in os.listdir(PLAYER_PATH)]
    if message.author.id in players:
        return True
    else:
        await client.send_message(message.channel, 'Error, please register using ";join"!')
        return False
        
#Helper funct for when you ask the user a yes or no question
async def yes_or_no(message, question, can_cancel=False):
    if can_cancel:
        await client.send_message(message.channel, question+'\n(y/n), or "cancel" to cancel')
    else:
        await client.send_message(message.channel, question+' (y/n)')
    response2 = await client.wait_for_message(author=message.author, channel=message.channel)
    response2 = response2.content.lower()
    if response2 == 'y' or response2 == 'yes':
        return 'y'
    elif response2 == 'no' or response2 == 'n':
        return 'n'
    elif response2 in exits:
        if can_cancel:
            return 'c'
        else:
            return 'o'
    else:
        return 'o'

#Display a given poke's pic (correctly adjusts for shinies, unown, nido, etc)
async def send_pic(message, poke):
    await client.send_file(message.channel, poke.get_pic())

#Converts given amount of seconds to minutes (and rounds)
async def seconds_to_minutes(t):
    return int(t/60)

#Reads the current location from the database. If enough time has passed
#since the last loc change, change the location. Setting force to True 
#forces this change.
async def get_location(return_timeleft=False, force=False):
    with open(CURRLOC_FILE, 'r') as f:
        stored_loc = json.load(f)
    curr_now = datetime.datetime.now()
    curr_time = curr_now.day*24 + curr_now.hour
    if force or stored_loc['time'] > curr_time or curr_time - stored_loc['time'] > HOURS_LOC_DELAY:
        #update time and loc
        stored_loc['time'] = curr_time
        loc = random.choice(locations)
        print('New Location:'+loc)
        stored_loc['loc'] = loc
        with open(CURRLOC_FILE, 'w') as f:
            json.dump(stored_loc,f)
    if return_timeleft:
        return stored_loc['loc'], HOURS_LOC_DELAY - (curr_time - stored_loc['time'])
    return stored_loc['loc']

#Looks through a players party, and sees if any pokemon is eligable to evolve
#This is based on the given evolution trigger.
#Params item and tradewith are used for specific types of evolution.
async def check_apply_evo(message, player, trigger, item=None, tradewith=None):
    for poke in player.party:
        evo = poke.find_evo(trigger, await get_location(), player, item, tradewith)
        #evo is a species data
        if evo != None:
            await asyncio.sleep(4)
            await client.send_message(message.channel, '...What?')
            await asyncio.sleep(1)
            await client.send_message(message.channel, poke.name + ' is evolving!\n(say \'cancel\' to stop evolution)')
            for _ in range(5):
                await asyncio.sleep(1)
                await client.send_message(message.channel, '.')
            await client.send_message(message.channel, poke.name + ' has evolved into ' + get_poke_name(evo) + '!!')
            if poke.has_base_name():
                poke.name = get_poke_name(evo)
            poke.id = int(evo)
            await show_poke_details(message, poke)

#Runs the client, and retrys if the connection fails.
#Dont use this! it doesnt really work-- just make a batch/sh file to loop it.            
def run_client(client, *args, **kwargs):
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(client.start(*args, **kwargs))
        except KeyboardInterrupt as k:
            raise k
        except Exception as e:
            print("Error", e)  # or use proper logging
        print("Retrying until restart...")
        time.sleep(60)
        
        
#file is stored in a seperate file (outside the repo).
#This is to keep the key off github
with open(KEY_PATH, 'r') as f:
    key = f.read() 

client.run(key)
#run_client(client, key)

