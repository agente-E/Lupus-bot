import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild

class Inventario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
        self.checker: CheckGuild = None

    @app_commands.command(name="inventario", description="Muestra los objetos del inventario de un usuario")
    @app_commands.describe(usuario="Usuario del que ver el inventario (opcional)")
    async def inventario(self, interaction: discord.Interaction, usuario: discord.User = None):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker

        # Don't permit to use the bot out the main server
        if await self.checker.check_guild(interaction=interaction) == False:
            return

        # Make the interacter user as default
        if usuario is None:
            usuario = interaction.user

        # Get the data for the inventory color
        user_data = await self.database.get_user_data(user_id=usuario.id)
        user_aspect = user_data['aspect']
        
        # Get the colors from database
        aspects = await self.database.get_aspects()
        aspect_data = next((aspect for aspect in aspects if aspect['name'] == user_aspect), None)
        color = discord.Color(int(aspect_data.get('color', "#000000")[1:], 16))
        
        # Get the inventory of the user
        user_inventory = await self.database.get_user_inventory(user_id=usuario.id)
        embed = discord.Embed(
            title=f"Inventario de {usuario.name}",
            colour=color
        )
        try:
            avatar_url = usuario.avatar.url
        except AttributeError:
            avatar_url = 'https://images-ext-1.discordapp.net/external/9NmCvbrWMNfRMMT_d42ejZRNvj1rseRwMlyik_0Epqc/https/discord.com/assets/788f05731f8aa02e.png?format=webp&quality=lossless'
        embed.set_thumbnail(url=avatar_url)
        if not user_inventory :
            embed.add_field(name='Objetos en el Inventario', value='No tienes objetos en tu inventario')
        else:
            inventory_text = ""
            for entry in user_inventory:
                inventory_text += f"• {entry['item']}: {entry['quantity']}\n"
            embed.add_field(name="Objetos en Inventario", value=inventory_text, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Inventario(bot))