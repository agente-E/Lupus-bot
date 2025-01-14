import discord
import discord
from discord.ext import commands
from cogs.utils.gacha.get_user_data import getUserData
from cogs.utils.gacha.get_percent_string import gerPercentString


class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_user_data_cog = getUserData(bot)
        self.get_percent_string_cog = gerPercentString

        @bot.tree.command(name="perfil", description="Consulta el perfil de un usuario.")
        async def perfil(interaction: discord.Interaction, user: discord.User = None):
            # Si no se pasa un usuario, se usa el que ejecutó el comando
            if user is None:
                user = interaction.user
            user_id = str(user.id)
            user_data = self.get_user_data_cog.get_user_data(user_id)
            await interaction.response.defer()
            last_gacha_timestamp = user_data['Last Gacha']
            if last_gacha_timestamp > 0:
                # Crear una marca de tiempo relativa usando el formato de Discord
                last_gacha_str = f"<t:{int(last_gacha_timestamp)}:R>"
                print(last_gacha_str)
            else:
                last_gacha_str = "Nunca"
            # Obtener los roles y las probabilidades desde user_data
            obtained_roles = user_data.get("Roles", "").split(", ")
            roles_probability = list(map(float, user_data.get("Role probability", "").split(", ")))
            roles_probability_parsed = [
                self.get_percent_string_cog.get_percent_string(probability) for probability in roles_probability
            ]
            roles_with_probabilities = list(zip(obtained_roles, roles_probability_parsed))

            sorted_roles_with_probabilities = sorted(roles_with_probabilities, key=lambda x: x[1], reverse=True)

            # Construcción de la cadena ordenada
            roles_str = ""
            for role, prob in sorted_roles_with_probabilities:
                roles_str += f"{role} - {prob}%\n"


            # Si no hay roles, establecer el mensaje predeterminado
            if not roles_str:
                roles_str = "No ha obtenido ningún rol todavía."

            # Crear el embed
            embed = discord.Embed(title=f"Perfil de {user.name}", color=discord.Color.blue())
            embed.set_thumbnail(url=user.avatar.url)  # Avatar del usuario
            embed.add_field(name="Echoes", value=str(user_data['Echoes']), inline=True)
            embed.add_field(name="Experiencia", value=str(user_data['Experience']), inline=True)
            embed.add_field(name="Nivel", value=str(user_data['Level']), inline=True)
            embed.add_field(name="Pity Counter", value=str(user_data['Pity Counter']), inline=True)
            embed.add_field(name="Última tirada", value=last_gacha_str, inline=True)
            embed.add_field(name="Fecha de creación de cuenta", value=user.created_at.strftime("%m-%d-%Y"), inline=True)
            embed.add_field(name="Roles Obtenidos", value=roles_str, inline=False)

            # Enviar el embed con la respuesta
            await interaction.followup.send(embed=embed)
async def setup(bot):
    await bot.add_cog(Perfil(bot))