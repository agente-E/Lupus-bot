# TODO
from pocketbase import PocketBase
from pocketbase.errors import ClientResponseError
from datetime import datetime, timezone
from discord.ext import commands

"""Class created to interact with database, it will get and save data. Using PocketBase"""
class InteractWithDatabase(commands.Cog):
    def __init__(self, bot):
        self.__client = PocketBase('http://127.0.0.1:8090')
        self.__users = 'USERS'
        self.__aspects = 'ASPECTS'
        self.__inventory = 'INVENTORY'
        self.__items = 'ITEMS'
        self.__rewards = 'REWARDS'

    '''Returns multiple rows from table REWARDS''' # TODO
    def get_rewards(self) -> dict:
        try:
            # Get the name and the cost from the databaese, filter by its category and if it is a shop item
            rewards = self.__client.collection(self.__rewards).get_full_list(query_params={'fields': 'name, probability, type, value, pity_reward, unlockable'})

            # Parse the items
            rewards_data = [{'name': reward.name, 'probability': reward.probability, 'type': reward.type, 'value': reward.value, 'pity_reward': reward.pity_reward, 'unlockable': reward.unlockable} for reward in rewards]

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
    def get_shop_items(self, category: str) -> dict:
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
    def get_aspects(self) -> dict:
        try:
            # Get the name, probabity and color from the databaese
            aspects = self.__client.collection(self.__aspects).get_full_list(query_params={'fields': 'name, probability, color'})

            # Parse the aspects
            aspects_data = [{'name': aspect.name, 'probability': aspect.probability, 'color': aspect.color} for aspect in aspects]

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

    '''Returns multiple rows from table INVENTORY formated'''
    def get_user_inventory(self, user_id) -> list:
        try:
            parsed_id = str(user_id)
            
            # Get the inventory of the user from database
            user_inventory = self.__client.collection(self.__inventory).get_full_list(query_params={"filter": f"user_id='{parsed_id}'"})

            # Sort the data by user, item, and quantity
            sorted_inventory = sorted(
                user_inventory, 
                key=lambda x: (x.item_id, x.quantity)
            )

            # Extract relevant attributes (user, item, quantity)
            user_inventory_data = [
                {'item': record.item_id, 'quantity': record.quantity}  
                for record in sorted_inventory
            ]
            
            return user_inventory_data
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    '''Returns a row from table USERS, level and experience'''
    def get_user_level(self, user_id: int) -> list:
        try:
            parsed_id = str(user_id)

            # Get the data of the user from database
            user_data = self.__client.collection(self.__users).get_one(id=parsed_id, query_params={'fields': 'level, experience'})
            
            # Parse the level and experience
            user_level_stats = {'level': user_data.level, 'experience': user_data.experience}

            return user_level_stats
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    '''Returns a row from table USERS formated with expand ASPECTS and REWARDS table, rewards as unlocks'''
    def get_user_data(self, user_id:int) -> dict:
        try:
            # Parse the id as string because pocketbase 
            # for some reason doesn't let you put the id as int 
            parsed_id = str(user_id)
            
            # Get the data of the user from database
            user_data = self.__client.collection(self.__users).get_one(id=parsed_id, query_params={"expand": 'aspect, unlocks'})
            
            # Get the name of the aspect
            aspect_name = getattr(user_data.expand.get("aspect"), "name", None)
    
            # Get the name of the unlocked items
            unlocks_names = [
                getattr(unlocked_item, "name", None) 
                for unlocked_item in user_data.expand.get("unlocks", [])
            ]

            # Extract the data in a specific order
            ordered_data = {
                "id": int(user_data.id), # Parse ID as an int
                "username": user_data.username,
                "aspect": aspect_name,
                "level": user_data.level,
                "experience": user_data.experience,
                "notes": user_data.notes,
                "knowledge": user_data.knowledge,
                "last_message": self.__to_epoch(user_data.last_message), # Parse to epoch time ('cause I like it)
                "last_gacha": self.__to_epoch(user_data.last_gacha),
                "pity_counter": user_data.pity_counter,
                "unlocks": unlocks_names
            }
            
            return ordered_data
        except ClientResponseError as e:
            if e.status != 404:
                print(f"Ocurrió un error con la base de datos:\n{e}")
                print(f"Código de estado: {e.status}")
                return
            
            print("No se encontraron datos en la consulta.")
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    '''Convert PocketBase datetime string to epoch time.'''
    def __to_epoch(self, time_str: str) -> int:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return int(dt.timestamp())
    
    def __to_pocketbase_datetime(self, epoch_time: int) -> str:
        # Convert epoch time to a datetime object in UTC
        dt = datetime.fromtimestamp(epoch_time, tz=timezone.utc)
        return dt.isoformat()  # Convert to ISO 8601 format with UTC timezone


async def setup(bot):
    await bot.add_cog(InteractWithDatabase(bot))