import discord
import requests
from discord.ext import commands

class saveUserData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pb_url = 'http://localhost:8090'

    def save_user_data(self, user_id, user_data):
        url = f'{self.pb_url}/api/collections/USERS/records/{user_id}'
        try:
            response = requests.patch(url, json=user_data)
            if response.status_code == 200:
                print(f'Datos del usuario {user_id} actualizados correctamente.')
            else:
                print(f'Error al actualizar los datos del usuario {user_id}. Respuesta: {response.text}')
        except Exception as e:
            print(f'Error en la solicitud: {e}')

    def save_user_roles(self, user_id, role_ids):
        try:
            response = requests.get(f'{self.pb_url}/api/collections/OBTAINED_ROLES/records', params={'filter': f'user_id="{user_id}"'})
            if response.status_code == 200:
                records = response.json().get('items', [])
                if records:
                    record_id = records[0]['id']
                    print(f"RECORD_ID del usuario: {record_id}")
                    patch_response = requests.patch(
                        f'{self.pb_url}/api/collections/OBTAINED_ROLES/records/{record_id}',
                        json=data
                    )
                    if patch_response.status_code == 200:
                        print(f"Registro de roles actualizado para el usuario {user_id}.")
                    else:
                        print(f"Error al actualizar el registro de roles: {patch_response.text}")
                else:
                    print(f"No se encontró un registro de roles para el usuario {user_id}.")
            else:
                print(f"Error al obtener el registro de roles: {response.text}")
        except Exception as e:
            print(f"Error al intentar actualizar los datos del usuario: {e}")

async def setup(bot):
    await bot.add_cog(saveUserData(bot))
