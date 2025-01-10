@bot.tree.command(name="ayuda", description="Lista todos los comandos disponibles.")
async def comandos(interaction: discord.Interaction):
    # Obtener todos los comandos registrados en el bot
    comandos_disponibles = []

    # Usamos bot.tree.get_commands() para obtener los comandos registrados
    for command in bot.tree.get_commands():
        # Filtramos los comandos de administrador. Esto depende de cómo los marques.
        # Si los comandos de admin tienen en su descripción "admin" o algún atributo especial, podemos filtrar.
        if "admin" not in command.description.lower():  # Filtro basado en la descripción
            comandos_disponibles.append(f"/{command.name}: {command.description}")

    # Crear un embed con la lista de comandos
    embed = discord.Embed(
        title="Comandos Disponibles",
        description="Aquí están todos los comandos que puedes usar:",
        color=discord.Color.green()
    )

    # Añadir todos los comandos al embed
    embed.add_field(name="Comandos Slash", value="\n".join(comandos_disponibles), inline=False)

    # Enviar el embed al canal
    await interaction.response.send_message(embed=embed)