import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild
from cogs.utils.gacha.give_rewards import GiveRewards

class Nivel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="nivel", description="Muestra el nivel y la experiencia faltante para el siguiente nivel")
    async def nivel(self, interaction: discord.Interaction, user: discord.User = None):

        # Don't permit to use the bot out the main server
        checker = self.bot.get_cog("CheckGuild") # type: CheckGuild
        if await checker.check_guild(interaction=interaction) == False:
            return
        
        # Make the interacter user as default
        if user is None:
            user = interaction.user
        
        # Get the data of the user
        database = self.bot.get_cog("InteractWithDatabase") # type: InteractWithDatabase
        
        # Get the data for the inventory color
        user_data = await database.get_user_data(user_id=user.id)
        user_aspect = user_data['aspect']
        
        # Check if the user can level up to evade visual problems (like have more xp than needed to lvl up, visual error)
        # Also save the updated data
        giver = self.bot.get_cog("GiveRewards") # type: GiveRewards
        previous_level = user_data['level']
        user_data = await giver.check_level_up(data=user_data)
        database.save_user_data(user_id=user.id, data=user_data)
        # Checks if the user has leveled up
        if user_data['level'] > previous_level:
            await interaction.channel.send(f"¡<@{interaction.user.id}>, has subido al nivel {user_data['level']}!")
        experience = user_data['experience']
        level = user_data['level']
        xp_req = 100 + level * 20
        xp_left = xp_req - experience
        aspects = database.get_aspects()
        
        aspect_data = next((aspect for aspect in aspects if aspect['name'] == user_aspect), None)
        color = discord.Color(int(aspect_data.get('color', "#000000")[1:], 16))

        embed = discord.Embed(title=f"Nivel de {user.name}", colour=color)
        embed.add_field(name="Nivel", value=f"{level}", inline=False)
        embed.add_field(name="Experiencia actual", value=f"{experience}/{xp_req}", inline=False)
        embed.add_field(name="Experiencia faltante", value=f"{xp_left} XP", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Nivel(bot))