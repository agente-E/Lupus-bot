import discord
import requests
from discord.ext import commands

class saveUserData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pb_url = 'http://localhost:8090'  # URL de tu servidor PocketBase

    def save_user_data(self, user_id, user_info):
        try:
            user_data = self.pb_client.collection('USERS').get_one(user_id)
            
            if user_data:
                updated_data = {**user_data, **user_info}
                self.pb_client.collection('USERS').update(user_id, updated_data)
                print(f"Usuario {user_id} actualizado con éxito.")
            else:
                new_data = {'id': user_id, **user_info}
                self.pb_client.collection('USERS').create(new_data)
                print(f"Usuario {user_id} creado con éxito.")
        except Exception as e:
            print(f"Error al guardar los datos del usuario {user_id}: {e}")

async def setup(bot):
    await bot.add_cog(saveUserData(bot))