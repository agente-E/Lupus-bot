# async def check_and_level_up(user_data, message:discord.Message = None, interaction:discord.Interaction = None):
#     if message is None and interaction is None: 
#         return
#     user = message.author.id if message is not None else interaction.user.id
#     channel = message.channel if message is not None else interaction.channel 
#     experiencia = user_data['experiencia']
#     nivel = user_data['nivel']
#     exp_requerida = (100 + nivel * 20)
#     while experiencia >= exp_requerida:
#         experiencia -= exp_requerida
#         exp_requerida = (100 + nivel * 20)
#         nivel += 1
#     if nivel > user_data['nivel']:
#         user_data['nivel'] = nivel
#         user_data['experiencia'] = experiencia
#         await channel.send(f"¡<@{user}> ha subido al nivel {nivel}!")
#     return user_data