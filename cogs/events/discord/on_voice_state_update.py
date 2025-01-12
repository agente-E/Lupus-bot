# from discord.ext import commands

# class VoiceStateCog(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @commands.Cog.listener()
#     async def on_voice_state_update(self, member, before, after):
#         user_id = str(member.id)
#         if before.channel is None and after.channel is not None:
#             Usuario se une a un canal de voz.
#             if user_id not in self.active_tasks:
#                 await track_voice_time(member)
#                 self.active_tasks[user_id] = True  # Marcamos al usuario como activo en la tarea de seguimiento
#                 print(f"Usuario {member} ha entrado al canal de voz.")
#         elif before.channel is not None and after.channel is None and not member.voice:
#             Usuario sale del canal de voz.
#             if user_id in self.active_tasks:
#                 await end_tracking(member)
#                 del self.active_tasks[user_id]  # Eliminamos al usuario de las tareas activas
#                 print(f"Usuario {member} ha salido del canal de voz.")

# Función para cargar el cog
# async def setup(bot):
#     await bot.add_cog(VoiceStateCog(bot))
