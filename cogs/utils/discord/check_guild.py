import discord
from discord.ext import commands

class CheckGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def check_guild(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("No puedes usar este comando aquí. Por favor, usa un canal del servidor https://discord.com/channels/776247434384375818/1312478372357603399.")
            return False

async def setup(bot):
    await bot.add_cog(CheckGuild(bot))