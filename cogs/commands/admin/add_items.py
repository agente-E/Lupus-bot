import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild

class AddItems(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: InteractWithDatabase = None

    @app_commands.command(name="additems", description="Añade items a un usuario (admin)")
    @app_commands.default_permissions(administrator=True)
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def command(self, interaction: discord.Interaction, member: discord.Member, item: str, quantity: int):
        self.db = self.bot.get_cog("InteractWithDatabase") if self.db is None else self.db

        await interaction.response.defer(thinking=True,ephemeral=True)

        if not await self.db.add_item_user(member.id, item, quantity):
            await interaction.followup.send(f"Error añadiendo el item")
            return
        
        await interaction.followup.send(f"Item {item} añadido a miembro {member.name}.")
    
    @command.autocomplete('item')
    async def item_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        self.db = self.bot.get_cog("InteractWithDatabase") if self.db is None else self.db

        items = await self.db.get_items()
        return [
            app_commands.Choice(name=x, value=x)
            for x in [x["name"] for x in items] if str.startswith(x.lower(), current.lower())
        ]

async def setup(bot):
    await bot.add_cog(AddItems(bot))