import discord
import requests
import re
import time
import random
import pocketbase
from discord.ext import commands
from cogs.utils.gacha.get_user_data import getUserData
from cogs.utils.gacha.save_user_data import saveUserData

class OnMessage (commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_user_data_cog = getUserData(bot)
        self.save_data_cog = saveUserData(bot)
        self.pb_url = 'http://localhost:8090'

    # When a message is sent
    @commands.Cog.listener()
    async def on_message(self, message):
        url_pattern = r'https?://(?:www\.)?\S+'
        if message.author.bot:
            return        # Check if the message is from an MD
        if message.guild is None:
            # Se podría implementar el chat con una IA
            await message.author.send("No puedes interactuar con el bot por md. Por favor, utiliza los canales del servidor para usar los comandos.")
            return

        if re.search(url_pattern, message.content):
            # Search if the user has image perms
            roles = [role.name for role in message.author.roles]
            if "Permisos de imagen" not in roles:
                await message.delete()
                try:
                    dm_channel = await message.author.create_dm()
                    await dm_channel.send(f"Hola {message.author.name}, para poder enviar enlaces debes desbloquear el rol de **Permisos de imagen**. Este rol se consigue realizando el comando `/roll` en el canal [bots](https://discord.com/channels/776247434384375818/1312478372357603399).")
                except Exception as e:
                    print(f"Error al enviar DM a {message.author.name}: {e}")
        # todo
        current_time = time.time()
        user_id = str(message.author.id)
        user_data = self.get_user_data_cog.get_user_data(user_id)
        echoes = user_data.get('Echoes', 0)
        experience = user_data.get('Experience', 0)
        last_message = user_data.get('Last message', 0)
        if last_message is None or last_message == 0 or current_time - last_message >= 60:
            booster_role_name = "Server Booster"
            last_message = current_time
            echoes_to_sum = 0
            experience_to_sum = 0
            if any(role.name == booster_role_name for role in message.author.roles):
                echoes_to_sum += random.randint(15, 25)
                experience_to_sum += random.randint(15, 25)
            else:
                echoes_to_sum += random.randint(1, 5)
                experience_to_sum += random.randint(1, 5)
            echoes += echoes_to_sum
            experience += experience_to_sum
            user_data['echoes'] = echoes
            user_data['experience'] = experience
            user_data['last_message'] = last_message
            self.save_data_cog.save_user_data(user_id, user_data)
        # todo       
        # if not check_for_updates.is_running():
        #     check_for_updates.start()
        allowed_channel = self.bot.get_channel(self.bot.config["channels"].get("deepwoken_updates"))
        suggest_channel = self.bot.get_channel(self.bot.config["channels"].get("suggest"))
        suggestions_channel = self.bot.get_channel(self.bot.config["channels"].get("suggestions"))
        if message.channel.id == suggest_channel and message.content.startswith('.s '):
            if re.search(url_pattern, message.content):
                user = message.author  # Obtén el autor del mensaje
                try:
                    # Envía un mensaje directo al usuario
                     await user.send("No puedes enviar enlaces en las sugerencias")
                except discord.Forbidden:
                    # Si el bot no puede enviar DM (por ejemplo, si el usuario tiene los DMs cerrados)
                    print(f"No se pudo enviar DM a {user.name}.")
            else:
                # Elimina los primeros tres caracteres (".s ") del mensaje
                suggestion = message.content[3:].strip()
                # Obtén el canal donde se enviará la sugerencia
                suggestions_channel_obj = bot.get_channel(suggestions_channel)
                if suggestions_channel_obj:
                    embed = discord.Embed(
                        title="💡 ¡Nueva Sugerencia Recibida! 💡",
                        color=discord.Color.green()  # Usamos azul para un tono profesional y atractivo
                    )
                    # Colocamos la sugerencia en un campo dedicado
                    embed.add_field(
                        name="📝 Sugerencia:",
                        value=f"**__{suggestion}__**",
                        inline=False
                    )
                    # Imagen de autor como thumbnail para hacerlo más personal
                    embed.set_thumbnail(url=message.author.avatar.url)
                    # Personalizamos el autor para hacerlo más destacado
                    embed.set_author(
                        name=f"💬 Sugerencia Propuesta por {message.author.name}"
                    )
                    # Envía el embed al canal de sugerencias
                    suggestion_message = await suggestions_channel_obj.send(embed=embed)
                    # Obtén los emotes personalizados usando sus IDs
                    tinky = bot.get_emoji(1295755914862923837)
                    emery = bot.get_emoji(1295755990544941127)
                    if tinky and emery:
                        # Agrega las reacciones usando los objetos de los emotes
                        await suggestion_message.add_reaction(tinky)  # Pulgar arriba
                        await suggestion_message.add_reaction(emery)  # Pulgar abajo
                    else:
                        print("No se pudieron encontrar los emotes personalizados.")
                    try:
                        dm_embed = discord.Embed(
                            title="Gracias por tu sugerencia",
                            description=f"Tu sugerencia fue enviada con éxito:\n\n{suggestion}",
                            color=discord.Color.green()
                            )
                        dm_embed.set_footer(text="Los usuarios valorarán tu sugerencia.")
                        await message.author.send(embed=dm_embed)
                    except discord.Forbidden:
                        # Si el usuario tiene los DMs desactivados, envía un mensaje al canal como alternativa
                        await message.channel.send(
                            f"No pude enviarte un mensaje directo, pero tu sugerencia fue enviada, {message.author.mention}."
                        )
                    await message.delete()
                elif message.channel.id == suggest_channel and not message.content.startswith('.s '):
                    print(f"El mensaje de {message.author} no comienza con '.s ' en el canal {message.channel.name}")
                    await message.delete()  # Elimina el mensaje enviado
                    user = message.author  # Obtén el autor del mensaje
                    try:
                        # Envía un mensaje directo al usuario
                        await user.send("Para hacer una sugerencia, por favor usa el prefijo `s. ` seguido de tu sugerencia.\nEjemplo: `s. Tu sugerencia aquí`")
                    except discord.Forbidden:
                        # Si el bot no puede enviar DM (por ejemplo, si el usuario tiene los DMs cerrados)
                        print(f"No se pudo enviar DM a {user.name}.")

            if message.channel.id == allowed_channel:
                last_message = message.created_at
                print(f"Mensaje procesado en canal permitido: {message.channel.name}")
            await bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(OnMessage(bot))