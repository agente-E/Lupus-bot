# TODO
import random
from pocketbase import PocketBase
from pocketbase.errors import ClientResponseError
from datetime import datetime, timezone
from discord.ext import commands

"""Class created to interact with database, it will get and save data. Using PocketBase"""
class InteractWithDatabase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__client = PocketBase('http://192.168.1.132:8090')
        self.__users = 'USERS'
        self.__aspects = 'ASPECTS'
        self.__inventory = 'INVENTORY'
        self.__items = 'ITEMS'
        self.__rewards = 'REWARDS'
        self.__aspect_map = {
            "Vesperian": "vesn",
            "Tiran": "tirn",
            "Primal Vesperian": "prin",
            "Lightborn": "lign",
            "Khan": "khan",
            "Gremor": "grer",
            "Ganymede": "gane",
            "Felinor": "felr",
            "Chrysid": "chrd",
            "Etrean": "etrn",
            "Celtor": "celr",
            "Capra": "capa",
            "Canor": "canr",
            "Auroran": "aurn",
            "Adret": "adrt"
        }

    '''Creates a new user on the database'''
    async def __create_new_user(self, user_id: int):
        try:

            # Parse the id as string
            parsed_id = str(user_id)

            # Get the username running an async
            user = await self.bot.fetch_user(user_id)
    
            # Get a random aspect by their probability
            aspect = self.__get_aspect_id(await self.get_random_aspect())

            data = {
                'id': parsed_id,
                'username': user.name,
                'aspect': aspect,
                'level': 1,
            }

            # Send the request to create the user
            self.__client.collection(self.__users).create(body_params=data)

        except ClientResponseError as e:
            print(f"Ocurrió un error con la base de datos:\n{e}")
            print(f"Código de estado: {e.status}")
            raise
        except Exception as e:
            print(f"Ha ocurrido un error: {e}")
            raise

    def reroll_aspect(self, data: dict) -> dict:
        
        # Get all aspects
        aspects = self.get_aspects()

        # Extract names and probabilities
        names = [aspect['name'] for aspect in aspects]
        probabilities = [aspect['probability'] for aspect in aspects]

        current_aspect = data['aspect']

        while True:
            selected_aspect = random.choices(names, probabilities, k=1)[0]

            if selected_aspect == current_aspect:
                continue

            if selected_aspect == 'Primal Vesperian' and data.get('level', 0) < 100:
                continue

            if selected_aspect in ['Auroran', 'Lightborn'] and not data.get('mod', False):
                continue

            # If all filters are passed, we assign the new aspect
            data['aspect'] = selected_aspect
            return data

    async def get_random_aspect(self) -> str:
        
        # Get all aspects
        aspects = self.get_aspects()         

        # Filter out unwanted aspects for selection
        filtered_aspects = [aspect for aspect in aspects if aspect['name'] not in ['Auroran', 'Lightborn', 'Primal Vesperian']]

        # Extract names and probabilities
        names = [aspect['name'] for aspect in filtered_aspects]
        probabilities = [aspect['probability'] for aspect in filtered_aspects]

        # Select one at random based on probability
        selected_aspect = random.choices(names, probabilities, k=1)[0]
        return selected_aspect

    def __get_reward_id(self, data: list):
        try:
            rewards = self.get_rewards()
            name_to_id = {reward['name']: reward['id'] for reward in rewards}
            parsed_ids = [name_to_id[name] for name in data if name in name_to_id]
            return parsed_ids
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")            

    def save_user_data(self, user_id: int, data: dict):
        '''Saves the data from a specific user to USER and INVENTORY'''
        try:
            # Parse the id to string
            parsed_id = str(user_id)

            # Manipulate the data to save it on the database
            # Parse the id to string
            data['id'] = parsed_id
            
            # Parse the aspect as id
            data['aspect'] = self.__get_aspect_id(data['aspect'])

            # Parse the last message and last gacha to pocketbase datetime
            data['last_message'] = self.__to_pocketbase_datetime(data['last_message'])
            data['last_gacha'] = self.__to_pocketbase_datetime(data['last_gacha'])
            
            # Parse the relations for unlocks
            if data['unlocks'] != None:
                data['unlocks'] = self.__get_reward_id(data=data['unlocks'])
            
            # Update the data from the user
            self.__client.collection(self.__users).update(id=parsed_id, body_params=data)

        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    def __get_aspect_id(self, aspect_name: str) -> str:
            return self.__aspect_map.get(aspect_name)
    
    def __to_pocketbase_datetime(self, epoch_time: int) -> str:
        if epoch_time == None:
            return
        # Convert epoch time to a datetime object in UTC
        dt = datetime.fromtimestamp(epoch_time, tz=timezone.utc)
        return dt.isoformat()
    
    def get_rewards(self) -> dict:
        '''Returns multiple rows from table REWARDS''' # TODO
        try:
            # Get the name and the cost from the databaese, filter by its category and if it is a shop item
            rewards = self.__client.collection(self.__rewards).get_full_list()

            # Parse the items
            rewards_data = [
                {
                    'id': reward.id,
                    'name': reward.name,
                    'probability': reward.probability,
                    'type': reward.type,
                    'value': reward.value,
                    'pity_reward': reward.pity_reward,
                    'unlockable': reward.unlockable
                } for reward in rewards]

            return rewards_data
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")
    
    '''Returns multiple rows from table ITEMS that has shop_item as True filtered by passed category'''
    def     get_shop_items(self, category: str) -> dict:
        try:
            # Get the name and the cost from the databaese, filter by its category and if it is a shop item
            items = self.__client.collection(self.__items).get_full_list(query_params={'fields': 'name, category, shop_item, cost', 'sort': '-cost', 'filter': f'shop_item = true && category = "{category}"'})

            # Parse the items
            items_data = [{'name': item.name, 'cost': item.cost} for item in items]

            return items_data
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")
    
    '''Returns multiple rows from table ASPECTS formated'''
    def get_aspects(self) -> list:
        try:
            # Get the name, probabity and color from the databaese
            aspects = self.__client.collection(self.__aspects).get_full_list(query_params={'fields': 'name, description, passive, probability, color, exclusive'})

            # Parse the aspects
            aspects_data = [
                {
                    'name': aspect.name,
                    'description': aspect.description,
                    'passive': aspect.passive,
                    'probability': aspect.probability,
                    'color': aspect.color,
                    'exclusive': aspect.exclusive
                } for aspect in aspects]

            return aspects_data
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    '''Returns multiple rows from table USERS, only id, level and experience sorted ASC'''
    def get_ranking(self) -> list:
        try:
            # Get the ID and level of the user from database
            users = self.__client.collection(self.__users).get_full_list(query_params={'fields': 'id, level, experience'})

            # Parse ID as int and order by level
            ranking = sorted([{'id': int(user.id), 'level': user.level, 'experience': user.experience} for user in users], key=lambda x: (x['level'], x['experience']))

            return ranking
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    def get_user_inventory(self, user_id) -> dict:
        try:
            # Get the inventory of the user from database
            user_inventory = self.__client.collection(self.__inventory).get_full_list(
                query_params={
                    "filter": f"user_id='{str(user_id)}'",
                    "expand": 'item_id'
                }
            )

            # Sort the data by item and quantity
            sorted_inventory = sorted(
                user_inventory, 
                key=lambda x: (x.item_id, x.quantity)
            )

            # Extract relevant attributes (item name, quantity)
            user_inventory_data = [
                {
                    'item': getattr(record.expand.get("item_id"), "name", None),
                    'quantity': record.quantity
                }
                for record in sorted_inventory
            ]

            return user_inventory_data

        except ClientResponseError as e:
            print(f"Ocurrió un error con la base de datos:\n{e}")
            print(f"Código de estado: {e.status}")
            return

        except Exception as e:
            print(f"Ha ocurrido un error: {e}")
            raise

    '''Returns a row from table USERS, level and experience'''
    def get_user_level(self, user_id: int) -> dict:
        try:
            # Get the data of the user from database
            user_data = self.__client.collection(self.__users).get_one(id=str(user_id), query_params={'fields': 'level, experience'})
            
            # Parse the level and experience
            user_level_stats = {'level': user_data.level, 'experience': user_data.experience}

            return user_level_stats
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
            raise
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")
            raise

    async def get_user_data(self, user_id: int) -> dict:
        '''Returns a row from table USERS formated with expand ASPECTS and REWARDS table, rewards as unlocks'''
        try:
            # Request to the database to get the data of the user
            user_data = self.__client.collection(self.__users).get_one(id=str(user_id), query_params={"expand": "aspect, unlocks, title"})

            # Order the data and parse it to work with it better
            ordered_data = {
                    "id": user_id,
                    "username": user_data.username,
                    "aspect": getattr(user_data.expand.get("aspect"), "name", None),
                    "level": user_data.level,
                    "experience": user_data.experience,
                    "notes": user_data.notes,
                    "knowledge": user_data.knowledge,
                    "last_message": self.__to_epoch(user_data.last_message),
                    "last_gacha": self.__to_epoch(user_data.last_gacha),
                    "pity_counter": user_data.pity_counter,
                    "unlocks": [getattr(unlock, 'name', None) for unlock in user_data.expand.get("unlocks", [])], # If there are no unlocks, just ignore it and return empty
                    "title": getattr(user_data.expand.get("title"), "name", None),
                    "mod": user_data.mod
                }

            return ordered_data
        except ClientResponseError as e:
            if e.status == 404:
                print("No se encontraron datos en la consulta, creando nuevo usuario")
                await self.__create_new_user(user_id)
                return await self.get_user_data(user_id) # Recursive call, this time, as it exists, it will find it this time
            else:
                print(f"Error en la base de datos ({e.status}): {e}")
                raise
        except Exception as e:
            print(f"Error inesperado: {e}")
            raise

    '''Convert PocketBase datetime string to epoch time.'''
    def __to_epoch(self, time_str: str) -> int:
        if time_str == '':
            return
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return int(dt.timestamp())

async def setup(bot):
    await bot.add_cog(InteractWithDatabase(bot))