import discord
import requests
from discord.ext import commands

class getUserData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pb_url = 'http://localhost:8090'  # URL de tu servidor PocketBase

    def get_user_data(self, user_id: str):
        try:
            # Endpoint para obtener los datos del usuario de la colección 'USERS'
            user_url = f'{self.pb_url}/api/collections/USERS/records/{user_id}'
            user_data_response = requests.get(user_url)

            # Si la solicitud fue exitosa
            if user_data_response.status_code == 200:
                user_data = user_data_response.json()

                # Obtener los roles del usuario
                obtained_roles_url = f'{self.pb_url}/api/collections/OBTAINED_ROLES/records?filter=user_id="{user_id}"'
                obtained_roles_response = requests.get(obtained_roles_url)
                
                if obtained_roles_response.status_code == 200:
                    obtained_roles = obtained_roles_response.json().get('items', [])
                else:
                    obtained_roles = []

                try:
                    # Extract roles from obtained_roles
                    roles = []
                    for role in obtained_roles:
                        # If role_id is a list (e.g., [39265987, 22135613]), we need to iterate over it
                        for role_id in role.get('role_id', []):
                            role_url = f'{self.pb_url}/api/collections/ROLES/records/{role_id}'
                            role_data_response = requests.get(role_url)
                            if role_data_response.status_code == 200:
                                role_data = role_data_response.json()
                                roles.append(role_data.get('name', 'Unknown'))
                except:
                    print("No elegible roles")
                # Estructura de los datos del usuario
                user_info = {
                    "ID": user_data["id"],
                    "Echoes": user_data.get("echoes", "No Data"),
                    "Experience": user_data.get("experiencie", "No Data"),
                    "Level": user_data["level"],
                    "Pity Counter": user_data.get("pity_counter", "No Data"),
                    "Last Gacha": user_data.get("last_gacha", "No Data"),
                    "Roles": ", ".join(roles) if roles else "No roles obtained",
                    "Last message": user_data.get("last_message", "No data"),
                    "Created": user_data["created"],
                    "Updated": user_data["updated"]
                }
                print(user_info)
                return user_info
            else:
                print(f"User with ID {user_id} not found in the database. Creating profile")
                user_data = self.create_new_user_profile(user_id)

        except requests.exceptions.RequestException as e:
            return f"An error occurred while fetching user data: {str(e)}"

    def create_new_user_profile(self, user_id: str):
        # Crear un perfil nuevo con valores predeterminados
        new_user_data = {
            "id": user_id,
            "echoes": 0,
            "experiencie": 0,
            "level": 1,
            "pity_counter": 0,
            "last_gacha": None,
            "last_message": None
        }
        try:
            # Enviar la solicitud para crear un nuevo usuario
            create_url = f'{self.pb_url}/api/collections/USERS/records'
            response = requests.post(create_url, json=new_user_data)

            if response.status_code == 201:
                new_user = response.json()
                return new_user
            else:
                return f"Error creating new user: {response.text}"

        except requests.exceptions.RequestException as e:
            return f"An error occurred while creating the new user profile: {str(e)}"


# Para agregar el Cog al bot
async def setup(bot):
    await bot.add_cog(getUserData(bot))