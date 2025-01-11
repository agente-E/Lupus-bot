import discord
import pocketbase
import requests
from discord.ext import commands

class saveUserData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pb_client = pocketbase.Client('http://localhost:8090')

    def save_user_data(self, user_id, user_info):
        try:
            user_data = self.pb_client.collection('USERS').get(user_id)
            # Si el usuario ya existe, lo actualizamos
            if user_data:
                user_data['data'] = user_info
                self.pb_client.collection('USERS').update(user_id, user_data)
                print(f"Usuario {user_id} actualizado con éxito.")
            else:
                self.pb_client.collection('USERS').create({'id': user_id, 'data': user_info})
                print(f"Usuario {user_id} creado con éxito.")
        except Exception as e:
            print(f"Error al guardar los datos del usuario {user_id}: {e}")

async def setup(bot):
    await bot.add_cog(saveUserData(bot))