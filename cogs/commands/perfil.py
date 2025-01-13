import discord
import discord
from discord.ext import commands
from cogs.utils.gacha.get_user_data import getUserData


class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_user_data_cog = getUserData(bot)

        @bot.tree.command(name="perfil", description="Consulta el perfil de un usuario.")
        async def perfil(interaction: discord.Interaction, user: discord.User = None):
            # Si no se pasa un usuario, se usa el que ejecutó el comando
            if user is None:
                user = interaction.user
            user_id = str(user.id)
            user_data = self.get_user_data_cog.get_user_data(user_id)
            await interaction.response.defer()

            # Convertir el timestamp de la última tirada a una fecha y hora legible
            last_gacha_timestamp = user_data['last_gacha']
            if last_gacha_timestamp > 0:
                # Crear una marca de tiempo relativa usando el formato de Discord
                last_gacha_str = f"<t:{int(last_gacha_timestamp)}:R>"  # Formato relativo ("hace X minutos")
                print(last_gacha_str)
            else:
                last_gacha_str = "Nunca"

            # Obtener los roles obtenidos y sus probabilidades
            roles_obtenidos = user_data.get("Roles", [])
            roles_str = ""
            
            # Crear un diccionario con las probabilidades de cada recompensa
            # probabilidad_roles = {recompensa["item"]: recompensa["probabilidad"] for recompensa in tabla_recompensas if recompensa["tipo"] == "Roles"}

            # Crear una lista de tuplas (rol, probabilidad) y ordenarla
            # roles_con_probabilidad = [
            #     (rol, probabilidad_roles.get(rol, "Desconocida"))
            #     for rol in roles_obtenidos
            # ]
            
            # Ordenar los roles por probabilidad (en orden descendente)
            # roles_con_probabilidad.sort(key=lambda x: x[1] if x[1] != "Desconocida" else 0, reverse=True)

            # # Crear la cadena de roles con sus probabilidades
            # for rol, probabilidad in roles_con_probabilidad:
            #     if probabilidad != "Desconocida":
            #         # Usamos la función `get_percent_string` para calcular el porcentaje
            #         probabilidad_porcentaje = get_percent_string(probabilidad)
            #     else:
            #         probabilidad_porcentaje = "Desconocida"
                
            #     roles_str += f"{rol} - {probabilidad_porcentaje}%\n"

            if not roles_str:
                roles_str = "No ha obtenido ningún rol todavía."

            # Crear el embed
            embed = discord.Embed(title=f"Perfil de {user.name}", color=discord.Color.blue())
            embed.set_thumbnail(url=user.avatar.url)  # Avatar del usuario
            embed.add_field(name="Echoes", value=str(user_data['echoes']), inline=True)
            embed.add_field(name="Experiencia", value=str(user_data['experiencie']), inline=True)
            embed.add_field(name="Nivel", value=str(user_data['Level']), inline=True)
            embed.add_field(name="Pity Counter", value=str(user_data['Pity counter']), inline=True)
            embed.add_field(name="Última tirada", value=last_gacha_str, inline=True)
            embed.add_field(name="Fecha de creación de cuenta", value=user.created_at.strftime("%m-%d-%Y"), inline=True)
            embed.add_field(name="Roles Obtenidos", value=roles_str, inline=False)

            # Enviar el embed con la respuesta
            await interaction.followup.send(embed=embed)
async def setup(bot):
    await bot.add_cog(Perfil(bot))