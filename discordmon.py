client = discord.Client()

@client.event
async def on_message(message):
    if message.author != client.user:
        
    return
client.run('<SecretKey>')