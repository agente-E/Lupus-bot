@tasks.loop(seconds=60)
async def check_live_status():
    global is_live
    stream_data = verificar_estado_directo()
    if stream_data:
        if not is_live:
            is_live = True
            channel = bot.get_channel(CHANNEL_TWITCH)
            if channel:
                embed = discord.Embed(
                    title="¡Estoy en directo!🔴", 
                    description=f"¡Ven a ver mi transmisión! [Enlace directo]({DIRECT_URL})",
                    color=discord.Color.green()
                )
                image_url = stream_data['thumbnail_url'].replace("{width}x{height}", "1280x720")
                embed.set_image(url=image_url)
                button = discord.ui.Button(label="Ver Directo", url=DIRECT_URL)
                view = discord.ui.View()
                view.add_item(button)
                await channel.send(f"<@&{ROLE_TWITCH}>", embed=embed, view=view)
    else:
        is_live = False
