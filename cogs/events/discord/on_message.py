import discord
import re
import time
from discord.ext import commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.gacha.give_rewards import GiveRewards

class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
        self.giver: GiveRewards = None
        self.url_pattern = r'https?://(?:www\.)?\S+'
        self.updates_channel = self.bot.config.get("channels", {})["deepwoken_updates"]
        self.updates_channel_obj = self.bot.get_channel(self.updates_channel)
        self.suggest_channel = self.bot.config.get("channels", {})["suggest"]
        self.suggestions_channel = self.bot.config.get("channels", {})["suggestions"]
        self.suggestions_channel_obj = self.bot.get_channel(self.suggestions_channel)
        self.image_perms = self.bot.config.get("roles", {})["image_perms"]
        self.server_booster = self.bot.config.get("roles", {})["booster"]
        self.tinky_emoji = self.bot.get_emoji(1327884746776121444)
        self.emery_emoji = self.bot.get_emoji(1327884755391479828)
        self.responses = {
            893871497876213791: "Yo también te quiero Ken <3",
            730442077011312651: "我希望我是一只鸟",
            740294285366395001: "Me cago en tus ### hijo de la grandisima ###. Ya va siendo hora de que te ##@@/*",
            992172983017812099: "Mandame fotos de tu erizo :3",
            509808641063387147: "Liquido reproductivo",
            474625767377207326: "Es Vianix el pescador, con su caña y su sombrilla...",
            338992922034831371: "Domado, domado domado domado",
            509808641063387147: "Prepucaldooooo... Y SEMN"
        }

    async def check_give_rewards(self, message:discord.Message):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.giver = self.bot.get_cog("GiveRewards") if self.giver is None else self.giver
        # Create user object
        user_data = await self.database.get_user_data(user_id=int(message.author.id))
        
        # Gets the current time
        current_time = int(time.time())
        
        # To check later if the user had leveled up
        previous_level = user_data['level']

        # Checks if a minute has been passed between the last message
        if user_data['last_message'] == None or current_time - user_data['last_message'] >= 60:
              
            # Sets the last message sent
            user_data['last_message'] = current_time
            
            # Get the booster role of the server by id, if the user dosn't have it, make it null
            booster_role = message.author.get_role(self.server_booster) if message.author.get_role(self.server_booster) else None
            
            # To check if a level up message has to be sent
            previous_level = user_data['level']
            
            # Give the rewards
            user_data = await self.giver.give_message_reward(data=user_data, server_booster_role=booster_role)
        
        user_data = await self.giver.check_level_up(data=user_data)

        # Checks if the user has leveled up
        if user_data['level'] > previous_level:
            await message.channel.send(f"¡<@{message.author.id}>, has subido al nivel {user_data['level']}!")
        cuser_data = user_data.copy()
        await self.database.save_user_data(user_id=user_data['id'], data=cuser_data)

    # Checks from who is the DM
    async def checkDM(self, message):
        if message.author.id in self.responses:
            await message.author.send(self.responses[message.author.id])
        else:
            await message.author.send("No puedes interactuar con el bot por md. Por favor, utiliza los canales del servidor para usar los comandos.")
        return

    # Processes the message and sends it as a suggestion in a channel
    async def checkSuggestion(self, message):

        # Checks if the message starts with ".s "
        if not message.content.startswith('.s '):
            await message.delete()
            try:

                # Send Dm to the user
                await message.author.send("Para hacer una sugerencia, por favor usa el prefijo `s. ` seguido de tu sugerencia.\nEjemplo: `s. [Tu sugerencia aquí]`")
            except discord.Forbidden:

                # Can't send DM to the user
                print(f"No se pudo enviar DM a {message.author.name}.")
            print("Incorrect suggestion message sent") # TODO LOG
            return
        
        # If it has a link and send report DM
        if re.search(self.url_pattern, message.content):
            try:
                await message.author.send("No puedes enviar enlaces en las sugerencias")
                await message.delete()
                return
            except discord.Forbidden:

                # The bot can't send DMs to the user
                print(f"No se pudo enviar DM a {message.author.name}.")
                return
            
        # In case that the channel cannot be found
        if not self.suggestions_channel_obj:
            print(f"No se ha encontrado el canal")
            await message.delete()
            return
        
        # Delete the first three characters
        suggestion = message.content[3:].strip()

        # Create embed
        embed = discord.Embed(
            title="💡 ¡Nueva Sugerencia Recibida! 💡",
            color=discord.Color.green()
        )

        embed.add_field(
            name="📝 Sugerencia:",
            value=f"**__{suggestion}__**",
            inline=False
        )
        
        # Add the author name
        embed.set_author(
            name=f"💬 Sugerencia Propuesta por {message.author.name}"
        )

        # Set the thumbnail as the pfp of the user
        try:
            embed.set_thumbnail(url=message.author.avatar.url)

        # In case that the avatar is null, use a default one instead
        except AttributeError:
            print(f"{message.author.name} no tiene avatar, usando imagen predeterminada.")
            
            # Set the avatar of the author as thumbnail
            embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/9NmCvbrWMNfRMMT_d42ejZRNvj1rseRwMlyik_0Epqc/https/discord.com/assets/788f05731f8aa02e.png?format=webp&quality=lossless")
        
        # Send the embed and save it
        suggestion_message = await self.suggestions_channel_obj.send(embed=embed)

        # Checks if the emojis exist
        if not self.tinky_emoji and self.emery_emoji:
            print("No se pudieron encontrar los emotes personalizados.")
        try:
            # Add the reaction to the embed
            await suggestion_message.add_reaction(self.tinky_emoji)
            await suggestion_message.add_reaction(self.emery_emoji)
        except Exception as e:
            print(f"No se han podido poner los emojis en la sugerencia: {e}")

        # Message the user to DM to thank for the suggestion
        try:
            dm_embed = discord.Embed(
                title="Gracias por tu sugerencia",
                description=f"Tu sugerencia fue enviada con éxito:\n\n{suggestion}",
                color=discord.Color.green()
            )
            dm_embed.set_footer(
                text="Los usuarios valorarán tu sugerencia.")
            await message.author.send(embed=dm_embed)
        except discord.Forbidden:

            # The bot can't send DMs to the user
            print(f"No se pudo enviar DM a {message.author.name}.")

        await message.delete()

    # For every message sent to the bot or in the server
    @commands.Cog.listener()
    async def on_message(self, message):
        
        # Stops if the message is from the bot
        if message.author.bot:
            return

        # The message don't come from a server
        if message.guild is None:
            await self.checkDM(message)
            return

        # Get the role "Cuarentena" and delete messages from users with the role
        quarantine_role = discord.utils.get(message.guild.roles, name="Cuarentena")
        if quarantine_role:
            if quarantine_role in message.author.roles:
                await message.delete()
                return

        # Checks if the message has been sent on suggestions channel
        if message.channel.id == self.suggest_channel:
            await self.checkSuggestion(message)
            return

        # Check if the user has permission to send url
        if re.search(self.url_pattern, message.content):
            roles = [role.id for role in message.author.roles]
            if self.image_perms not in roles:
                await message.delete()
                try:
                    dm_channel = await message.author.create_dm()
                    await dm_channel.send(f"Hola {message.author.name}, para poder enviar enlaces debes desbloquear el rol de **Permisos de imagen**. Este rol se consigue realizando el comando `/roll` en el canal https://discord.com/channels/776247434384375818/1312478372357603399.")
                except Exception as e:
                    print(f"Error al enviar DM a {message.author.name}: {e}")

        # Checks if the message has been sent in updates channel
        if message.channel.id == self.updates_channel:
            
            # Warn on the terminal
            print("Mensaje enviado en el canal de actualización") # TODO LOG
            
            # Gets the 'CheckForUpdates' cog
            check_for_updates_obj = self.bot.get_cog("CheckForUpdates")
            
            # If the task is not started, start it
            if not check_for_updates_obj.is_running:
                await check_for_updates_obj.run_task()

            # Set the last message for the updates
            last_message = message.created_at         
            await check_for_updates_obj.set_last_message(last_message)

        # Responses Meow if the message contains meow
        if re.search('meow', (message.content).lower()):
            await message.channel.send("Meow")

        await self.check_give_rewards(message=message)

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(OnMessage(bot))