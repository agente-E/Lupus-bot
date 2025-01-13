import discord
import requests
from discord import app_commands
from discord.ext import commands
from cogs.utils.gacha.get_user_data import getUserData
from cogs.utils.gacha.save_user_data import saveUserData


class RmEchoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_user_data_cog = getUserData(bot)
        self.save_data_cog = saveUserData(bot)

        @bot.tree.command(name="rmechoes", description="Extrae una cantidad de echoes al usuario indicado admin")
        @app_commands.default_permissions(administrator=True)
        async def rmechoes(interaction:discord.Interaction, usuario: discord.Member, cantidad: int):
            user_id = str(usuario.id)
            user_data = self.get_user_data_cog.get_user_data(user_id)
            echoes = user_data['Echoes']
            echoes_to_sub = cantidad
            echoes -= echoes_to_sub
            user_data['echoes'] = cantidad
            self.save_data_cog.save_user_data(user_id, user_data)
            await interaction.response.send_message(f"{cantidad} extraidos al usuario {usuario.name}", ephemeral=True)
            try:
                await usuario.send(f"Se te han eliminado {cantidad} echoes")
            except discord.Forbidden:
                print(f"No se pudo enviar DM a {usuario.name}.")

async def setup(bot):
    await bot.add_cog(RmEchoes(bot))