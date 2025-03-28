# TODO rework, by views like aspects or shop

import discord
from discord.ext import commands

class Comandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.comandos_disponibles = []
        
        @bot.tree.command(name="comandos", description="Lista todos los comandos disponibles.")
        async def comandos(interaction: discord.Interaction):
            
            # Get all commands from tree
            for command in bot.tree.get_commands():
                
                # If admin it's on the description, skip it
                if "admin" not in command.description.lower():
                    self.comandos_disponibles.append(f"/{command.name}: {command.description}")

            # Create embed with command list
            embed = discord.Embed(
                title="Comandos Disponibles",
                description="Aquí están todos los comandos que puedes usar:",
                color=discord.Color.green()
            )

            # Add all commands to the embed
            embed.add_field(name="Comandos Slash", value="\n".join(self.comandos_disponibles), inline=False)

            # Enviar el embed al canal
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Comandos(bot))




















