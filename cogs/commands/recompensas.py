# import discord
# from copy import deepcopy
# from discord.ext import commands
# from discord import app_commands
# from discord.ui import Select, View
# from cogs.utils.gacha.interact_with_data import InteractWithDatabase
# from cogs.utils.discord.check_guild import CheckGuild

# class Recompensas(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.database: InteractWithDatabase = None
#         self.checker: CheckGuild = None
    
#     # TODO (Want to create a correct UI 😭)
#     @app_commands.command(name="recompensas", description="Muestra la tienda")
#     async def recompensas(self, interaction: discord.Interaction):
#         self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
#         self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker
        
#         if await self.checker.check_guild(interaction=interaction) == False:
#             return

#         embed = discord.Embed(title="🎁 Recompensas 🎁", description="Selecciona una categoría.", color=discord.Color.blue())
#         select_menu = Select(
#             placeholder="Selecciona una categoría",
#             options=[
#                 discord.SelectOption(label="Experiencia", value="experiencia"),
#                 discord.SelectOption(label="Recompensas Comunes", value="faciles"),
#                 discord.SelectOption(label="Recompensas Épicas", value="epicas"),
#                 discord.SelectOption(label="Recompensas Legendarias", value="raras"),
#                 discord.SelectOption(label="Recompensas de Pity", value="pity"),
#                 discord.SelectOption(label="Objetos", value="objeto")
#         ])

#         view = View()
#         view.add_item(select)

#         # Enviar el mensaje con el select menu
#         await interaction.response.send_message(
#             content="Selecciona una categoría para ver las recompensas.",
#             view=view
#         )

#         # Función que se ejecuta cuando se selecciona una opción
#         async def mostrar_recompensas(interaction: discord.Interaction):
#             await interaction.response.defer()  # Mantener la interacción activa

#             # Obtener la opción seleccionada
#             categoria = interaction.data["values"][0]  # Obtener la opción seleccionada desde la interacción

#             # Filtrar las recompensas según la categoría seleccionada
#             if categoria == "experiencia":
#                 recompensas = [r for r in tabla_recompensas if r["tipo"] == "Experiencia"]
#             elif categoria == "faciles":
#                 recompensas = [r for r in tabla_recompensas if r["tipo"] == "Roles" and r["probabilidad"] >= 0.0011223]
#             elif categoria == "epicas":
#                 recompensas = [r for r in tabla_recompensas if r["tipo"] == "Roles" and 0.00015312 <= r["probabilidad"] <= 0.00110111]
#             elif categoria == "raras":
#                 recompensas = [r for r in tabla_recompensas if r["tipo"] == "Roles" and r["probabilidad"] <= 0.00007]
#             elif categoria == "pity":
#                 recompensas = [r for r in tabla_recompensas if r["item"] in PITY_REWARDS]
#             elif categoria == "objeto":
#                 recompensas = [r for r in tabla_recompensas if r["tipo"] == "Objeto" and r["probabilidad"]]


#             # Ordenar las recompensas por probabilidad (de más fácil a más difícil)
#             recompensas.sort(key=lambda x: x["probabilidad"], reverse=True)

#             # Crear el embed
#             embed = discord.Embed(
#                 title="🎉 **Tabla de Recompensas y Probabilidades** 🎉",
#                 description="Aquí tienes las recompensas disponibles y sus probabilidades:",
#                 color=discord.Color.blue()
#             )

#             # Inicializamos el contador de fields y el embed
#             contador_fields = 0

#             # Añadir las recompensas al embed
#             for recompensa in recompensas:
#                 item = recompensa["item"]
#                 probabilidad = recompensa["probabilidad"]
#                 probabilidad_porcentaje = get_percent_string(probabilidad)

#                 # Comprobar si se debe crear un nuevo embed
#                 if contador_fields >= 25:
#                     # Enviar el embed actual y crear uno nuevo
#                     await interaction.followup.send(embed=embed)
#                     embed = discord.Embed(title="🎉 Recompensa 🎉", description="Aquí están las recompensas disponibles:",             color=discord.Color.blue())
#                     contador_fields = 0  # Reseteamos el contador

#                 # Añadir el nuevo campo al embed
#                 embed.add_field(
#                     name=f"**{item}**",
#                     value=f"Probabilidad de {probabilidad_porcentaje}%",
#                     inline=False
#                 )
#                 contador_fields += 1

#             # Enviar el último embed si hay alguno pendiente
#             if contador_fields > 0:
#                 await interaction.followup.send(embed=embed)


#         # Añadir el callback para el select menu
#         select.callback = mostrar_recompensas

# TODO
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from datetime import datetime
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild

class Recompensas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
        self.checker: CheckGuild = None

    @app_commands.command(name="recompensas", description="Muestra las recompensas disponibles")
    async def unlocked_roles_command(self, interaction: discord.Interaction):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker

        if await self.checker.check_guild(interaction=interaction) == False:
            return
        
        await interaction.response.defer()
        
        await interaction.response.send_message("Still working")

async def setup(bot):
    await bot.add_cog(Recompensas(bot))