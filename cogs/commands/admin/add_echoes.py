# @bot.tree.command(name="addechoes", description="Añade una cantidad de echoes al usuario indicado admin")
# @app_commands.default_permissions(administrator=True)
# async def addechoes(interaction:discord.Interaction, usuario: discord.Member, cantidad: int):
#     user_id = str(usuario.id)
#     user_data = get_user_data(user_id)
#     user_data['echoes'] += cantidad
#     save_user_data(user_id, user_data)
#     await interaction.response.send_message(f"{cantidad} añadidos al usuario {usuario.name}", ephemeral=True)
#     try:
#         if cantidad <= 1:
#             await usuario.send(f"Se te ha añadido {cantidad} echo")
#         else:
#             await usuario.send(f"Se te han añadido {cantidad} echoes")
#     except discord.Forbidden:
#         print(f"No se pudo enviar DM a {usuario.name}.")