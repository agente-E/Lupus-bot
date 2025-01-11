import discord
from discord.ext import commands

class getColor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # Get color by rarity
    def get_color(probabilidad):
        if probabilidad <= 0.0002:  # 1 in 5,000 or more
            return discord.Color.red()
        elif probabilidad <= 0.00067:  # 1 in 1,111
            return discord.Color.gold()
        elif probabilidad <= 0.001:  # 1 in 1,000
            return discord.Color.purple()
        elif probabilidad <= 0.002:  # 1 in 500
            return discord.Color.blue()
        else:  # more common than 1 in 500
            return discord.Color.green()
        
async def setup(bot):
    await bot.add_cog(getColor(bot))