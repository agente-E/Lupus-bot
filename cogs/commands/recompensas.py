# Comando para mostrar las recompensas según la selección
@bot.tree.command(name="recompensas", description="Muestra la tabla de recompensas y sus probabilidades.")
async def recompensas(interaction: discord.Interaction):
    # Crear opciones para el select menu
    opciones = [
        discord.SelectOption(label="Experiencia", value="experiencia"),
        discord.SelectOption(label="Recompensas normales", value="faciles"),
        discord.SelectOption(label="Recompensas legendarias", value="raras"),
        discord.SelectOption(label="Recompensas de Pity", value="pity")
    ]

    # Crear el select menu
    select = Select(placeholder="Selecciona una categoría", options=opciones)

    # Crear el view con el select
    view = View()
    view.add_item(select)

    # Enviar el mensaje con el select menu
    await interaction.response.send_message(
        content="Selecciona una categoría para ver las recompensas.",
        view=view
    )

    # Función que se ejecuta cuando se selecciona una opción
    async def mostrar_recompensas(interaction: discord.Interaction):
        await interaction.response.defer()  # Mantener la interacción activa

        # Obtener la opción seleccionada
        categoria = interaction.data["values"][0]  # Obtener la opción seleccionada desde la interacción

        # Filtrar las recompensas según la categoría seleccionada
        if categoria == "experiencia":
            recompensas = [r for r in tabla_recompensas if r["tipo"] == "Experiencia"]
        elif categoria == "faciles":
            recompensas = [r for r in tabla_recompensas if r["tipo"] == "Roles" and r["probabilidad"] >= 0.0012]
        elif categoria == "raras":
            recompensas = [r for r in tabla_recompensas if r["tipo"] == "Roles" and r["probabilidad"] <= 0.0011]
        elif categoria == "pity":
            # Filtrar las recompensas de Pity, usando la lista `PITY_REWARDS`
            recompensas = [r for r in tabla_recompensas if r["item"] in PITY_REWARDS]

        # Ordenar las recompensas por probabilidad (de más fácil a más difícil)
        recompensas.sort(key=lambda x: x["probabilidad"], reverse=True)

        # Crear el embed
        embed = discord.Embed(
            title="🎉 **Tabla de Recompensas y Probabilidades** 🎉",
            description="Aquí tienes las recompensas disponibles y sus probabilidades:",
            color=discord.Color.blue()
        )

        # Añadir las recompensas al embed
        for recompensa in recompensas:
            item = recompensa["item"]
            probabilidad = recompensa["probabilidad"]
            tiradas = round(1 / probabilidad)  # Redondear el número de tiradas
            embed.add_field(
                name=f"**{item}**",
                value=f"1 entre {tiradas} tiradas",
                inline=False
            )

        # Usar followup.send para enviar el embed
        await interaction.followup.send(embed=embed)

    # Añadir el callback para el select menu
    select.callback = mostrar_recompensas
