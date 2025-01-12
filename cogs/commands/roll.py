import discord
from discord.ext import commands
import time
from cogs.utils.gacha.get_user_data import getUserData
from cogs.utils.gacha.save_user_data import saveUserData
from cogs.utils.gacha.get_color import getColor

class getUserData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pb_url = 'http://localhost:8090'
        self.get_user_data_cog = getUserData(bot)
        self.save_data_cog = saveUserData(bot)
        self.get_color_cog = getColor(bot)

        @bot.tree.command(name="roll", description="Realiza una tirada de gacha y gana recompensas.")
        async def roll(interaction: discord.Interaction):
            if interaction.guild is None:
                await interaction.response.send_message("No puedes usar este comando en los DMs. Por favor, usa un canal del servidor.")
                return
            user_id = str(interaction.user.id)
            user_data = self.get_user_data_cog.get_user_data(user_id)

            # Obtener el tiempo de la última tirada (timestamp)
            last_gacha = user_data.get('Last gacha', 0)
            current_time = int(time.time())  # Obtener el tiempo actual en segundos

            # Verificar si el usuario puede hacer una tirada gratuita
            gacha_cooldown = int(self.bot.config.get(["channels"].get("gacha_cooldown")))
            if current_time - last_gacha >= gacha_cooldown:
                # El usuario puede hacer la tirada gratuita
                user_data['last_gacha'] = current_time  # Actualizamos el tiempo de la última tirada
                self.save_data_cog.save_user_data(user_id, user_data)

                # Realizar la tirada gratuita
                recompensa = await realizar_tirada_normal(user_data, interaction)  # Actualizamos también el pity_counter
                for item in tabla_recompensas:
                    if item['item'] == recompensa:  # Si el ítem obtenido coincide con el de la tabla
                        probabilidad_roll = item['probabilidad']  # Guardar la probabilidad del ítem
                color_embed = self.bot.get_color_cog.get_color(probabilidad_roll)
                # Guardamos nuevamente los datos después de la tirada
                # Esto hay que mirarlo
                self.save_data_cog.save_user_data(user_id, user_data)

                # Crear el embed con la recompensa
                embed = discord.Embed(
                    title=f"Tirada de Gacha de {interaction.user.name}",
                    description=f"{interaction.user.mention} ha realizado una tirada de gacha gratuita.",
                    color=color_embed
                )
                embed.add_field(name="Recompensa Obtenida", value=recompensa, inline=False)
                embed.add_field(name="Echoes Restantes", value=f"{user_data['echoes']} Echoes", inline=True)
                embed.add_field(name="Contador de Pity", value=f"{user_data['pity_counter']} / 60", inline=True)
                if recompensa in PITY_REWARDS:
                    embed.set_footer(text=("**¡Has obtenido una recompensa de Pity!**"))
                # Enviar el embed con la recompensa gratuita
                await interaction.response.send_message(embed=embed)
            else:
                # Si el usuario ya ha usado su tirada gratuita, informamos el tiempo restante
                time_left = GACHA_COOLDOWN - (current_time - last_gacha)
                hours_left = time_left // 3600
                minutes_left = (time_left % 3600) // 60
                seconds_left = time_left % 60

                # Crear el mensaje informando sobre el tiempo restante
                embed = discord.Embed(
                    title="Tirada Gratuita",
                    description=f"{interaction.user.mention}, ya has utilizado tu tirada gratuita.\n"
                                f"Tiempo restante para la siguiente tirada gratuita: {minutes_left}m {seconds_left}s",
                    color=discord.Color.red()
                )
                embed.add_field(name="Tienes:", value=f"{user_data['echoes']} Echoes", inline=True)


                # Crear los botones para gastar echoes
                button_gastar = Button(label=f"1 tirada: {PRICE_PER_ROLL} echoes", style=discord.ButtonStyle.green)
                button_gastar10 = Button(label=f"10 tiradas: {PRICE_PER_ROLL * 8} echoes", style=discord.ButtonStyle.blurple)

                # Crear una vista con los botones
                view = View(timeout=60)
                view.add_item(button_gastar)
                view.add_item(button_gastar10)

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
                    for item in tabla_recompensas:
                        if item['item'] == recompensa:  # Si el ítem obtenido coincide con el de la tabla
                            probabilidad_roll = item['probabilidad']  # Guardar la probabilidad del ítem
                    color_embed = obtener_color_por_probabilidad(probabilidad_roll)
                    # Guardar los datos nuevamente después de la tirada
                    save_user_data(user_id, user_data)

                    # Crear el embed con la recompensa
                    embed = discord.Embed(
                        title=f"Tirada de Gacha de {interaction.user.name}",
                        description=f"{interaction.user.mention} ha realizado una tirada de gacha con Echoes.",
                        color=color_embed
                    )
                    embed.add_field(name="Recompensa Obtenida", value=recompensa, inline=False)
                    embed.add_field(name="Echoes Restantes", value=f"{user_data['echoes']} Echoes", inline=True)
                    embed.add_field(name="Contador de Pity", value=f"{user_data['pity_counter']} / 60", inline=True)
                    if recompensa in PITY_REWARDS:
                        embed.set_footer(text=("**¡Has obtenido una recompensa de Pity!**"))

                    # Enviar el embed con la recompensa
                    await interaction.response.send_message(embed=embed)

                    # Eliminar el mensaje original después de la interacción
                    if interaction.message:
                        await interaction.message.delete()

                # Acción para el botón "Esperar"
                async def on_gastar_echoesx10(interaction: discord.Interaction):
                    recompensas_roll = []
                    probabilidades_roll = []
                    # Verificamos que el usuario que pulsa el botón es el que lo solicitó
                    if interaction.user.id != int(user_id):
                        await interaction.response.send_message("Este botón no es para ti.", ephemeral=True)
                        return

                    user_data = get_user_data(user_id)  # Obtener los datos del usuario

                    # Verificar si el usuario tiene suficientes echoes
                    if user_data['echoes'] < PRICE_PER_ROLL * 8:
                        await interaction.response.send_message(f"{interaction.user.mention}, no tienes suficientes echoes para hacer la tirada.", ephemeral=True)
                        # Eliminar el mensaje original después de la interacción, incluso si no hay suficientes echoes
                        if interaction.message:
                            await interaction.message.delete()
                        return

                    # Descontar los echoes
                    user_data['echoes'] -= PRICE_PER_ROLL * 8
                    save_user_data(user_id, user_data)

                    # Realizar 10 tiradas y almacenar los resultados
                    for i in range(10):
                        recompensa = await realizar_tirada_normal(user_data, interaction)
                        recompensas_roll.append(recompensa)  # Agregar la recompensa a la lista  # Asegúrate de que esta línea use `await`
                        # Buscar la probabilidad del ítem obtenido en la tabla de recompensas
                        for item in tabla_recompensas:
                            if item['item'] == recompensa:  # Si el ítem obtenido coincide con el de la tabla
                                probabilidades_roll.append(item['probabilidad'])  # Guardar su probabilidad
                    # Guardar los datos nuevamente después de la tirada
                    save_user_data(user_id, user_data)

                    recompensas_texto = "\n".join(recompensas_roll)
                    probabilidad_mas_rara = min(probabilidades_roll)
                    # Obtener el color según la probabilidad más rara
                    color_embed = obtener_color_por_probabilidad(probabilidad_mas_rara)
                    embed = discord.Embed(
                        title=f"Tirada de Gacha de {interaction.user.name}",
                        description=f"{interaction.user.mention} ha realizado una tirada de gacha con Echoes.",
                        color=color_embed
                    )
                    embed.add_field(name="Recompensas Obtenidas", value=recompensas_texto, inline=False)
                    embed.add_field(name="Echoes Restantes", value=f"{user_data['echoes']} Echoes", inline=True)
                    embed.add_field(name="Contador de Pity", value=f"{user_data['pity_counter']} / 60", inline=True)
                    for recompensa in recompensas_roll:
                        if recompensa in PITY_REWARDS:
                            embed.set_footer(text="¡Has obtenido una recompensa de Pity!")

                    # Enviar el embed con todas las recompensas
                    await interaction.response.send_message(embed=embed)


                    # Eliminar el mensaje original después de la interacción
                    if interaction.message:
                        await interaction.message.delete()

                # Asociar las acciones a los botones
                button_gastar.callback = on_gastar_echoes
                button_gastar10.callback = on_gastar_echoesx10

                # Enviar el mensaje con los botones
                await interaction.response.send_message(embed=embed, view=view)