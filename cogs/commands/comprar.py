import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from datetime import datetime
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild

class Comprar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
        self.checker: CheckGuild = None

    @app_commands.command(name="comprar", description="Compra un objeto de la tienda")
    @app_commands.describe(objeto="Nombre del objeto")
    @app_commands.describe(cantidad="Cuantos quieres comprar")
    async def comprar(self, interaction: discord.Interaction, objeto: str, cantidad: int):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker
        await interaction.response.defer(thinking=True, ephemeral=False)

        if await self.checker.check_guild(interaction=interaction) == False:
            return
        
        items = await self.database.get_items()
        matched_item = next((item for item in items if item['name'] == objeto), None)

        if matched_item and not matched_item['shop_item'] or not matched_item:
            await interaction.followup.send("No puedes comprar objetos no disponibles.")
            return

        if cantidad <= 0:
            await interaction.followup.send("No puedes comprar unidades inferiores a 1.")
            return
        
        # Check if it's affordable
        total_cost = matched_item['cost'] * cantidad
        user_data = await self.database.get_user_data(user_id=interaction.user.id)
        if total_cost > user_data['knowledge']:
            await interaction.followup.send("No tienes suficiente <:knowledge:1338469359906979874> para comprar este objeto.")
            return

        if not await self.database.decrease_knowledge(user_id=interaction.user.id, knowledge=total_cost):
            await interaction.followup.send(f"No se ha podido restar tu saldo, avisa a un desarrollador porfavor.")
            return

        if not await self.database.add_item_user(interaction.user.id, objeto, cantidad):
            await interaction.followup.send(f"El objeto no existe u ocurrió un error inesperado.")
            return
        
        message = None
        if cantidad <= 1:
            message = f"Has comprado {objeto}."
        else:
            message = f"Has comprado {cantidad} {objeto}."
        
        await interaction.followup.send(message)
    
    @comprar.autocomplete('objeto')
    async def item_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        items = await self.database.get_items()
        shop_items = [item for item in items if item['shop_item']]
        return [
            app_commands.Choice(name=x, value=x)
            for x in [x["name"] for x in shop_items] if str.startswith(x.lower(), current.lower())
        ]

async def setup(bot):
    await bot.add_cog(Comprar(bot))