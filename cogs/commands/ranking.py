# Comando para mostrar el ranking de usuarios con más nivel
@bot.tree.command(name="ranking", description="Consulta el ranking de usuarios con más nivel.")
async def ranking(interaction: discord.Interaction):
    try:
        with open("users.json", "r") as file:
            data = json.load(file)
            sorted_data = sorted(data.items(), key=lambda item: item[1]['nivel'], reverse=True)
        embed = discord.Embed(title="🏆 Ranking de Niveles 🏆", color=discord.Color.purple())
        for rank, (user_id, user_info) in enumerate(sorted_data[:10], 1):
            user = await bot.fetch_user(user_id)
            embed.add_field(
                name=f"#{rank} - {user.name}",
                value=f"Nivel: {user_info['nivel']}",
                inline=False
            )
        # Enviar el embed con la respuesta
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Hubo un error al obtener el ranking: {e}")