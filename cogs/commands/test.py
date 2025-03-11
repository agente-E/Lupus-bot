import discord
from discord.ext import commands
from discord import app_commands

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        @bot.tree.command(name="test", description="test")
        async def test(interaction: discord.Interaction):
            # Fix: Correctly access the "gacha_cooldown" key
            gacha_cooldown = self.bot.config["gacha_settings"].get("gacha_cooldown")
            await interaction.response.send_message(gacha_cooldown)

async def setup(bot):
    await bot.add_cog(Test(bot))
