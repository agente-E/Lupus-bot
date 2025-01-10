# Evento al enviar un mensaje
@bot.event
async def on_message(message):
    global last_message
    url_pattern = r'https?://(?:www\.)?\S+'
    if message.author.bot:
        return
    # Verificar si el mensaje proviene de un canal de texto (es decir, no es un DM)
    if message.guild is None:  # Esto significa que el mensaje proviene de un DM
        # Enviar un mensaje al usuario informándole que no puede usar comandos en DMs
        await message.author.send("No puedes interactuar con el bot por md. Por favor, utiliza los canales del servidor para usar los comandos.")
        return  # Ignorar el resto del código para evitar que el comando se ejecute en un DM
    if re.search(url_pattern, message.content):
        roles = [role.name for role in message.author.roles]
        if "Permisos de imagen" not in roles:
            await message.delete()
            try:
                user_data = get_user_data(str(message.author.id))
                dm_channel = await message.author.create_dm()
                await dm_channel.send(f"Hola {message.author.name}, para poder enviar enlaces debes desbloquear el rol de **Permisos de imagen**. Este rol se consigue realizando el comando `/roll` en el canal [bots](https://discord.com/channels/776247434384375818/1312478372357603399).")
            except Exception as e:
                print(f"Error al enviar DM a {message.author.name}: {e}")
    current_time = time.time()
    user_id = str(message.author.id)
    if user_id not in user_last_message_time:
        user_last_message_time[user_id] = 0  
    if user_id in user_last_message_time:
        last_message_time = user_last_message_time[user_id]
        if current_time - last_message_time >= 60:
            user_last_message_time[user_id] = current_time
            user_data = get_user_data(user_id)
            booster_role_name = "Server Booster"
            if any(role.name == booster_role_name for role in message.author.roles):
                user_data['echoes'] += random.randint(15, 25)
                user_data['experiencia'] += random.randint(15, 25)
                user_data = await check_and_level_up(user_data, message=message)
                save_user_data(user_id, user_data)
            else:
                user_data['echoes'] += random.randint(1, 5)
                user_data['experiencia'] += random.randint(1, 5)
                user_data = await check_and_level_up(user_data, message=message)
                save_user_data(user_id, user_data)         
    if not check_for_updates.is_running():
        check_for_updates.start()
    allowed_channel = CHANNEL_DWU
    suggest_channel = CHANNEL_SUGGEST
    suggestions_channel = CHANNEL_SUGGESTIONS
    if message.channel.id == suggest_channel and message.content.startswith('.s '):
        if re.search(url_pattern, message.content):
            user = message.author  # Obtén el autor del mensaje
            try:
                # Envía un mensaje directo al usuario
                await user.send("No puedes enviar enlaces en las sugerencias")
            except discord.Forbidden:
                # Si el bot no puede enviar DM (por ejemplo, si el usuario tiene los DMs cerrados)
                print(f"No se pudo enviar DM a {user.name}.")
        else:
            # Elimina los primeros tres caracteres (".s ") del mensaje
            suggestion = message.content[3:].strip()
            # Obtén el canal donde se enviará la sugerencia
            suggestions_channel_obj = bot.get_channel(suggestions_channel)
            if suggestions_channel_obj:
                embed = discord.Embed(
                    title="💡 ¡Nueva Sugerencia Recibida! 💡",
                    color=discord.Color.green()  # Usamos azul para un tono profesional y atractivo
                )
                # Colocamos la sugerencia en un campo dedicado
                embed.add_field(
                    name="📝 Sugerencia:",
                    value=f"**__{suggestion}__**",
                    inline=False
                )
                # Imagen de autor como thumbnail para hacerlo más personal
                embed.set_thumbnail(url=message.author.avatar.url)
                # Personalizamos el autor para hacerlo más destacado
                embed.set_author(
                    name=f"💬 Sugerencia Propuesta por {message.author.name}"
                )
                # Envía el embed al canal de sugerencias
                suggestion_message = await suggestions_channel_obj.send(embed=embed)
                # Obtén los emotes personalizados usando sus IDs
                tinky = bot.get_emoji(1295755914862923837)
                emery = bot.get_emoji(1295755990544941127)
                if tinky and emery:
                    # Agrega las reacciones usando los objetos de los emotes
                    await suggestion_message.add_reaction(tinky)  # Pulgar arriba
                    await suggestion_message.add_reaction(emery)  # Pulgar abajo
                else:
                    print("No se pudieron encontrar los emotes personalizados.")
                try:
                    dm_embed = discord.Embed(
                        title="Gracias por tu sugerencia",
                        description=f"Tu sugerencia fue enviada con éxito:\n\n{suggestion}",
                        color=discord.Color.green()
                    )
                    dm_embed.set_footer(text="Los usuarios valorarán tu sugerencia.")
                    await message.author.send(embed=dm_embed)
                except discord.Forbidden:
                    # Si el usuario tiene los DMs desactivados, envía un mensaje al canal como alternativa
                    await message.channel.send(
                        f"No pude enviarte un mensaje directo, pero tu sugerencia fue enviada, {message.author.mention}."
                    )
                await message.delete()
        # Evita que otros comandos se procesen en este mensaje
    elif message.channel.id == suggest_channel and not message.content.startswith('.s '):
        print(f"El mensaje de {message.author} no comienza con '.s ' en el canal {message.channel.name}")
        await message.delete()  # Elimina el mensaje enviado
        user = message.author  # Obtén el autor del mensaje
        try:
            # Envía un mensaje directo al usuario
            await user.send("Para hacer una sugerencia, por favor usa el prefijo `s. ` seguido de tu sugerencia.\nEjemplo: `s. Tu sugerencia aquí`")
        except discord.Forbidden:
            # Si el bot no puede enviar DM (por ejemplo, si el usuario tiene los DMs cerrados)
            print(f"No se pudo enviar DM a {user.name}.")

    if message.channel.id != allowed_channel:
        return
    last_message = message.created_at
    print(f"Mensaje procesado en canal permitido: {message.channel.name}")
    await bot.process_commands(message)