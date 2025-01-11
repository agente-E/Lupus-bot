import discord
from discord.ext import commands

class gerPercentString(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_percent_string(weight) -> str:
        return (f"{weight * 100:.2f}" if weight * 100 >= 1 else f"{weight * 100:.7f}").rstrip('0').rstrip('.')

async def setup(bot):
    await bot.add_cog(gerPercentString(bot))