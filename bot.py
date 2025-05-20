import json
import aiofiles
import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Load private data
load_dotenv()

# Get private data
TOKEN = os.getenv("TOKEN")

# Bot perms
intents = discord.Intents.default()  # Permission to read messages
intents.message_content = True  # Reads the messages content
intents.members = True  # Permission to read member events (Join, leave...)
intents.guilds = True # Permission for server information
intents.dm_messages = True # Permission to send messages though DM
intents.voice_states = True # Permission to receive voice state changes
bot = commands.Bot(command_prefix = "dw/", intents=intents) # Definition of the bot variable with prefix dw/

async def load_cogs(bot):
    cogs_names = []

    # Looks all files through cogs folder
    for root, dirs, files in os.walk("cogs"):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                
                # Get the name of the directory
                cog_name = os.path.splitext(os.path.relpath(os.path.join(root, file)))[0]
                cog_name = cog_name.replace(os.sep, ".")
                cogs_names.append(cog_name)

    # Loads all found cogs
    for cog in cogs_names:
        # Get only the name of the cog (last part after the last dot)
        cog_display_name = cog.split('.')[-1]        

        # Checks if it's already loaded
        if cog in bot.extensions:
            print(f"Cog '{cog_display_name}' ya está cargado, recargando.")
            try:
                # TODO Add dispatch to running tasks
                await bot.unload_extension(cog)  # Unload the cog
                print(f"Cog '{cog_display_name}' descargado correctamente.")
            except Exception as e:
                print(f"Failed to unload cog '{cog_display_name}'. Error: {e}")

        try:
            await bot.load_extension(cog)
            print(f"Cog '{cog_display_name}' cargado con exito.")
        except Exception as e:
            print(f"No se pudo cargar el cog '{cog_display_name}'. Error: {e}")

# Loads the config.json and assigns it to the bot
async def load_config():       
    
    # Open the file with async
    async with aiofiles.open("config.json", mode="r") as f:
            
        # Load the content of the file as a dictionary
        config_content = await f.read()
        config = json.loads(config_content)
        
    return config

@bot.tree.command(name="refresh", description="Recarga los cogs del bot admin")
@app_commands.default_permissions(administrator=True)
async def refresh(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False, thinking=True)
    try:
        # Unload config.json
        print('Recargando configuración.')
        del bot.config
        
        # Load config.json
        bot.config = await load_config()
        print("Configuración cargada correctamente.")
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
    await load_cogs(bot)
    try:
        # Shows the loaded cogs
        synced = await bot.tree.sync()
        print(f'Se han sincronizado {len(synced)} comandos de la aplicación.')
        commands = await bot.tree.fetch_commands() # Show syncronized commands  
        print(", ".join(command.name for command in commands)) # Separated with comma
    except Exception as e:
        print(f'Error al sincronizar los comandos de aplicación: {e}')

    await interaction.followup.send(f"Se han recargado {len(synced)} comandos y configuración cargada correctamente.", ephemeral=True)

# Bot execution
@bot.event
async def on_ready(): # Start event
    try:
        # Loads the config.json
        bot.config = await load_config()
        print("Configuración cargada correctamente.")
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
    try:
        # Load all the cogs
        await load_cogs(bot)
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")    
    # Get all the slash commands
    try:
        synced = await bot.tree.sync()
        print(f'Se han sincronizado {len(synced)} comandos de la aplicación.')
        commands = await bot.tree.fetch_commands() # Show syncronized commands  
        print(", ".join(command.name for command in commands)) # Separated with comma
    except Exception as e:
        print(f'Error al sincronizar los comandos de aplicación: {e}')
    
    # Looks all channels on the discord servers
    for guild in bot.guilds:
        print(f"En el servidor: {guild.name}")
        
        # Looks all voice channels on the server
        for channel in guild.voice_channels:
            
            # Looks every user that it's on a voice channel
            for user_id, _ in channel.voice_states.items():
                member = guild.get_member(user_id)
                print(f"Miembro {member.name} está en el canal: {channel.name}")
                # TODO Add user to a list to track how much time it has been passed on a call to give the notes and exprerience 

    # Makes the bot RPC change to "Jugando Deepwoken"
    await bot.change_presence(activity=discord.Activity(name="Deepwoken", type=0))
    
    # The bot is Reaggie
    print(f'Bot {bot.user.name} está listo y conectado a Discord!')

# Run the bot
bot.run(TOKEN)