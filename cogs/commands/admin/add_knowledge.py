import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase

class AddKnowledge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
    
    @app_commands.command(name="addknowledge", description="Añade una cantidad de Knowledge al usuario indicado (admin)")
    @app_commands.default_permissions(administrator=True)
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def add_knowledge(self, interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        await interaction.response.defer(thinking=True, ephemeral=True)

        if cantidad <= 0:
            await interaction.followup.send("No puedes poner un número inferior a 1.", ephemeral=True)
            return

        if not await self.database.increment_knowledge(usuario.id, cantidad):
            await interaction.followup.send("Error añadiendo knowledge (mira la consola).", ephemeral=True)
            return
        
        await interaction.followup.send(f"{cantidad}<:knowledge:1338469359906979874> añadidos al usuario {usuario.name}", ephemeral=True)
        try:
            mensaje = f"Se te ha añadido {cantidad}<:knowledge:1338469359906979874>" if cantidad == 1 else f"Se te han añadido {cantidad}<:knowledge:1338469359906979874>"
            await usuario.send(mensaje)
        except discord.Forbidden:
            print(f"No se pudo enviar DM a {usuario.name}.")

async def setup(bot):
    await bot.add_cog(AddKnowledge(bot))
