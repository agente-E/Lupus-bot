import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase

class AddNotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
    
    @app_commands.command(name="addnotes", description="Añade una cantidad de Notas al usuario indicado (admin)")
    @app_commands.default_permissions(administrator=True)
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def add_notes(self, interaction:discord.Interaction, usuario: discord.Member, cantidad: int):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        await interaction.response.defer(thinking=True, ephemeral=True)

        if cantidad <= 0:
            await interaction.followup.send("No puedes poner un número inferior a 1.")
            return

        if not await self.database.increment_notes(usuario.id, cantidad):
            await interaction.followup.send(f"Error añadiendo notas (mira la consola).")
            return

        await interaction.followup.send(f"{cantidad}<:note:1338471019702259763> añadidos al usuario {usuario.name}", ephemeral=True)
        try:
            message = None
            if cantidad <= 1:
                message = f"Se te ha añadido {cantidad}<:note:1338471019702259763>"
            else:
                message = f"Se te han añadido {cantidad}<:note:1338471019702259763>"
            await usuario.send(message)
        except discord.Forbidden:
            print(f"No se pudo enviar DM a {usuario.name}.")

async def setup(bot):
    await bot.add_cog(AddNotes(bot))
