from pocketbase import PocketBase
from pocketbase.errors import ClientResponseError
from typing import Dict
from datetime import datetime

"""Class created to interact with database, it will get and save data. Using PocketBase"""
class InteractWithDatabase():
    def __init__(self):
        self.__client = PocketBase('http://127.0.0.1:8090')
        self.__users = 'USERS'
        self.__aspects = 'ASPECTS'
        self.__inventory = 'INVENTORY'
        self.__items = 'ITEMS'
        self.__rewards = 'REWARDS'

    '''Returns multiple rows from table USERS, only level sorted ASC'''
    def get_ranking(self):
        try:
            # Get the levels sorted
            self.__client.collection
        except Exception as e:
            print(f"Ha ocurrido un error: {e}")

    '''Returns multiple rows from table INVENTORY formated'''
    def get_user_inventory(self, user_id):
        parsed_id = str(user_id)
        try:
            # Get the inventory of the user
            user_inventory = self.__client.collection(self.__inventory).get_full_list(query_params={"filter": f"user_id='{parsed_id}'"})

            # Sort the data by user, item, and quantity
            sorted_inventory = sorted(
                user_inventory, 
                key=lambda x: (x.item_id, x.quantity)  # Accessing attributes with dot notation
            )

            # Extract relevant attributes (user, item, quantity)
            user_inventory_data = [
                {'item': record.item_id, 'quantity': record.quantity}  # Accessing attributes with dot notation
                for record in sorted_inventory
            ]
            
            return user_inventory_data
        except ClientResponseError as e:
            print(f"Ocurrió un error con la base de datos: {e}")
            print(f"Código de estado: {e.status}")
            print(f"Detalles: {e.response}")
        except Exception as e:
            print(f"Ha ocurrido un error: {e}")

    '''Returns a row from table USERS formated with expand ASPECTS and REWARDS table, rewards as unlocks'''
    def get_user_data(self, user_id:int) -> Dict:
        
        # Parse the id as string because pocketbase 
        # for some reason doesn't let you put the id as int 
        parsed_id = str(user_id)
        try:
            
            # Get the data of the user from database
            user_data = self.__client.collection(self.__users).get_one(parsed_id, {"expand": 'aspect, unlocks'})
            
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
                print(f"Ocurrió un error con la base de datos: {e}")
                print(f"Código de estado: {e.status}")
                print(f"Detalles: {e.response}")
                return
            print("No se encontraron datos en la consulta.")

        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    '''Convert PocketBase datetime string to epoch time.'''
    def __to_epoch(self, time_str: str) -> int:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return int(dt.timestamp())