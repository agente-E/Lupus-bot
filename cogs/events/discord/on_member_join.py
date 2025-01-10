# Cuando un usuario se une al servidor
@bot.event
async def on_member_join(member):
    # Crea el embed de bienvenida
    embed = discord.Embed(
        title="¡Bienvenido al servidor!",
        description=f"¡Hola {member.mention}! Estamos encantados de que te hayas unido a nuestra comunidad. Aquí tienes una guía para empezar:",
        color=discord.Color.green()  # Puedes elegir cualquier color
    )
    # Agregar campos al embed (personaliza como desees)
    embed.add_field(
        name="1️⃣ Reglas del servidor",
        value="Lee nuestras reglas para asegurarte de que todos creamos un buen lugar de convivencia. https://discord.com/channels/776247434384375818/777160475158511627",
        inline=False
    )
    embed.add_field(
        name="2️⃣ Presentación",
        value="¡Nos encantaría conocerte! No dudes en hablar con la comunidad por sus canales correspondidos.",
        inline=False
    )
    embed.add_field(
        name="3️⃣ Comandos útiles",
        value="Usa el comando `/roll` para realizar tiradas y obtener recompensas, desde experiencia, permisos en el servidor y roles de decoración.",
        inline=False
    )
    embed.add_field(
        name="4️⃣ Preguntas",
        value="Si tienes alguna pregunta, no dudes en preguntar en el canal de ayuda o contactar a alguno de los helpers.",
        inline=False
    )
    embed.add_field(
        name="5️⃣ Invitación",
        value=(
            "Si quieres invitar a alguien al servidor, puedes copiarlo en el canal:\n"
            "https://discord.com/channels/776247434384375818/860630677489319936"
        ),
        inline=False
    )
    embed.add_field(
    name="🔧 ¿Cómo funciona el servidor?",
    value=(
        "Cada canal tiene una función específica y estará disponible desde el momento en que entres al servidor. "
        "El servidor cuenta con su propia mecánica para ciertas acciones, como enviar imágenes, usar sonidos en llamadas y realizar tiradas. "
        "Para hacer una tirada, deberás usar el comando `/roll`. Puedes hacer una tirada gratis cada 10 minutos, "
        "pero si necesitas más, puedes gastar *echoes* para realizar tiradas adicionales.\n\n"
        
        "*¿Cómo consigo echoes?*\n"
        "Fácil: siendo activo en el servidor. "
        "Obtendrás *echoes* de manera pasiva al enviar mensajes cada minuto y al pasar tiempo en llamadas de voz. "
        "Además, ganarás experiencia, que por ahora no tiene otro uso más que mostrar tu nivel de actividad en la comunidad."
    ),
    inline=False
    )
    # Enviar el mensaje embed al DM del nuevo miembro
    try:
        dm_channel = await member.create_dm()
        await dm_channel.send(embed=embed)
    except discord.Forbidden:
        print(f"No se pudieron enviar los DMs a {member.name}. El usuario tiene bloqueados los DMs.")
    try:
        # Asignar el rol al nuevo miembro
        rol_name = "Usuario"  # Cambia esto por el nombre del rol que deseas asignar
        announcement_role = "Anuncios"
        guild = member.guild
        # Busca el rol por nombre
        role = discord.utils.get(guild.roles, name=rol_name)
        role2 = discord.utils.get(guild.roles, name=announcement_role)
        # Si el rol existe, asignarlo al miembro
        if role:
            await member.add_roles(role)
            print(f"Rol {rol_name} asignado a {member.name}")
        else:
            print(f"Rol {rol_name} no encontrado en el servidor.")
        if role2:
            await member.add_roles(role2)
            print(f"Rol {rol_name} asignado a {member.name}")
        else:
            print(f"Rol {rol_name} no encontrado en el servidor.")
        # Obtener el canal de bienvenida
        channel = bot.get_channel(CHANNEL_WELCOME)
        if channel is None:
            raise ValueError("Canal de bienvenida no encontrado")
        # Crear y enviar la imagen de bienvenida
        welcome_image = await create_welcome_image(member)
        await channel.send(file=discord.File(welcome_image, filename='welcome.png'))
    except Exception as e:
        print(f"Error en on_member_join: {e}")
    user_id = str(member.id)  # Convertimos la ID del miembro a string para hacer la búsqueda
    # Obtener los datos del usuario desde el archivo JSON
    user_data = get_user_data(user_id)
    # Comprobar si el usuario tiene roles obtenidos
    roles_obtenidos = user_data.get('roles_obtenidos', [])
    # Si el usuario tiene roles obtenidos, asignarlos
    if roles_obtenidos:
        roles = []
        for role_name in roles_obtenidos:
            # Busca el rol en el servidor por nombre (asegúrate de que el rol existe)
            role = discord.utils.get(member.guild.roles, name=role_name)
            if role:
                roles.append(role)
        
        # Si se encuentran roles, asignarlos al miembro
        if roles:
            await member.add_roles(*roles)
            print(f"Se asignaron los roles a {member.name}: {', '.join(role.name for role in roles)}")