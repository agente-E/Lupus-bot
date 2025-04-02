import random
import discord
from discord import app_commands
from discord.ext import commands

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 776247434384375818
    @app_commands.command(name="roll", description="Realiza una tirada de gacha")
    async def roll(self, interaction: discord.Interaction):
        
        # Don't permit to use the bot out the main server
        if interaction.guild is None or interaction.guild.id == self.guild_id:
            await interaction.response.send_message("No puedes usar este comando aquí. Por favor, usa un canal del servidor https://discord.com/channels/776247434384375818/1312478372357603399.")
            return
        

# Add cog to the bot
async def setup(bot):
    await bot.add_cog(Roll(bot))
