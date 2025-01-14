# TODO


# import discord
# from discord import app_commands
# from discord.ext import commands

# class Invite(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot      

#         @bot.tree.command(name="invite", description="Genera un mensaje de invite admin")
#         @app_commands.default_permissions(administrator=True)
#         async def invite(interaction: discord.Interaction):
#             invite_link = "https://discord.gg/7Kc8gGSub2"
#             image_path = "assets/images/Tinky_Winky.png"  # Imagen en el mismo directorio
            
#             Crear el embed con el formato y la imagen de cabecera
#             embed = discord.Embed(
#                 title="¡Invitación al servidor!",
#                 description=( 
#                     ".•° ✿ °•..•° ✿ °•..•° ✿ °•.\n"
#                     "¡Esta es la invitación del servidor! Con ella, puedes invitar a tus amigos y pasar un buen rato en esta comunidad basada en Deepwoken.\n"
#                     f"`{invite_link}`\n"
#                     ".•° ✿ °•..•° ✿ °•..•° ✿ °•."
#                 ),
#                 color=discord.Color.purple(),
#             )

#             Establecer la imagen de cabecera del embed
#             embed.set_thumbnail(url="attachment://Tinky_Winky.png")
            
#             try:
#                 Abrir y adjuntar la imagen como archivo
#                 with open(image_path, "rb") as image_file:
#                     file = discord.File(fp=image_file, filename="Tinky_Winky.png")
                    
#                     Enviar el mensaje con el embed y el archivo
#                     await interaction.response.send_message(embed=embed, file=file)
#             except FileNotFoundError:
#                 Si la imagen no se encuentra, enviamos un mensaje de error
#                 await interaction.response.send_message("No se pudo encontrar la imagen para la invitación. Por favor, revisa la ruta.", ephemeral=True,  # Solo visible para el administrador
#                 )

# async def setup(bot):
#     await bot.add_cog(Invite(bot))
