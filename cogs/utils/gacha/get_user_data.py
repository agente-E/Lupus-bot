import discord
import requests
from discord.ext import commands


class getUserData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pb_url = 'http://localhost:8090'

    def get_users_levels(self):
        try:
            # URL API
            users_url = f'{self.pb_url}/api/collections/USERS/records?fields=id,level'
            response = requests.get(users_url)
            users_data = response.json()
            # Filtrar y ordenar los usuarios por el campo 'level' (de mayor a menor)
            users_sorted = sorted(users_data['items'], key=lambda x: x['level'], reverse=True)
            # Crear una lista con los 'id' y 'level' de cada usuario
            users_level_info = [{'ID': user['id'], 'Level': user['level']} for user in users_sorted]
            # Retornar la lista de usuarios con su id y level
            return users_level_info

            # Si la solicitud no fue exitosa, devolver un mensaje de error
        except Exception as e:
            # Manejo de excepciones
            return {'error': str(e)}



    def get_user_data(self, user_id: str):
        try:
            user_url = f'{self.pb_url}/api/collections/USERS/records/{user_id}'
            user_data_response = requests.get(user_url)
            if user_data_response.status_code == 200:
                user_data = user_data_response.json()
                obtained_roles_url = f'{self.pb_url}/api/collections/OBTAINED_ROLES/records?filter=user_id="{user_id}"'
                obtained_roles_response = requests.get(obtained_roles_url)
                if obtained_roles_response.status_code == 200:
                    obtained_roles = obtained_roles_response.json().get('items', [])
                else:
                    obtained_roles = []
                try:
                    roles = []
                    for role in obtained_roles:
                        for role_id in role.get('role_id', []):
                            role_url = f'{self.pb_url}/api/collections/ROLES/records/{role_id}'
                            role_data_response = requests.get(role_url)
                            if role_data_response.status_code == 200:
                                role_data = role_data_response.json()
                                roles.append(role_data.get('name', 'Unknown'))
                except:
                    print("No elegible roles")
                user_info = {
                    "ID": user_data["id"],
                    "Echoes": user_data.get("echoes", "No Data"),
                    "Experience": user_data.get("experience", "No Data"),
                    "Level": user_data["level"],
                    "Pity Counter": user_data.get("pity_counter", "No Data"),
                    "Last Gacha": user_data.get("last_gacha", "No Data"),
                    "Last message": user_data.get("last_message", "No data"),
                    "Roles": ", ".join(roles) if roles else "No roles obtained",
                    "Created": user_data["created"],
                    "Updated": user_data["updated"]
                }
                return user_info
            else:
                print(f"Usuario con el ID {user_id} no se encontró en la base de datos. Creando nuevo perfil")
                user_data = self.create_new_user_profile(user_id)
                print(user_data)
                obtained_roles_url = f'{self.pb_url}/api/collections/OBTAINED_ROLES/records?filter=user_id="{user_id}"'
                obtained_roles_response = requests.get(obtained_roles_url)
                if obtained_roles_response.status_code == 200:
                    obtained_roles = obtained_roles_response.json().get('items', [])
                else:
                    obtained_roles = []
                try:
                    roles = []
                    for role in obtained_roles:
                        for role_id in role.get('role_id', []):
                            role_url = f'{self.pb_url}/api/collections/ROLES/records/{role_id}'
                            role_data_response = requests.get(role_url)
                            if role_data_response.status_code == 200:
                                role_data = role_data_response.json()
                                roles.append(role_data.get('name', 'Unknown'))
                except:
                    print("No elegible roles")
                user_info = {
                    "ID": user_data["id"],
                    "Echoes": user_data.get("echoes", "No Data"),
                    "Experience": user_data.get("experience", "No Data"),
                    "Level": user_data["level"],
                    "Pity Counter": user_data.get("pity_counter", "No Data"),
                    "Last Gacha": user_data.get("last_gacha", "No Data"),
                    "Last message": user_data.get("last_message", "No data"),
                    "Roles": ", ".join(roles) if roles else "No roles obtained",
                    "Created": user_data["created"],
                    "Updated": user_data["updated"]
                }
                return user_info

        except requests.exceptions.RequestException as e:
            return f"An error occurred while fetching user data: {str(e)}"

    def create_new_user_profile(self, user_id: str):
        # Crear un perfil nuevo con valores predeterminados
        user_data = {
            "id": user_id,
            "echoes": 0,
            "experience": 0,
            "level": 1,
            "pity_counter": 0,
            "last_gacha": None,
            "last_message": None
        }
        try:
            # Enviar la solicitud para crear un nuevo usuario
            create_url = f'{self.pb_url}/api/collections/USERS/records'
            response = requests.post(create_url, json=user_data)
            user_url = f'{self.pb_url}/api/collections/USERS/records/{user_id}'
            user_data_response = requests.get(user_url)
            if user_data_response.status_code == 200:
                user_data = user_data_response.json()
                return user_data

        except requests.exceptions.RequestException as e:
            print(f"Error al intentar crear el perfil del usuario: {str(e)}")
            return None


# Para agregar el Cog al bot
async def setup(bot):
    await bot.add_cog(getUserData(bot))