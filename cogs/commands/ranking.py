    # TODO (Want to create a correct UI 😭)
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from datetime import datetime
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild

class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
        self.checker: CheckGuild = None

    @app_commands.command(name="ranking", description="Muestra el top de usuarios con más nivel en el servidor")
    async def unlocked_roles_command(self, interaction: discord.Interaction):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker

        if await self.checker.check_guild(interaction=interaction) == False:
            return
        
        await interaction.response.defer()
        
        await interaction.response.send_message("Still working")
        

async def setup(bot):
    await bot.add_cog(Ranking(bot))