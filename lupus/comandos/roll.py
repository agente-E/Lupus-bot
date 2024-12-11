import discord
from discord.ext import commands

class ComandoRoll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Guardamos la instancia del bot

        @discord.app_commands.command(name="roll", description="Realiza una tirada de gacha y gana recompensas.")
        async def roll(interaction: discord.Interaction):
            user_id = str(interaction.user.id)
            user_data = get_user_data(user_id)  # Obtenemos los datos del usuario

            # Obtener el tiempo de la última tirada (timestamp)
            last_gacha = user_data.get('last_gacha', 0)
            current_time = int(time.time())  # Obtener el tiempo actual en segundos

            # Verificar si el usuario puede hacer una tirada gratuita
            if current_time - last_gacha >= HORA_EN_SEGUNDOS:
                # El usuario puede hacer la tirada gratuita
                user_data['last_gacha'] = current_time  # Actualizamos el tiempo de la última tirada
                save_user_data(user_id, user_data)  # Guardamos los datos después de la actualización

                # Realizar la tirada gratuita
                recompensa = await realizar_tirada_normal(user_data, interaction)  # Actualizamos también el pity_counter

                # Guardamos nuevamente los datos después de la tirada
                save_user_data(user_id, user_data)

                # Crear el embed con la recompensa
                embed = discord.Embed(
                    title=f"Tirada de Gacha de {interaction.user.name}",
                    description=f"{interaction.user.mention} ha realizado una tirada de gacha gratuita.",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Recompensa Obtenida", value=recompensa, inline=False)
                embed.add_field(name="Echoes Restantes", value=f"{user_data['echoes']} Echoes", inline=True)
                embed.add_field(name="Contador de Pity", value=f"{user_data['pity_counter']} / 60", inline=True)

                # Enviar el embed con la recompensa gratuita
                await interaction.response.send_message(embed=embed)
            else:
                # Si el usuario ya ha usado su tirada gratuita, informamos el tiempo restante
                time_left = HORA_EN_SEGUNDOS - (current_time - last_gacha)
                hours_left = time_left // 3600
                minutes_left = (time_left % 3600) // 60
                seconds_left = time_left % 60

                # Crear el mensaje informando sobre el tiempo restante
                embed = discord.Embed(
                    title="Tirada Gratuita",
                    description=f"{interaction.user.mention}, ya has utilizado tu tirada gratuita.\n"
                                f"Tiempo restante para la siguiente tirada gratuita: {hours_left}h {minutes_left}m {seconds_left}s",
                    color=discord.Color.red()
                )

                # Crear los botones para gastar echoes
                button_yes = Button(label="Gastar Echoes", style=discord.ButtonStyle.green)
                button_no = Button(label="Esperar", style=discord.ButtonStyle.red)

                # Crear una vista con los botones
                view = View(timeout=60)
                view.add_item(button_yes)
                view.add_item(button_no)

                async def on_gastar_echoes(interaction: discord.Interaction):
                    # Verificamos que el usuario que pulsa el botón es el que lo solicitó
                    if interaction.user.id != int(user_id):
                        await interaction.response.send_message("Este botón no es para ti.", ephemeral=True)
                        return

                    user_data = get_user_data(user_id)  # Obtener los datos del usuario

                    # Verificar si el usuario tiene suficientes echoes
                    if user_data['echoes'] < PRICE_PER_ROLL:
                        await interaction.response.send_message(f"{interaction.user.mention}, no tienes suficientes echoes para hacer la tirada.", ephemeral=True)
                        # Eliminar el mensaje original después de la interacción, incluso si no hay suficientes echoes
                        if interaction.message:
                            await interaction.message.delete()
                        return

                    # Descontar los echoes
                    user_data['echoes'] -= PRICE_PER_ROLL
                    save_user_data(user_id, user_data)

                    # Aquí es donde necesitas pasar tanto `user_data` como `interaction`
                    recompensa = await realizar_tirada_normal(user_data, interaction)  # Asegúrate de que esta línea use `await`

                    # Guardar los datos nuevamente después de la tirada
                    save_user_data(user_id, user_data)

                    # Crear el embed con la recompensa
                    embed = discord.Embed(
                        title=f"Tirada de Gacha de {interaction.user.name}",
                        description=f"{interaction.user.mention} ha realizado una tirada de gacha con Echoes.",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Recompensa Obtenida", value=recompensa, inline=False)
                    embed.add_field(name="Echoes Restantes", value=f"{user_data['echoes']} Echoes", inline=True)
                    embed.add_field(name="Contador de Pity", value=f"{user_data['pity_counter']} / 60", inline=True)

                    # Enviar el embed con la recompensa
                    await interaction.response.send_message(embed=embed)

                    # Eliminar el mensaje original después de la interacción
                    if interaction.message:
                        await interaction.message.delete()

                # Acción para el botón "Esperar"
                async def on_esperar(interaction: discord.Interaction):
                    # Verificamos que el usuario que pulsa el botón es el que lo solicitó
                    if interaction.user.id != int(user_id):
                        await interaction.response.send_message("Este botón no es para ti.", ephemeral=True)
                        return

                    await interaction.response.send_message(f"{interaction.user.mention}, puedes esperar a que pasen diez minutos para obtener otra tirada gratuita.", ephemeral=True)

                    # Eliminar el mensaje original después de la interacción
                    if interaction.message:
                        await interaction.message.delete()

                # Asociar las acciones a los botones
                button_yes.callback = on_gastar_echoes
                button_no.callback = on_esperar

                # Enviar el mensaje con los botones
                await interaction.response.send_message(embed=embed, view=view)

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
                if item["tipo"] == "Roles" and item["item"] in PITY_REWARDS:
                    rol = discord.utils.get(interaction.guild.roles, name=item["item"])
                    if rol:
                        await interaction.user.add_roles(rol)
                        print(f"Rol '{item['item']}' asignado a {interaction.user.name}")  # Mensaje de depuración
                    else:
                        print(f"Rol '{item['item']}' no encontrado.")  # Mensaje de depuración

                    # Añadimos el rol legendario a la lista de roles obtenidos
                    if item["item"] not in user_data['roles_obtenidos']:
                        user_data['roles_obtenidos'].append(item["item"])
                    else:
                        return await realizar_tirada_normal(user_data, interaction)  # Llamada recursiva
                    user_data['pity_counter'] = 0
                    save_user_data(user_data['id'], user_data)  # Guardamos los datos después de la asignación
                    return item["item"]  # Retornamos el rol legendario como recompensa

                # Si obtenemos un rol común
                if item["tipo"] == "Roles":
                    if item["item"] in user_data['roles_obtenidos']:
                        # Si ya tiene el rol, lo ignoramos y volvemos a tirar
                        return await realizar_tirada_normal(user_data, interaction)  # Llamada recursiva

                    # Asignar el rol al usuario
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
                return item["item"]
        # En caso improbable (pero seguro que algo se retornará)
        return "No deberías tener esto"        



    # Función de configuración para cargar el cog
async def setup(bot):
    await bot.add_cog(ComandoRoll(bot))