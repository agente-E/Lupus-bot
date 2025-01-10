@bot.event
async def on_voice_state_update(member, before, after):
    user_id = str(member.id)
    if before.channel is None and after.channel is not None:
        # Usuario se une a un canal de voz.
        if user_id not in active_tasks:
            await track_voice_time(member)
    elif before.channel is not None and after.channel is None and not member.voice:
        # Usuario sale del canal de voz.
        if user_id in active_tasks:
            await end_tracking(member)