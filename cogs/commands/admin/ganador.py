@bot.tree.command(name="ganador", description="Selecciona a un ganador aleatorio que cumpla el requisito mínimo de nivel 5 admin")
@app_commands.default_permissions(administrator=True)
async def ganador(interaction: discord.Interaction):
    # ID del canal y mensaje donde se necesita la reacción
    channel_id = 1229485607915360306  # Reemplaza con el ID correcto del canal
    message_id = 1324443868535586907  # Reemplaza con el ID correcto del mensaje
    
    # Obtener el canal por ID
    channel = interaction.guild.get_channel(channel_id)
    if not channel:
        await interaction.response.send_message("No se pudo encontrar el canal especificado.", ephemeral=True)
        return

    try:
        # Intentamos obtener el mensaje
        message = await channel.fetch_message(message_id)
    except discord.errors.NotFound:
        await interaction.response.send_message("El mensaje con el ID proporcionado no se pudo encontrar.", ephemeral=True)
        return

    # 1. Obtener usuarios con nivel >= 5 del archivo JSON
    try:
        with open("users.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        await interaction.response.send_message("No se pudo cargar el archivo de usuarios.", ephemeral=True)
        return

    # Filtrar usuarios que cumplen el nivel mínimo
    eligible_users = [
        int(user_id) for user_id, user_data in data.items()
        if user_data.get("nivel", 0) >= 5
    ]
    
    if not eligible_users:
        await interaction.response.send_message("No hay usuarios con nivel 5 o más.", ephemeral=True)
        return

    # 2. Verificar cuáles de esos usuarios han reaccionado al mensaje con el emoji 🐐
    emoji = '🐐'
    reacted_users = []

    for reaction in message.reactions:
        if reaction.emoji == emoji:
            async for user in reaction.users():
                if user.id in eligible_users:
                    reacted_users.append(user)
    # Obtener los nombres de los usuarios elegibles
    eligible_user_names = [
        user_data["nombre"] for user_id, user_data in data.items()
        if int(user_id) in reacted_users
    ]

    print(f"Usuarios que cumplen nivel >= 5 y reaccionaron: {eligible_user_names}")

    # 3. Seleccionar al ganador entre los usuarios válidos
    if reacted_users:
        winner = random.choice(reacted_users)
        
        # Obtener el nivel del ganador
        winner_level = data.get(str(winner.id), {}).get("nivel", 0)

        # Crear un mensaje normal con el ping al ganador fuera del embed
        message = f"🎉El ganador del sorteo es {winner.mention}🎉"
        
        # Crear un embed para mostrar al ganador
        embed = discord.Embed(
            title="¡Ganador del sorteo!",
            description=f"Has sido seleccionado como el ganador del sorteo.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=winner.avatar.url)  # Agrega la foto de perfil del ganador como thumbnail
        embed.add_field(name="Nivel del ganador", value=str(winner_level), inline=False)  # Añadir nivel
        embed.set_footer(text="¡Felicidades al ganador! 🎉", icon_url=interaction.guild.icon.url)  # Agregar footer con imagen del servidor
        
        # Enviar el mensaje normal con el ping y luego el embed
        await interaction.response.send_message(content=message, embed=embed)
    else:
        await interaction.response.send_message("No hay usuarios que cumplan con los requisitos y hayan reaccionado al mensaje.")
