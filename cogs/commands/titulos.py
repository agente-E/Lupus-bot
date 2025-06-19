import discord
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from datetime import datetime
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild
from typing import Callable, Optional

class Pagination(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, get_page: Callable):
        self.interaction = interaction
        self.get_page = get_page
        self.total_pages: Optional[int] = None
        self.index = 1
        super().__init__(timeout=100)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            embed = discord.Embed(
                description=f"Solo el autor del comando puede realizar esta acción.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False

    async def navegate(self):
        embed, self.total_pages = await self.get_page(self.index)
        if self.total_pages == 1:
            await self.interaction.response.send_message(embed=embed)
        elif self.total_pages > 1:
            self.update_buttons()
            await self.interaction.response.send_message(embed=embed, view=self)

    async def edit_page(self, interaction: discord.Interaction):
        embed, self.total_pages = await self.get_page(self.index)
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    def update_buttons(self):
        if self.index > self.total_pages // 2:
            self.children[2].emoji = "⏮️"
        else:
            self.children[2].emoji = "⏭️"
        self.children[0].disabled = self.index == 1
        self.children[1].disabled = self.index == self.total_pages

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.Button):
        self.index -= 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        self.index += 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple)
    async def end(self, interaction: discord.Interaction, button: discord.Button):
        if self.index <= self.total_pages//2:
            self.index = self.total_pages
        else:
            self.index = 1
        await self.edit_page(interaction)

    async def on_timeout(self):
        # remove buttons on timeout
        message = await self.interaction.original_response()
        await message.edit(view=None)

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        return ((total_results - 1) // results_per_page) + 1

class Titulos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
        self.checker: CheckGuild = None

    @app_commands.command(name="titulos", description="Muestra los titulos desbloqueados de un usuario")
    @app_commands.describe(usuario="Usuario del que ver los roles (opcional)")
    async def unlocked_roles_command(self, interaction: discord.Interaction, usuario: discord.Member = None):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker

        if await self.checker.check_guild(interaction=interaction) == False:
            return
        
        # Make the interacter user as default
        if usuario is None:
            usuario = interaction.user
        
        user_unlocks = await self.database.get_user_unlocks(interaction.user.id)
        user_unlocks.sort(key=lambda x: float(x['probability']), reverse=True)

        # Get the colors from database
        user_data = await self.database.get_user_data(interaction.user.id)
        user_aspect = user_data['aspect']
        aspects = await self.database.get_aspects()
        aspect_data = next((aspect for aspect in aspects if aspect['name'] == user_aspect), None)
        color = discord.Color(int(aspect_data.get('color', "#000000")[1:], 16))

        embed = discord.Embed(
            title="Titulos obtenidos",
            color=color
        )
        try:
            avatar_url = usuario.avatar.url
        except AttributeError:
            avatar_url = 'assets/images/defaultAvatar.png'
        embed.set_thumbnail(url=avatar_url)
        if not user_unlocks:
            embed.add_field(
                name="No tienes titulos obtenidos",
                value="Todavía no has obtenido ni un solo titulo. Para obtenerlos, realiza tiradas con `/roll`",
                inline=False
            )
            await interaction.response.send_message(embed=embed)
            return
        
        async def get_page(page: int):
            offset = (page - 1) * 10
            current_page_unlocks = user_unlocks[offset:offset + 10]

            embed = discord.Embed(
                title="Títulos obtenidos",
                color=color,
                description=""
            )

            for unlock in current_page_unlocks:
                embed.description += f"{unlock['name']} - `{unlock['probability']}%`\n"

            total_pages = Pagination.compute_total_pages(len(user_unlocks), 10)
            embed.set_footer(text=f"Página {page} de {total_pages}")
            embed.set_thumbnail(url=avatar_url)

            return embed, total_pages
        pagination = Pagination(interaction, get_page)
        await pagination.navegate()

async def setup(bot):
    await bot.add_cog(Titulos(bot))