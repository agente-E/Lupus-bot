# TODO

# import discord
# import 

# self.user_last_message_time[user_id] = current_time

#   # user_data = get_user_data(user_id)
#   # aspect = user_data["aspecto"]
#   booster_role_name = "Server Booster"
#    if any(role.name == booster_role_name for role in message.author.roles):
#         if aspect == "Canor":
#             user_data['echoes'] += random.randint(20, 30)
#         elif aspect == "Etrean":
#             user_data['echoes'] += random.randint(5, 35)
#         else:
#             user_data['echoes'] += random.randint(15, 25)
#         if aspect == "Adret":
#             user_data['experiencia'] += random.randint(
#                 15 * 2, 25 * 2)
#         else:
#             user_data['experiencia'] += random.randint(15, 25)
#         user_data = await check_and_level_up(user_data, message=message)
#     else:
#         if aspect == "Canor":
#             user_data['echoes'] += random.randint(5, 10)
#         elif aspect == "Etrean":
#             user_data['echoes'] += random.randint(0, 10)
#         else:
#             user_data['echoes'] += random.randint(1, 5)
#         if aspect == "Adret":
#             user_data['experiencia'] += random.randint(
#                 1 * 2, 5 * 2)
#         else:
#             user_data['experiencia'] += random.randint(1, 5)
#         user_data = await check_and_level_up(user_data, message=message)
#     save_user_data(user_id, user_data)
