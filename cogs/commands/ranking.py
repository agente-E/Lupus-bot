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

class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
        self.checker: CheckGuild = None

    @app_commands.command(name="ranking", description="Muestra el top de usuarios con más nivel en el servidor")
    async def ranking(self, interaction: discord.Interaction):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker

        if await self.checker.check_guild(interaction=interaction) == False:
            return

        ranking = await self.database.get_ranking()
        async def get_page(page: int):
            emb = discord.Embed(title="🏆 Ranking de Usuarios 🏆", color=discord.Color.purple())

            results_per_page = 10
            start = (page - 1) * results_per_page
            end = start + results_per_page
            current_page_users = ranking[start:end]

            for i, user in enumerate(current_page_users, start=start + 10):
                emb.add_field(
                    name=f"#{i} {user['username']}",
                    value=f"Nivel {user['level']}",
                    inline=False
                )

            total_pages = Pagination.compute_total_pages(len(ranking), results_per_page)
            emb.set_footer(text=f"Página {page} de {total_pages}")
            return emb, total_pages

        await Pagination(interaction, get_page).navegate()

async def setup(bot):
    await bot.add_cog(Ranking(bot))