import discord
import discord
from discord.ext import commands
from cogs.utils.gacha.get_user_data import getUserData

class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_user_data_cog = getUserData(bot)

        @bot.tree.command(name="ranking", description="Consulta el ranking de usuarios con más nivel.")
        async def ranking(interaction: discord.Interaction):
            try:
                # Obtener los datos de los usuarios (ID y niveles)
                user_data = self.get_user_data_cog.get_users_levels()
                # Ordenar los usuarios por su nivel (de mayor a menor)
                sorted_data = sorted(user_data, key=lambda x: x["Level"], reverse=True)

                # Crear el embed para mostrar el ranking
                embed = discord.Embed(
                    title="🏆 Ranking de usuarios con más Nivel 🏆",
                    color=discord.Color.blurple()
                )

                for rank, user_info in enumerate(sorted_data[:10], 1):
                    user_id = user_info["ID"]
                    user = await bot.fetch_user(user_id)
                    embed.add_field(
                        name=f"#{rank} - {user.name}",
                        value=f"Nivel: {user_info['Level']}",
                        inline=False
                    )

                # Enviar el embed con la respuesta
                await interaction.response.send_message(embed=embed,)
            
            except Exception as e:
                # Manejo de errores
                await interaction.response.send_message(f"Hubo un error al obtener el ranking: {e}")

async def setup(bot):
    await bot.add_cog(Ranking(bot))