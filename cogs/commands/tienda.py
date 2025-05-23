import discord
from copy import deepcopy
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild

class Tienda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tienda", description="Muestra la tienda")
    async def inventario(self, interaction: discord.Interaction):
        
        # Don't permit to use the bot out the main server
        checker = self.bot.get_cog("CheckGuild") # type: CheckGuild
        if await checker.check_guild(interaction=interaction) == False:
            return
                
        database = self.bot.get_cog("InteractWithDatabase") # type: InteractWithDatabase
        user_data = await database.get_user_data(user_id=interaction.user.id)
        aspect = user_data['aspect']

        embed = discord.Embed(title="🛒 Tienda 🛒", description="Selecciona una categoría.", color=discord.Color.green())
        select_menu = Select(
        placeholder="Selecciona una categoría",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Perfil", description="Objetos de perfil", emoji="📄"),
            # discord.SelectOption(label="", description="", emoji="") for more options in future
        ]
    )
        
        async def select_callback(interaction: discord.Interaction):
            selection = select_menu.values[0]
            shop_items = await database.get_shop_items(category=selection)
            embed = discord.Embed(title="🛒 Tienda 🛒", color=discord.Color.blue())
            use_inline = len(shop_items) % 3 == 0
            counter = 0

            for item in shop_items:
                inline = use_inline and counter < 3
                embed.add_field(
                    name=f"**{item['name']}**",
                    value=f"{item['cost']} <:knowledge:1338469359906979874>",
                    inline=inline
                )
                counter = counter + 1 if use_inline else 0
                if use_inline and counter == 3:
                    counter = 0

            if aspect == "Khan":
                embed.set_footer(text="Usa /comprar [objeto] para comprar.\n\nPor ser Khan, los objetos cuestan un 30% menos\n\nSelecciona otra categoría para ver más opciones.")
            else:
                embed.set_footer(text="Usa /comprar [objeto] para comprar.\n\nSelecciona otra categoría para ver más opciones.")
            await interaction.response.edit_message(embed=embed, view=view)

        select_menu.callback = select_callback

        view = View()
        view.add_item(select_menu)

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Tienda(bot))