import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from datetime import datetime
import math

ITEMS_PER_PAGE = 10

class RolePaginator(View):
    def __init__(self, user_data, interaction_user, timeout=60):
        super().__init__(timeout=timeout)
        self.user_data = sorted(user_data, key=lambda x: x["probability"])  # menor prob = más raro
        self.current_page = 0
        self.total_pages = math.ceil(len(self.user_data) / ITEMS_PER_PAGE)
        self.interaction_user = interaction_user

        self.prev_button = Button(label="⏪", style=discord.ButtonStyle.primary)
        self.next_button = Button(label="⏩", style=discord.ButtonStyle.primary)
        self.prev_button.callback = self.go_prev
        self.next_button.callback = self.go_next
        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    def get_page_items(self):
        start = self.current_page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        return self.user_data[start:end]

    def get_embed(self):
        embed = discord.Embed(
            title="🎖 Roles desbloqueados",
            description=f"Página {self.current_page + 1} de {self.total_pages}",
            color=discord.Color.gold()
        )
        roles_on_page = self.get_page_items()

        for role in roles_on_page:
            name = role["name"]
            probability = role["probability"]
            obtained = datetime.fromtimestamp(role["created"]).strftime("%d/%m/%Y %H:%M")
            embed.add_field(name=name, value=f"🎯 Prob: `{probability:.2f}%`\n📅 Obtenido: {obtained}", inline=False)

        return embed

    async def update_message(self, interaction):
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    async def go_prev(self, interaction: discord.Interaction):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("No puedes usar este menú.", ephemeral=True)
            return

        self.current_page = (self.current_page - 1) % self.total_pages
        await self.update_message(interaction)

    async def go_next(self, interaction: discord.Interaction):
        if interaction.user != self.interaction_user:
            await interaction.response.send_message("No puedes usar este menú.", ephemeral=True)
            return

        self.current_page = (self.current_page + 1) % self.total_pages
        await self.update_message(interaction)


class Titulos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = None
        self.checker = None

    @app_commands.command(name="titulos", description="Muestra los títulos desbloqueados de un usuario")
    @app_commands.describe(usuario="Usuario del que ver los roles (opcional)")
    async def unlocked_roles_command(self, interaction: discord.Interaction, usuario: discord.Member = None):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker

        if not await self.checker.check_guild(interaction=interaction):
            return

        usuario = usuario or interaction.user

        try:
            user_history = await self.database.get_user_history(usuario.id)
        except Exception as e:
            await interaction.response.send_message("❌ No se pudo obtener el historial del usuario.", ephemeral=True)
            print(f"Error al obtener historial: {e}")
            return

        if not user_history:
            await interaction.response.send_message("❌ Este usuario no tiene recompensas registradas.", ephemeral=True)
            return

        # Filtrar solo roles y expandir info
        role_unlocks = []
        for entry in user_history:
            reward = entry.get("reward")
            if reward and reward.get("type") == "Role":
                role_unlocks.append({
                    "name": reward.get("name"),
                    "probability": reward.get("probability", 0),
                    "created": entry.get("created", 0)
                })

        if not role_unlocks:
            await interaction.response.send_message("⚠️ Este usuario no ha desbloqueado roles.", ephemeral=True)
            return

        paginator = RolePaginator(role_unlocks, interaction.user)
        await interaction.response.send_message(embed=paginator.get_embed(), view=paginator)

async def setup(bot):
    await bot.add_cog(Titulos(bot))
