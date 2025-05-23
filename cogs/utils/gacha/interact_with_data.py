# TODO
import discord
import random
from pocketbase import PocketBase
from pocketbase.errors import ClientResponseError
from datetime import datetime, timezone
from discord.ext import commands

"""Class created to interact with database, it will get and save data. Using PocketBase"""
class InteractWithDatabase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.config.get("guild", {})["hispanic"]
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

    async def reroll_aspect(self, data: dict) -> dict:
        
        # Get all aspects
        aspects = await self.get_aspects()

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
        aspects = await self.get_aspects()         

        # Filter out unwanted aspects for selection
        filtered_aspects = [aspect for aspect in aspects if aspect['name'] not in ['Auroran', 'Lightborn', 'Primal Vesperian']]

        # Extract names and probabilities
        names = [aspect['name'] for aspect in filtered_aspects]
        probabilities = [aspect['probability'] for aspect in filtered_aspects]

        # Select one at random based on probability
        selected_aspect = random.choices(names, probabilities, k=1)[0]
        return selected_aspect

    async def __get_rewards_id(self, data: list) -> list:
        try:
            rewards = await self.get_rewards()
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

    async def save_user_data(self, user_id: int, data: dict):
        '''Saves the data from a specific user to USER'''
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
                data['unlocks'] = await self.__get_rewards_id(data=data['unlocks'])
            
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

    # def __get_item_id(self, data: list):
    #     try:
    #         items = self.get_items()
    #         name_to_id = {item['name']: items['id'] for item in items}
    #         parsed_ids = [name_to_id[name] for name in data if name in name_to_id]
    #         return parsed_ids
    #     except ClientResponseError as e:
    #         if e.status != 404:
    #             print(f"Ocurrió un error con la base de datos:\n{e}")
    #             print(f"Código de estado: {e.status}")
    #             return
            
    #         print("No se encontraron datos en la consulta.")
    #     except Exception as e:
    #         print(F"Ha ocurrido un error: {e}")            

    def save_user_inventory(self, user_id: int, inventory_data: list):
        '''Saves the data from a specific user to INVENTORY'''
        try:
            # Parse the id to string
            parsed_id = str(user_id)
          
            for item in inventory_data:
                item_id = item.get("id")
                quantity = item.get("quantity", 0)
            
                existing = self.__client.collection(self.__inventory).get_full_list(
                    query_params={
                        "filter": f"user_id='{parsed_id}' && item_id='{item_id}'"
                    }
                )

                if existing:
                    inventory_record = existing[0]
                    new_quantity = inventory_record['quantity'] + quantity
                    if new_quantity <= 0:
                        self.__client.collection(self.__inventory).delete(inventory_record["id"])
                    else:
                        self.__client.collection(self.__inventory).update(
                        parsed_id,
                        {"quantity": new_quantity}
                    )
                else:
                    if quantity > 0:
                        self.__client.collection(self.__inventory).create({
                            "user_id": parsed_id,
                            "item_id": item_id,
                            "quantity": quantity
                        })

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
    
    async def increment_exp(self, user_id: int, experience: int):
        try:
            self.__client.collection(self.__users).update(
                    id=str(user_id),
                    body_params={'experience+': experience}
                )
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    async def increment_notes(self, user_id: int, notes: int):
        try:
            self.__client.collection(self.__client).update(
                    id=user_id,
                    body_params={'notes+': notes}
                )
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    async def increment_notes_exp(self, user_id: int, notes: int, experience: int):
        try:
            self.__client.collection(self.__client).update(
                    id=user_id,
                    body_params={'notes+': notes, 'experience+': experience}
                )
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    async def get_rewards(self) -> list:
        '''Returns multiple rows from table REWARDS''' # TODO
        try:
            # Get the name and the cost from the databaese, filter by its category and if it is a shop item
            rewards = self.__client.collection(self.__rewards).get_full_list(query_params={"expand": 'item'})

            # Parse the items
            rewards_data = [
                {
                    'id': reward.id,
                    'name': reward.name,
                    'probability': reward.probability,
                    'type': reward.type,
                    'value': reward.value,
                    'unlockable': reward.unlockable,
                    'item': getattr(reward.expand.get("item"), "name", None),
                    'pity_reward': reward.pity_reward
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
    
    async def get_items(self) -> list:
        '''Returns multiple rows from table ITEMS'''
        try:
            # Get the name and the cost from the databaese, filter by its category and if it is a shop item
            items = self.__client.collection(self.__items).get_full_list()

            # Parse the items
            items_data = [
                {
                    'id': item.id,
                    'name': item.name,
                    'category': item.category,
                    'shop_item': item.shop_item,
                    'cost': item.cost
                } for item in items]
            return items_data

        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    async def get_shop_items(self, category: str) -> dict:
        '''Returns multiple rows from table ITEMS that has shop_item as True filtered by passed category'''
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
    
    async def get_aspects(self) -> list:
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

    async def get_ranking(self) -> list:
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

    async def get_user_inventory(self, user_id) -> list:
        """
        Retrieves a specific item from a user's inventory, if it exists.

        Purpose:
            This function is used to check whether a specific item exists in a user's inventory.
            For validating ownership or preparing to update item quantity.

        Args:
            user_id (int): The unique identifier of the user.
            item_id (str): The unique identifier of the item to look up.

        Returns:
            dict: (If not exists, returns None) Returns a dictionary representing the inventory record if found, with:
                - id (str): The unique ID of the inventory record.
                - item (str): The item ID.
                - quantity (int): The quantity of the item.
        """
        try:
            # Get the inventory of the user from database
            user_inventory = self.__client.collection(self.__inventory).get_full_list(
                query_params={
                    "filter": f"user_id='{str(user_id)}'",
                    "expand": 'item_id'
                }
            )               

            # Sort by item name
            sorted_inventory = sorted(
                user_inventory, 
                key=lambda x: getattr(x.expand.get("item_id"), "name", "").lower()
            )

            # Extract relevant attributes (item name, quantity)
            user_inventory_data = [
                {
                    'id': record.id if record.id else None,
                    'item': getattr(record.expand.get("item_id"), "name", None),
                    'quantity': record.quantity
                }
                for record in sorted_inventory
            ]
            print(user_inventory_data)
            return user_inventory_data

        except ClientResponseError as e:
            print(f"Ocurrió un error con la base de datos:\n{e}")
            print(f"Código de estado: {e.status}")
            return

        except Exception as e:
            print(f"Ha ocurrido un error: {e}")
            raise

    async def get_item_user_inventory(self, user_id, item_id: str) -> dict:
        """
        Retrieves a specific item from a user's inventory, if it exists.

        Purpose:
            Checks whether a user has a particular item in their inventory.
            For updating quantities or validating item ownership.

        Args:
            user_id (int): The unique identifier of the user.
            item_id (str): The unique identifier of the item to search for.

        Returns:
            dict: (If not exists, returns None) A dictionary representing the inventory record if found, containing:
                - id (str): The inventory record ID.
                - item (str): The item ID.
                - quantity (int): The quantity of the item.
        """
        try:
            # Get the inventory of the user from database
            user_inventory = self.__client.collection(self.__inventory).get_full_list(
                query_params={
                    "filter": f"user_id='{str(user_id)}' && item_id='{item_id}'",
                    "expand": 'item_id'
                }
            )
            
            if not user_inventory:
                return None
            
            record = user_inventory[0]

            return{
                'id': record.id if record.id else None,
                'item': getattr(record.expand.get("item_id"), "name", None),
                'quantity': record.quantity
            }

        except ClientResponseError as e:
            print(f"Ocurrió un error con la base de datos:\n{e}")
            print(f"Código de estado: {e.status}")
            return

        except Exception as e:
            print(f"Ha ocurrido un error: {e}")
            raise

    async def get_user_unlocks(self, user_id: int):
        try:
            # Get the data of the user from database
            user_data = self.__client.collection(self.__users).get_one(id=str(user_id), query_params={'fields': 'unlocks'})
            
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

    async def attach_role(self, user_id: int, reward: dict):
        try:
            reward_id = await self.__get_reward_id(reward_name=reward['name'])
            self.__client.collection(self.__users).update(
                id=str(user_id),
                body_params={'unlocks+': reward_id}
            )
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    async def add_reward_user(self, user_id: int, reward: dict):
        """
        Applies a reward to a specified user based on the reward type.

        Purpose:
            Determines the appropriate action depending on the type of reward provided.
            This may include adding experience points, attaching roles (as unlocks),
            or adding items to the user's inventory. It allows for flexible reward handling
            in systems like gacha, achievements, or events.

        Args:
            user_id (int): The unique identifier of the user receiving the reward.
            reward (dict): A dictionary containing reward details, which may include:
                - id (int)
                - name (str)
                - probability (int)
                - type (str): One of "Experience", "Role", or "Item"
                - value (int): Only used if type is "Experience"
                - unlockable (bool): Only used if type is "Role"
                - item (str): Only used if type is "Item"
                - pity_reward (bool)
        """
        reward_type = reward['type']

        match reward_type:
            case 'Experience':
                await self.increment_exp(user_id=user_id, experience=reward['value'])

            case 'Role':
                await self.attach_role(user_id=user_id, reward=reward)

            case 'Item':
                await self.add_item_user(user_id=user_id, item_name=reward['item'], quantity=1)

            case _:
                # Por si el tipo no coincide con ninguno anterior
                print(f"Tipo de recompensa desconocido: {reward_type}")
                return

    async def add_item_user(self, user_id: int, item_name: str, quantity: int):        
        """
        Adds the specified item to an user inventory.

        Purpose:
            Adds a specified quantity of an item to a user's inventory.
            If the item already exists for the user, the quantity is updated.
            Otherwise, a new inventory record is created.

        Args:
            user_id (int): The unique identifier of the user.
            item_name (str): The name of the item to add.
            quantity (int): The amount of the item to add.
        """
        try:
            # Get the id of the item
            item_id = await self.__get_item_id(item_name=item_name)

            # Search if the item already exists in the INVENTORY table
            existing_item = await self.get_item_user_inventory(user_id=user_id, item_id=item_id)
            if existing_item:
                
                # If it exists, update the quantity
                new_quantity = existing_item['quantity'] + quantity
                self.__client.collection(self.__inventory).update(
                    id=existing_item['id'],
                    body_params={'quantity': new_quantity}
                )
            else:
                # If it doesn't exist, create a new entry
                data = {
                    'user_id': str(user_id),
                    'item_id': item_id,
                    'quantity': quantity
                }
                self.__client.collection(self.__inventory).create(body_params=data)

        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    async def remove_item_user(self, user_id: int, item_name: str, quantity: int):        
        """
        Removes the specified item to an user inventory.

        Purpose:
            Removes a specified quantity of an item to a user's inventory.
            If the item already exists for the user, the quantity is updated.
            Otherwise, a new inventory record is created.

        Args:
            user_id (int): The unique identifier of the user.
            item_name (str): The name of the item to remove.
            quantity (int): The amount of the item to remove.
        """
        try:
            # Get the id of the item
            item_id = await self.__get_item_id(item_name=item_name)

            # Search if the item already exists in the INVENTORY table
            existing_item = await self.get_item_user_inventory(user_id=user_id, item_id=item_id)
            if existing_item:
                new_quantity = existing_item['quantity'] - quantity
                print(existing_item)
                print(new_quantity)
                # If it exists, update the quantity
                # In case that reaches zero, delete the row
                if new_quantity <= 0:
                    
                    self.__client.collection(self.__inventory).delete(
                        id=existing_item['id']
                    )
                else:
                    self.__client.collection(self.__inventory).update(
                        id=existing_item['id'],
                        body_params={'quantity': new_quantity}
                    )

        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")


    async def __get_reward_id(self, reward_name: str) -> str:
        try:
            rewards = await self.get_rewards()
            name_to_id = {i['name']: i['id'] for i in rewards}
            return name_to_id[reward_name]
        except KeyError:
            raise ValueError(f"Item '{reward_name}' no encontrado.")


    async def __get_item_id(self, item_name: str) -> str:
        """
        Gets the ID of an item based on its name.

        Purpose:
            This function translates a human-readable item name into the corresponding
            internal database ID. It is used to avoid relying on hardcoded IDs and
            ensures consistent referencing of items when performing database operations.

        Args:
            item_name (str): The name of the item to look up.

        Returns:
            str: The database ID associated with the given item name.
        """
        try:
            items = await self.get_items()
            name_to_id = {i['name']: i['id'] for i in items}
            return name_to_id[item_name]
        except KeyError:
            raise ValueError(f"Item '{item_name}' no encontrado.")

        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")
    
    async def get_user_level(self, user_id: int) -> dict:
        """
        Retrieves the level and experience of a user from the USERS table.

        Purpose:
            This function is designed to access only the essential progress data of a user,
            such as their level and experience points. For features like
            leveling systems, user stats display, and experience-based logic.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            dict: A dictionary containing:
                - level (int): The user's current level.
                - experience (int): The user's total accumulated experience.
        """
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
        """
        Retrieves a user record from the USERS table, including expanded data
        from the ASPECTS and REWARDS tables.

        Purpose:
            Provides complete data required to display and manage a user profile,
            including their aspect, unlocked rewards (as names), and various attributes
            relevant to gameplay logic and UI rendering.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            dict: A dictionary containing the following user profile fields:
                - id (int)
                - username (str)
                - aspect (str)
                - level (int)
                - experience (int)
                - notes (int)
                - knowledge (int)
                - last_message (int): Time of last message (epoch)
                - last_gacha (int): Time of last gacha usage (epoch)
                - pity_counter (int)
                - unlocks (list): List of unlocked reward names
                - title (str)
                - mod (bool)
        """
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

    def __to_epoch(self, time_str: str) -> int:
        """
        Converts a PocketBase datetime string to epoch time.

        Purpose:
            Allows integration with platforms like Discord that support relative timestamps
            using epoch time, making it easier to present time-based events dynamically.

        Args:
            time_str (str): A datetime string in ISO 8601 format (e.g., "2025-05-23 18:45:00.000Z").

        Returns:
            int: The corresponding epoch time in seconds (e.g., 1748014608).
        """

        if time_str == '':
            return
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return int(dt.timestamp())

async def setup(bot):
    await bot.add_cog(InteractWithDatabase(bot))