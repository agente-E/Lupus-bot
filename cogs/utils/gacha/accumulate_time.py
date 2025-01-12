# def accumulate_time(user_id, member):
#     """Suma el tiempo transcurrido al tiempo acumulado del usuario."""
#     if user_id in active_tasks:
#         # Calcula los minutos transcurridos desde la última marca de tiempo.
#         start_time = active_tasks[user_id]
#         elapsed_minutes = (datetime.now() - start_time).total_seconds() / 60
#         user_times[user_id] = user_times.get(user_id, 0) + int(elapsed_minutes)
#         active_tasks[user_id] = datetime.now()  # Actualiza la marca de tiempo.
#         # Recompensar al usuario por cada minuto acumulado.
#         user_data = get_user_data(user_id)
#         booster_role_name = "Server Booster"
#         if any(role.name == booster_role_name for role in member.roles):
#             for _ in range(int(elapsed_minutes)):
#                 user_data['echoes'] += random.randint(15, 25)
#                 user_data['experiencia'] += random.randint(15, 25)
#         else:
#             for _ in range(int(elapsed_minutes)):
#                  user_data['echoes'] += random.randint(1, 5)
#                 user_data['experiencia'] += random.randint(1, 5)
#         save_user_data(user_id, user_data)
