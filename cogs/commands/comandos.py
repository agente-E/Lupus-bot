# TODO rework, by views like aspects or shop
import discord
from discord import app_commands
from discord.ext import commands

class Comandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="comandos", description="Lista todos los comandos disponibles")
    async def comandos(self, interaction: discord.Interaction):
        avalible_commands = []

        # Get all commands from tree
        for command in self.bot.tree.get_commands():
            
            # If admin it's on the description, skip it
            if "admin" not in command.description.lower():
                avalible_commands.append(f"/{command.name}: {command.description}")

        # Create embed with command list
        embed = discord.Embed(
            title="Comandos Disponibles",
            description="Aquí están todos los comandos que puedes usar:",
            color=discord.Color.green()
        )          
                    
        # Add all commands to the embed
        embed.add_field(name="Comandos Slash", value="\n".join(avalible_commands), inline=False)
    
        # Send the embed to the channel
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Comandos(bot))