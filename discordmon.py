import discord, os, instances, datetime, random, json, time, datetime
from poke_data import *
cooldown = 3600 #seconds, == 1 hour
exits = ['exit', 'e x i t', 'c', 'cancel', 'exiT', '"exit"', ';exit', ';cancel', 'close', 'exit\\']
client = discord.Client()
prefix = ';'
locations = [name[:-4] for name in os.listdir('./data/locations/')]
players = [name[:-4] for name in os.listdir('./data/players/')]
timestamp_file = './data/timestamps.txt'
currloc_file = './data/currloc.txt'
players_in_session = []
PC_TIMEOUT = 60
HOURS_LOC_DELAY = 6
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
                if   cmd in ['catch', 'pokemon', 'p']:
                    await catch_poke(message)
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
            except Exception as e:
                #we catch this so it doesn't hang that user's session on error,
                #but we still want to see what went wrong so:
                print(e)
        players_in_session.remove(message.author.id)  
    return

async def catch_poke(message):
    #check if current user is a player
    if not await is_player(message):
        return
    player = instances.read_playerfile(message.author.id)
    #check if the correct amount of time has passed
    with open(timestamp_file, 'r') as f:
        data = json.load(f)
    if player.id in data:
        last_time = data[player.id]
        diff = int(time.time()) - last_time
        if diff < cooldown:
            remain = cooldown-diff
            if remain > 60:
                remain = await seconds_to_minutes(remain)
                await client.send_message(message.channel, 'Please wait ' + str(remain) + ' minute(s) before catching another!')
            else:
                await client.send_message(message.channel, 'Please wait ' + str(remain) + ' seconds(s) before catching another!')
            return
    #set up pokemon and catch it
    poke = instances.make_for_encounter(await get_location())
    if poke == None:
        await client.send_message(message.channel, 'You caught... nothing!')
        return
    else:
        output = 'You caught ' + str(poke.name) + '!'
        output += '\nLevel:    ' + str(poke.level)
        await client.send_message(message.channel, output)
        await send_pic(message, poke)
        await client.send_message(message.channel, '----------------')
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
        data[player.id] = int(time.time())
        with open(timestamp_file, 'w') as f:
            json.dump(data, f)

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
    show_pc = True
    while not done:
        if show_pc:
            output = '```---- ' + player.name +'\'s PC ----'
            output +=  '\nBox ' + player.boxes[curr_box].name
            output += ' (' + str(curr_box+1) + '/' + str(len(player.boxes)) + '):\n'
            output += str(player.boxes[curr_box])
            output += '\nCommands:'
            output += '\n"details <index>" --- Show more details on specified pokemon'
            if curr_box < len(player.boxes)-1:
                output += '\n">" -- next box'
            if curr_box > 0:
                output += '\n"<" -- previous box'
            output +=  '\n"exit" -- close pc'
            output += '```'
            await client.send_message(message.channel, output)
            show_pc = False
        else:
            
            output = '```\nCommands:'
            output += '\n"details <index>" --- Show more details on specified pokemon'
            if curr_box < len(player.boxes)-1:
                output += '\n">" -- next box'
            if curr_box > 0:
                output += '\n"<" -- previous box'
            output +=  '\n"exit" -- close pc'
            output += '```'
            await client.send_message(message.channel, output)
        response = await client.wait_for_message(author=message.author, channel=message.channel, timeout=PC_TIMEOUT)
        if response != None:
            response = response.content.lower()
            if response == None:
                done = True
            elif response == '>' and curr_box < len(player.boxes)-1:
                curr_box += 1
            elif response == '<' and curr_box > 0:
                curr_box -= 1
            elif response in exits:
                done = True
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
                    show_pc = False
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
                    show_pc = False
            else:
                await client.send_message(message.channel, 'Invalid Response.')
        else:
            done = True
    await client.send_message(message.channel, 'PC closed.')
    instances.write_player(player)
    
async def show_poke_details(message, poke):
    await client.send_message(message.channel, '```Details for ' + poke.name + ':```')
    await send_pic(message, poke)
    output =  '\n```Lvl ' + str(poke.level) + ' ' + poke.get_species() + ' (<Gender_Goes_Here>)'
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
        
#check if user registered, if not let them know to register    
async def is_player(message):
    global players
    players = [name[:-4] for name in os.listdir('./data/players/')]
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
        return stored_loc['loc'], HOURS_LOC_DELAY - (curr_time.hour - stored_loc['hour']) - 1
    return stored_loc['loc']

with open('../key.txt', 'r') as f:
    key = f.read() 
client.run(key)


