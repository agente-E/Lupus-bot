import discord
import discord
from discord.ext import commands
from discord import Interaction
from cogs.utils.gacha.get_user_data import getUserData


class Nivel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_user_data_cog = getUserData(bot)

        @bot.tree.command(name="nivel", description="Consulta el nivel, experiencia actual y la cantidad de XP requerida para el siguiente nivel.")
        async def nivel(interaction: discord.Interaction, user: discord.User = None):
            # Si no se menciona un usuario, usar al que ejecutó el comando
            if user is None:
                user = interaction.user
            
            user_id = str(user.id)   
            user_data = self.get_user_data_cog.get_user_data(user_id)
            
            if user_data is None:
                await interaction.response.send_message(f"No se encontraron datos para el usuario {user.name}.", ephemeral=True)
                return   
            
            experiencia = user_data['Experience']
            print(experiencia)
            nivel = user_data['Level']
            xp_requerida = 100 + nivel * 20
            xp_faltante = xp_requerida - experiencia
            
            embed = discord.Embed(title=f"Nivel de {user.name}", color=discord.Color.green())
            embed.add_field(name="Nivel", value=f"{nivel}", inline=False)
            embed.add_field(name="Experiencia actual", value=f"{experiencia}/{xp_requerida}", inline=False)
            embed.add_field(name="Experiencia faltante", value=f"{xp_faltante} XP", inline=False)
            
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Nivel(bot))