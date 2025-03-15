import discord
from discord.ext import commands
from discord import app_commands
import re
import time
import asyncio
from cogs.utils.gacha import GetUserData
from cogs.events.tasks import CheckForUpdates

class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url_pattern = r'https?://(?:www\.)?\S+'
        self.updates_channel = self.bot.config.get("channels", {})["deepwoken_updates"]
        self.updates_channel_obj = self.bot.get_channel(self.updates_channel)
        self.suggest_channel = self.bot.config.get("channels", {})["suggest"]
        self.suggestions_channel = self.bot.config.get("channels", {})["suggestions"]
        self.dwupdates = self.bot.config.get("roles", {})["deepwoken_updates"]
        self.dwupdates_role = f"<@&{self.dwupdates}>"

        self.tinky_emoji = self.bot.get_emoji(1295755914862923837)
        self.emery_emoji = self.bot.get_emoji(1295755990544941127)
        self.responses = {
            893871497876213791: "Yo también te quiero Ken <3",
            730442077011312651: "我希望我是一只鸟",
            740294285366395001: "Me cago en tus ### hijo de la grandisima ###. Ya va siendo hora de que te ##@@/*",
            992172983017812099: "Mandame fotos de tu erizo :3",
            474625767377207326: "Es Vianix el pescador, con su caña y su sombrilla..."
        }

    # Checks from who is the DM
    async def checkDM(self, message):
        if message.author.id in self.responses:
            await message.author.send(self.responses[message.author.id])
        else:
            await message.author.send("No puedes interactuar con el bot por md. Por favor, utiliza los canales del servidor para usar los comandos.")
        return

    # Processes the message and sends it as a suggestion in a channel
    async def checkSuggestion(self, message):

        # Delete the message if it has a link and send report DM
        if re.search(self.url_pattern, message.content):
            try:
                await message.author.send("No puedes enviar enlaces en las sugerencias")
            except discord.Forbidden:

                # The bot can't send DMs to the user
                print(f"No se pudo enviar DM a {message.author.name}.")
        else:

            # Delete the first three characters
            suggestion = message.content[3:].strip()

            # Get the channel on the server by the ID
            suggestions_channel_obj = self.bot.get_channel(
                self.suggestions_channel)

            # Create an embed for the suggestion
            if suggestions_channel_obj:
                embed = discord.Embed(
                    title="💡 ¡Nueva Sugerencia Recibida! 💡",
                    color=discord.Color.green()
                )

                embed.add_field(
                    name="📝 Sugerencia:",
                    value=f"**__{suggestion}__**",
                    inline=False
                )

                # Set the avatar of the author as thumbnail
                embed.set_thumbnail(url=message.author.avatar.url)

                # Add the author name
                embed.set_author(
                    name=f"💬 Sugerencia Propuesta por {message.author.name}"
                )

                # Send the embed and save it
                suggestion_message = await suggestions_channel_obj.send(embed=embed)

                # Checks if the emojis exist and reacts with them to the message
                if self.tinky_emoji and self.emery_emoji:
                    await suggestion_message.add_reaction(self.tinky_emoji)
                    await suggestion_message.add_reaction(self.emery_emoji)
                else:
                    print("No se pudieron encontrar los emotes personalizados.")

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
    async def on_member_join(self, message):
        
        # Stops if the message is from the bot
        if message.author.bot:
            return

        # The message don't come from a server
        if message.guild is None:
            await self.checkDM(message)

        # Get the role "Cuarentena" and delete messages from users with the role
        quarantine_role = discord.utils.get(
            message.guild.roles, name="Cuarentena")
        if quarantine_role:
            if quarantine_role in message.author.roles:
                await message.delete()

        # Checks if the message has been sent on suggestions channel and startswith ".s "
        if message.channel.id == self.suggest_channel and message.content.startswith('.s '):
            await self.checkSuggestion()

        # Warn the user to send the message correctly though DM
        elif message.channel.id == self.suggest_channel and not message.content.startswith('.s '):
            await message.delete()
            try:

                # Send Dm to the user
                await message.author.send("Para hacer una sugerencia, por favor usa el prefijo `s. ` seguido de tu sugerencia.\nEjemplo: `s. [Tu sugerencia aquí]`")
            except discord.Forbidden:

                # Can't send DM to the user
                print(f"No se pudo enviar DM a {message.author.name}.")

        # Check if the user has permission to send url
        if re.search(self.url_pattern, message.content):
            roles = [role.name for role in message.author.roles]
            if "Permisos de imagen" not in roles:
                await message.delete()
                try:
                    dm_channel = await message.author.create_dm()
                    await dm_channel.send(f"Hola {message.author.name}, para poder enviar enlaces debes desbloquear el rol de **Permisos de imagen**. Este rol se consigue realizando el comando `/roll` en el canal [Lupus Roll](https://discord.com/channels/776247434384375818/1312478372357603399).")
                except Exception as e:
                    print(f"Error al enviar DM a {message.author.name}: {e}")

        # Checks if the message has been sent in updates channel
        if message.channel.id == self.updates_channel:
            
            # Gets the 'CheckForUpdates' cog
            check_for_updates_obj:CheckForUpdates = self.bot.get_cog("CheckForUpdates")
            
            # Set the last message for the updates
            last_message = message.created_at         
            check_for_updates_obj.set_last_message(last_message)


        # Responses Meow if the message contains meow
        if re.search('meow', (message.content).lower()):
            await message.channel.send("Meow")

        # Get the user ID as int
        user_id = int(message.author.id)

        # Create user object
        user_data = GetUserData(user_id) # TODO
        last_message_time = user_data.get_last_message()  # Get attribute

        # Gets the current time
        current_time = time.time()

        # Checks if a minute has been passed between the last message
        if current_time - last_message_time >= 60:
            # TODO utils.gacha.give_rewards
            pass
        await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(OnMessage(bot))