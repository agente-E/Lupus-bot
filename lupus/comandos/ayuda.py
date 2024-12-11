import discord
from discord.ext import commands

class ComandosAyuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Guardamos la instancia del bot

    @discord.app_commands.command(name="ayuda", description="Lista todos los comandos disponibles.")
    async def comandos(self, interaction: discord.Interaction):
        # Obtener todos los comandos registrados en el bot
        comandos_disponibles = []

        # Usamos self.bot.tree.get_commands() para obtener los comandos registrados con /
        for command in self.bot.tree.get_commands():
            comandos_disponibles.append(f"/{command.name}: {command.description}")

        # Crear un embed con la lista de comandos
        embed = discord.Embed(
            title="Comandos Disponibles",
            description="Aquí están todos los comandos que puedes usar:",
            color=discord.Color.green()
        )

        # Añadir todos los comandos al embed
        embed.add_field(name="Comandos Slash", value="\n".join(comandos_disponibles), inline=False)

        # Enviar el embed al canal
        await interaction.response.send_message(embed=embed)

# Función de configuración para cargar el cog
async def setup(bot):
    await bot.add_cog(ComandosAyuda(bot))
