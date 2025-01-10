async def track_voice_time(member):
    """Inicia el seguimiento del tiempo en el canal de voz."""
    user_id = str(member.id)
    active_tasks[user_id] = datetime.now()  # Marca la hora de entrada.
    try:
        while member.voice and member.voice.channel:
            await asyncio.sleep(60)  # Espera un minuto.
            if member.voice and member.voice.channel:
                accumulate_time(user_id, member)  # Actualiza el tiempo acumulado.
            else:
                break  # Si el usuario ya no está conectado, rompe el bucle.
    except Exception as e:
        print(f"Error en track_voice_time para {member.name}: {e}")