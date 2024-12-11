# Importaciones de librerías y archivos locales
import discord
from discord.ext import commands
import os  # Importar el módulo os
import lupus.config.config  # Carga las variables (asegúrate de que config tiene TOKEN)

# Declaración de variables
intents = discord.Intents.default()  # Crea una instancia de intents con permisos predeterminados básicos
intents.message_content = True  # Lee los mensajes del usuario
intents.members = True  # Permite escuchar eventos de miembros
intents.guilds = True  # Permite al bot recibir eventos relacionados con servidores (guilds)

# Crea una instancia de la clase Bot, configurando el prefijo de comandos y los permisos (intents)
bot = commands.Bot(command_prefix='dw/', intents=intents)

@bot.event  # Evento de bot on_ready
async def on_ready():
    try:
        # Cargar todos los comandos desde la carpeta 'lupus/comandos'
        for filename in os.listdir('./lupus/comandos'):  # Itera sobre los archivos en la carpeta 'lupus/comandos'
            if filename.endswith('.py') and filename != '__init__.py':  # Excluir '__init__.py'
                command_name = f'lupus.comandos.{filename[:-3]}'  # Elimina la extensión .py del nombre del archivo
                try:
                    await bot.load_extension(command_name)  # Cargar el comando (cog)
                    print(f'Comando cargado: {command_name}')
                except Exception as e:
                    print(f'Error al cargar el comando {command_name}: {e}')  # Imprimir el error correcto
    except Exception as e:
        print(f"Error al cargar la carpeta de comandos: {e}")
    
    try:
        # Sincroniza los comandos del bot con / (slash commands)
        synced = await bot.tree.sync()
        print(f'Se han sincronizado {len(synced)} comandos de la aplicación (slash commands).')
    except Exception as e:
        print(f'Error al sincronizar los comandos de la aplicación: {e}')
    
    try:
        check_live_status.start()  # Comprueba si el usuario está en directo
        if not check_for_updates.is_running():  # Comprueba si hay alguna actualización
            check_for_updates.start()
    except NameError:
        print("Las tareas 'check_live_status' o 'check_for_updates' no están definidas.")

    print(f'Bot {bot.user.name} está listo y conectado a Discord!')

# Ejecuta el bot
bot.run(lupus.config.config.TOKEN)  # Asegúrate de que lupus.config.config.TOKEN contiene el token de tu bot
