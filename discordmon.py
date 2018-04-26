import discord, os, instances, datetime, random

client = discord.Client()
prefix = ';'
locations = [name[:-4] for name in os.listdir('./data/locations/')]
loc = random.choice(loc)
@client.event
async def on_message(message):
    if message.author != client.user:
        is message.content == prefix+'pokemon':
            loc = random.choice(loc)
            pokemon = make_for_encounter(loc)
            await client.send_message(message.channel, str(pokemon))
    return
client.run('<SecretKey>')