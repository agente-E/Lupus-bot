# async def end_tracking(member):
#     """Finaliza el seguimiento cuando el usuario sale del canal."""
#     user_id = str(member.id)
#     if user_id in active_tasks:
#         try:
#             accumulate_time(user_id, member)  # Asegúrate de sumar tiempo acumulado.
#             del active_tasks[user_id]  # Eliminar la tarea activa.
#             print(f"{member.name} ha salido del canal. Tiempo total acumulado: {user_times.get(user_id, 0)} minutos.")
#             # Opcional: Guardar datos en la base de datos.
#             save_user_data(user_id, get_user_data(user_id))
#         except Exception as e:
#             print(f"Error en end_tracking para {member.name}: {e}")