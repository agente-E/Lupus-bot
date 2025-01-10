import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Load private variables
load_dotenv()

# Get variables
TOKEN = os.getenv("TOKEN")

# Permisos del bot
intents = discord.Intents.default()  # Permission to read messages
intents.message_content = True  # Reads the messages content
intents.members = True  # Permission to read member events (Join, leave...)
intents.guilds = True # Permission for server information
intents.dm_messages = True # Permission to send messages though DM
intents.voice_states = True # Permission to receive voice state changes
bot = commands.Bot(command_prefix = "dw/", intents=intents) # Definition of the bot variable with prefix dw/

# Bot execution
@bot.event
async def on_ready(): # Start event
    
    # Get all the slash commands
    try:
        synced = await bot.tree.sync()
        print(f'Se han sincronizado {len(synced)} comandos de la aplicación (slash commands).')
        commands = await bot.tree.fetch_commands() # Show syncronized commands  
        print(", ".join(command.name for command in commands))
    except Exception as e:
        print(f'Error al sincronizar los comandos de aplicación: {e}')
    
    # Start the function to check if I'm on stream (remake todo)
    # check_live_status.start()
    # if not check_for_updates.is_running():
    #     check_for_updates.start()

    # Looks all channels on the discord servers
    for guild in bot.guilds:
        print(f"En el servidor: {guild.name}")
        # Looks all voice channels on every channel 
        for channel in guild.voice_channels:
            # Looks every user that it's on a voice channel
            for user_id, _ in channel.voice_states.items():
                member = guild.get_member(user_id)
                print(f"Miembro {member.name} está en el canal: {channel.name}")
                # asyncio.create_task(track_voice_time(member))
    
    # Makes the bot RPC change to "Jugando Deepwoken"
    await bot.change_presence(activity=discord.Activity(name="Deepwoken", type=0))
    print(f'Bot {bot.user.name} está listo y conectado a Discord!')

bot.run(TOKEN)