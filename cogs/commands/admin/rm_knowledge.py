import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase

class RmKnowledge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None

    @app_commands.command(name="rmknowledge", description="Elimina una cantidad de Knowledge al usuario indicado (admin)")
    @app_commands.default_permissions(administrator=True)
    @discord.app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(usuario="Usuario al que quitar Knowledge")
    @app_commands.describe(cantidad="Número de Knowledge a quitar")
    async def rm_knowledge(self, interaction:discord.Interaction, usuario: discord.Member, cantidad: int):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        await interaction.response.defer(thinking=True, ephemeral=True)

        if cantidad <= 0:
            await interaction.followup.send("No puedes poner un número inferior a 1.", ephemeral=True)
            return

        if not await self.database.decrease_knowledge(usuario.id, cantidad):
            await interaction.followup.send(f"Error eliminando knowledge (mira la consola).", ephemeral=True)
            return

        await interaction.followup.send(f"{cantidad}<:knowledge:1338469359906979874> extraidos al usuario {usuario.name}", ephemeral=True)
        try:
            message = None
            if cantidad <= 1:
                message = f"Se te han quitado {cantidad}<:knowledge:1338469359906979874>"
            else:
                message = f"Se te han quitado {cantidad}<:knowledge:1338469359906979874>"
            await usuario.send(message)
        except discord.Forbidden:
            print(f"No se pudo enviar DM a {usuario.name}.")

async def setup(bot):
    await bot.add_cog(RmKnowledge(bot))
