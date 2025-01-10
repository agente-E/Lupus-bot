# Función para realizar la tirada
async def realizar_tirada_normal(user_data, interaction):
    # Si el pity ya ha alcanzado el umbral, le damos la recompensa asegurada de PITY_REWARDS
    if all(PITY_REWARD in user_data['roles_obtenidos'] for PITY_REWARD in PITY_REWARDS):
        user_data['pity_counter'] = -1
    if user_data['pity_counter'] >= PITY_THRESHOLD:
        repeat = False    
        recompensa_pity = random.choice(PITY_REWARDS)  # Elegimos una recompensa aleatoria de la lista
        # Verificar si el usuario ya tiene esta recompensa
        while repeat is False:    
            if recompensa_pity not in user_data['roles_obtenidos']:
                # Buscar el rol en el servidor
                role = discord.utils.get(interaction.guild.roles, name=recompensa_pity)
                if role:
                    repeat = True
                    print(f"Recompensa de pity seleccionada: {recompensa_pity}")  # Mensaje de depuración
                    await interaction.user.add_roles(role)  # Asignamos el rol al usuario
                    print(f"Rol '{recompensa_pity}' asignado a {interaction.user.name}")  # Mensaje de depuración
                else:
                    print(f"Rol '{recompensa_pity}' no encontrado.")  # Mensaje de depuración
            else:
                recompensa_pity = random.choice(PITY_REWARDS)
        # Añadimos la recompensa a la lista de roles obtenidos del usuario
        user_data['roles_obtenidos'].append(recompensa_pity)
        # Reiniciar el contador de pity después de dar la recompensa
        user_data['pity_counter'] = 0  
        save_user_data(user_data['id'], user_data)  # Guardamos los datos después de asignar el rol
        return recompensa_pity  # Retornamos la recompensa obtenida

    # Caso en el que el pity no ha alcanzado el umbral
    # Tiramos por una recompensa aleatoria según la tabla de probabilidades
    total_probabilidad = sum(item["probabilidad"] for item in tabla_recompensas)
    tirada = random.uniform(0, total_probabilidad)
    acumulada = 0

    for item in tabla_recompensas:
        acumulada += item["probabilidad"]
        if tirada <= acumulada:
            # Si obtenemos un rol y el rol es uno de los de pity
            if item["tipo"] == "Roles" and item["item"] in PITY_REWARDS and item["item"] not in user_data['roles_obtenidos']:
                rol = discord.utils.get(interaction.guild.roles, name=item["item"])
                if rol:
                    await interaction.user.add_roles(rol)
                    print(f"Rol '{item['item']}' asignado a {interaction.user.name}")  # Mensaje de depuración
                    user_data['roles_obtenidos'].append(item["item"])
                else:
                    return await realizar_tirada_normal(user_data, interaction)
                user_data['pity_counter'] = 0
                save_user_data(user_data['id'], user_data)  # Guardamos los datos después de la asignación
                return item["item"]  # Retornamos el rol legendario como recompensa
            # Si obtenemos un rol común
            if item["tipo"] == "Roles":
                if item["item"] in user_data['roles_obtenidos']:
                    return await realizar_tirada_normal(user_data, interaction)  # Llamada recursiva
                rol = discord.utils.get(interaction.guild.roles, name=item["item"])
                if rol:
                    await interaction.user.add_roles(rol)
                    user_data['roles_obtenidos'].append(item["item"])  # Añadir el rol a la lista de roles obtenidos
                    print(f"Rol '{item['item']}' asignado a {interaction.user.name}")  # Mensaje de depuración
            if item["tipo"] == "Experiencia":
                user_data['experiencia'] += item['valor']
            # Incrementar el pity solo para recompensas que no sean de rol legendario
            if item["item"] not in PITY_REWARDS:
                user_data['pity_counter'] += 1  # Incrementamos el pity por cada tirada normal
            save_user_data(user_data['id'], user_data)  # Guardamos los datos después de la tirada
            await check_and_level_up(user_data, interaction=interaction)
            return item["item"]
    return "No deberías tener esto"