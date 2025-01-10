@bot.tree.command(name="rmechoes", description="Extrae una cantidad de echoes al usuario indicado admin")
@app_commands.default_permissions(administrator=True)
async def rmechoes(interaction:discord.Interaction, usuario: discord.Member, cantidad: int):
    user_id = str(usuario.id)
    user_data = get_user_data(user_id)
    user_data['echoes'] -= cantidad
    save_user_data(user_id, user_data)
    await interaction.response.send_message(f"{cantidad} extraidos al usuario {usuario.name}", ephemeral=True)
    try:
        await usuario.send(f"Se te han eliminado {cantidad} echoes")
    except discord.Forbidden:
        print(f"No se pudo enviar DM a {usuario.name}.")
