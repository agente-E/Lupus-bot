import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
from cogs.utils.gacha.interact_with_data import InteractWithDatabase

class AddItems(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database: InteractWithDatabase = None

    @app_commands.command(name="additems", description="Añade items a un usuario (admin)")
    @app_commands.default_permissions(administrator=True)
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def command(self, interaction: discord.Interaction, usuario: discord.Member, item: str, cantidad: int):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        if cantidad <= 0:
            await interaction.response.edit_message("No puedes poner un número inferior a 1.")
            return

        if not await self.database.add_item_user(usuario.id, item, cantidad):
            await interaction.followup.send(f"Error añadiendo el item (mira la consola).")
            return
        
        message = None
        if cantidad <= 1:
            message = f"Se ha añadido el item {item} al usuario {usuario.name}."
        else:
            message = f"Se han añadido {cantidad} {item} al usuario {usuario.name}."
        await interaction.followup.send(message)

    @command.autocomplete('item')
    async def item_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        items = await self.database.get_items()
        return [
            app_commands.Choice(name=x, value=x)
            for x in [x["name"] for x in items] if str.startswith(x.lower(), current.lower())
        ]

async def setup(bot):
    await bot.add_cog(AddItems(bot))