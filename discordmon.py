import discord, os, instances, json, asyncio
import math, random, time, datetime
from poke_data import *
cooldown = 3600 #seconds, == 1 hour
exits = ['exit', 'e x i t', 'c', 'cancel', 'exiT', '"exit"', ';exit', ';cancel', 'close', 'exit\\']
client = discord.Client()
prefix = ';'

player_path    = '../players/'
timestamp_file = './data/timestamps.txt'
currloc_file = './data/currloc.txt'
locations = [name[:-4] for name in os.listdir('./data/locations/')]
players = [name[:-4] for name in os.listdir(player_path)]
players_in_session = []
PC_TIMEOUT = 60
HOURS_LOC_DELAY = 6
WILD_FIGHT_TIME = 5 #seconds
@client.event

async def on_ready():
    print('Online.')

@client.event
async def on_message(message):
    if message.author != client.user and message.author.id not in players_in_session:
        players_in_session.append(message.author.id)
        if message.content.startswith(';'):
            cmd = message.content[1:].lower()
            try:
                if   cmd in ['encounter', 'pokemon', 'p', 'e']:
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
            except Exception as e:
                #we catch this so it doesn't hang that user's session on error,
                #but we still want to see what went wrong so:
                print(type(e))
                print(e)
        players_in_session.remove(message.author.id)  
    return

async def encounter_poke(message):
    #check if current user is a player
    if not await is_player(message):
        return
    player = instances.read_playerfile(message.author.id)
    #check if the correct amount of time has passed
    with open(timestamp_file, 'r') as f:
        time_data = json.load(f)
    if player.id in time_data:
        last_time = time_data[player.id]
        diff = int(time.time()) - last_time
        if diff < cooldown:
            remain = cooldown-diff
            if remain > 60:
                remain = await seconds_to_minutes(remain)
                await client.send_message(message.channel, 'Please wait ' + str(remain) + ' minute(s) before catching another!')
            else:
                await client.send_message(message.channel, 'Please wait ' + str(remain) + ' seconds(s) before catching another!')
            return
    #-------END OF CHECKS-------        
    #set up pokemon, and return if location contains none
    tries = 5
    poke = None
    while poke == None and tries >= 0:
        poke = instances.make_for_encounter(await get_location())
        tries -= 1
    if poke == None:
        await client.send_message(message.channel, 'You found... nothing!')
        return
    
    output = 'A wild ' + str(poke.name) + ' Appears!'
    output += '\nLevel:    ' + str(poke.level)
    await client.send_message(message.channel, output)
    await send_pic(message, poke)
    await client.send_message(message.channel, '----------------')
    
    #check if the player even has a party.
    #if no party, always catch pokemon and never fight
    if player.party == []:
        await catch_poke(message, player, poke)
        done = True
    else:
        done = False
    output = ''
    while not done:
        output += 'Catch or Fight? (c/f)'
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
                await fight_poke(message, player, poke)
            else:
                output = 'Invalid Response.'
    #player should have encountered a poke to get here
    #update the players timeout, they will have to wait through the timeout again after
    with open(timestamp_file, 'r') as f:
        time_data = json.load(f)
    time_data[player.id] = int(time.time())
    #with open(timestamp_file, 'w') as f:
    #    json.dump(data, f)
    instances.write_player(player)
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
    
async def fight_poke(message, player, poke):
    player_power = player.get_party_power()
    diff = player_power - poke.level
    await client.send_message(message.channel, 'Simulating Battle...')
    await asyncio.sleep(WILD_FIGHT_TIME) #wait for dramatic tension
    if player_power >= int(random.normalvariate(poke.level, int(math.sqrt(poke.level)))):
        output = poke.name + ' Defeated!'
        await client.send_message(message.channel, output)
        await distribute_xp(message, player, poke)
    else:
        await client.send_message(message.channel, 'You lost the battle...')

async def distribute_xp(message, player, wild_poke):
    if player.party == []:
        return
    output = ''
    xp = wild_poke.get_base_xp() * wild_poke.level
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
            await client.send_message(message.channel, player.party[0].name + ' Leveled Up!')
        else:
            msg = player.party[0].name + ' Gained ('+str(player.party[0].level - og_level)+') Levels!'
            await client.send_message(message.channel, msg)
        await learn_new_moves(message, poke, poke.find_new_moves(og_level))
    if len(player.party) > 1:
        for poke in player.party[1:]:
            og_level = poke.level
            poke.add_xp(int(xp/len(player.party[1:])))
            if og_level != poke.level:
                if poke.level - og_level == 1:
                    await client.send_message(message.channel, poke.name + ' Leveled Up!')
                else:
                    msg = poke.name + ' Gained ('+str(poke.level - og_level)+') Levels!'
                    await client.send_message(message.channel, msg)
                await learn_new_moves(message, poke, poke.find_new_moves(og_level))
async def learn_new_moves(message, poke, moves):
    for move in moves:
        if len(poke.moves) < 4:
            poke.moves.append(move)
            client.send_message(message.channel, poke.name + ' learned ' + move)
        else:
            done = False
            while not done:
                output = poke.name + ' wants to learn <' + move + '> but '+ poke.name
                output += 'already knows 4 moves! Should a move be forgotten to make space for ' + move + '?'
                response = await yes_or_no(message, output)
                if response == 'y':
                    output = poke.name + '\'s moves:'
                    for index, m in poke.moves:
                        output += '\n' + str(index) + ') ' + m
                    output += '\nWhat move will be replaced with ' + move + '?'
                    output += '\nsay "cancel" to cancel.'
                    client.send_message(message.channel, output)
                    done2 = False
                    while not done2:
                        response2 = await wait_for_message(author=message.author, channel=message.channel).content.lower()
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
                                
                                output = '1, 2 and... Poof! ' + poke.name + ' forgot '+ poke.moves[index]
                                output += '\nand... ' + poke.name + ' learned ' + move + '!'
                                poke.moves[index] = move
                                await client.send_message(message.channel, output)
                                done = True
                                done2 = True
                elif response == 'n':
                    response2 = await yes_or_no(message, 'Stop learning ' + move +'?')
                    if response2 == 'y':
                        await client.send_message(message.channel, poke.name + ' did not learn ' + move + '.')                   
                elif response == 'o':
                    await client.send_message(message.channel, 'Error, Invalid Response.')
                    
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
                    
async def pc_wrapper(message):
    try:
        num = int(message.content.lower()[3:])
    except Exception:
        await client.send_message(message.channel, 'Invalid Index.')
    else:
        await show_boxes(message, curr_box=num-1)

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
                        disp_pc = True
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
                        disp_pc = True
            else:
                fails += 1
                if fails == 3:
                    done = True
            
        else:
            done = True
    await client.send_message(message.channel, player.name + '\'s PC closed.')
    instances.write_player(player)
    
async def show_poke_details(message, poke):
    await client.send_message(message.channel, '```Details for ' + poke.name + ':```')
    await send_pic(message, poke)
    output =  '\n```Lvl ' + str(poke.level) + ' ' + poke.get_species() + ' (<Gender_Goes_Here>)'
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
        await client.send_message(message.channel, 'Invalid Index.')
        
async def show_loc(message):
    location_name, timeleft = await get_location(return_timeleft=True)
    location_name = get_area_loc_name(location_name)
    await client.send_message(message.channel, 'Current Location: ' + location_name.replace('-',' ').title() + '\nHours Remaining: '+str(timeleft))

async def show_party(message):
    if not await is_player(message):
        return
    player = instances.read_playerfile(message.author.id)
    await client.send_message(message.channel, player.str_party())
    
#check if user registered, if not let them know to register    
async def is_player(message):
    global players
    players = [name[:-4] for name in os.listdir(player_path)]
    if message.author.id in players:
        return True
    else:
        await client.send_message(message.channel, 'Error, please register using ";join"!')
        return False
        
#for when you ask the user a yes or no question
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

async def send_pic(message, poke):
    await client.send_file(message.channel, poke.get_pic())

async def seconds_to_minutes(t):
    return int(t/60)

async def get_location(return_timeleft=False):
    with open(currloc_file, 'r') as f:
        stored_loc = json.load(f)
    curr_time = datetime.datetime.now()
    if stored_loc['day'] == curr_time.day and curr_time.hour - stored_loc['hour'] < HOURS_LOC_DELAY:
        pass
    else:
        stored_loc['day']  = curr_time.day
        stored_loc['hour'] = curr_time.hour
        loc = random.choice(locations)
        print('New Location:'+loc)
        stored_loc['loc'] = loc
        with open(currloc_file, 'w') as f:
            json.dump(stored_loc,f)
    if return_timeleft:
        return stored_loc['loc'], HOURS_LOC_DELAY - (curr_time.hour - stored_loc['hour'])
    return stored_loc['loc']

def run_client(client, *args, **kwargs):
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(client.start(*args, **kwargs))
        except Exception as e:
            print("Error", e)  # or use proper logging
        print("Waiting until restart")
        time.sleep(100)

with open('../key.txt', 'r') as f:
    key = f.read() 
#client.run(key)
run_client(client, key)

