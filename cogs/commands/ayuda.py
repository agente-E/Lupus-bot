import discord
from discord.ext import commands
from discord import app_commands

class Ayuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Registrar el comando slash ayuda
        @bot.tree.command(name="ayuda", description="Lista todos los comandos disponibles.")
        async def ayuda(interaction: discord.Interaction):
            avalible_commands = []

            # Obtener todos los comandos registrados con bot.tree
            for command in bot.tree.get_commands():
                # Filtrar los comandos de administrador que tienen la palabra 'admin' en su descripción
                if "admin" not in command.description.lower():
                    avalible_commands.append(f"/{command.name}: {command.description}")

            # Crear un embed con la lista de comandos
            embed = discord.Embed(
                title="Comandos Disponibles",
                description="Aquí están todos los comandos que puedes usar:",
                color=discord.Color.green()
            )

            # Añadir todos los comandos al embed
            embed.add_field(name="Comandos", value="\n".join(avalible_commands), inline=False)

            # Enviar el mensaje con el embed
            await interaction.response.send_message(embed=embed)

# Cargar el cog
async def setup(bot):
    await bot.add_cog(Ayuda(bot))
