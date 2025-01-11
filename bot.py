import asyncio
import json
import aiofiles
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

async def load_cogs(bot):
    cogs_names = []
    # Looks all files through cogs
    for root, dirs, files in os.walk("cogs"):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                # Get the name of the directory
                cog_name = os.path.splitext(os.path.relpath(os.path.join(root, file)))[0]
                cog_name = cog_name.replace(os.sep, ".")  # Convierte las barras a puntos
                cogs_names.append(cog_name)

    # Carga todas las extensiones encontradas
    for cog in cogs_names:
        try:
            await bot.load_extension(cog)
            print(f"Cog '{cog}' cargado con éxito.")
        except Exception as e:
            print(f"No se pudo cargar el cog '{cog}'. Error: {e}")

# Loads the config.json
async def config_load():
    # Open the filewith async
    async with aiofiles.open("config.json", mode="r") as f:
        # Load the content of the file as a dictionary
        config_content = await f.read()
        config = json.loads(config_content)
    return config

asyncio.run(load_cogs(bot))

@bot.tree.command(name="refresh", description="Recarga los cogs del bot admin")
@app_commands.default_permissions(administrator=True)
async def refresh(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    bot.dispatch("extensions_stop")
    await load_cogs(bot)
    try:
        synced = await bot.tree.sync()
        print(f'Se han sincronizado {len(synced)} comandos de la aplicación.')
        commands = await bot.tree.fetch_commands() # Show syncronized commands  
        print(", ".join(command.name for command in commands)) # Separated with comma
    except Exception as e:
        print(f'Error al sincronizar los comandos de aplicación: {e}')
    try:
        # Loads the config.json
        bot.config = await config_load()
        print("Configuración cargada correctamente.")
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
    bot.dispatch("extensions_ready")
    await interaction.followup.send(f"Se han recargado los cogs: {len(synced)} y configuración cargada correctamente.", ephemeral=True)

# Bot execution
@bot.event
async def on_ready(): # Start event
    try:
        # Loads the config.json
        bot.config = await config_load()
        print("Configuración cargada correctamente.")
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

# Run the bot
bot.run(TOKEN)