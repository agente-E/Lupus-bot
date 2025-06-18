import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild
from cogs.utils.gacha.give_rewards import GiveRewards

class Nivel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
        self.checker: CheckGuild = None

    @app_commands.command(name="nivel", description="Muestra el nivel y la experiencia faltante para el siguiente nivel")
    @app_commands.describe(usuario="Usuario del que ver el nivel (opcional)")
    async def nivel(self, interaction: discord.Interaction, usuario: discord.User = None):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker

        if await self.checker.check_guild(interaction=interaction) == False:
            return
        
        # Make the interacter user as default
        if usuario is None:
            usuario = interaction.user
        
        # Get the data for the embed color
        user_data = await self.database.get_user_data(user_id=usuario.id)
        
        # Check if the user can level up to evade visual problems (like have more xp than needed to lvl up, visual error)
        giver = self.bot.get_cog("GiveRewards") # type: GiveRewards
        previous_level = user_data['level']
        user_data = await giver.check_level_up(data=user_data)
        
        # Checks if the user has leveled up and save the data
        if user_data['level'] > previous_level:
            await interaction.channel.send(f"¡<@{interaction.user.id}>, has subido al nivel {user_data['level']}!")
        
        # Parse the data to show in the embed
        experience = user_data['experience']
        level = user_data['level']
        xp_req = 100 + level * 20
        xp_left = xp_req - experience

        user_aspect = user_data['aspect']
        aspects = await self.database.get_aspects()        
        aspect_data = next((aspect for aspect in aspects if aspect['name'] == user_aspect), None)
        color = discord.Color(int(aspect_data.get('color', "#000000")[1:], 16))
        embed = discord.Embed(title=f"Nivel de {usuario.name}", colour=color)
        try:
            avatar_url = usuario.avatar.url
        except AttributeError:
            avatar_url = 'assets/images/defaultAvatar.png'
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Nivel", value=f"{level}", inline=False)
        embed.add_field(name="Experiencia actual", value=f"{experience}/{xp_req}", inline=False)
        embed.add_field(name="Experiencia faltante", value=f"{xp_left} XP", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=False)
        
        # ? I need to remember why I wrote this line
        cuser_data = user_data.copy()
        await self.database.save_user_data(user_id=usuario.id, data=cuser_data)

async def setup(bot):
    await bot.add_cog(Nivel(bot))