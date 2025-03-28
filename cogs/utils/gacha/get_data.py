# TODO
from typing import Dict
from pocketbase import PocketBase
from discord import commands
from datetime import datetime

class GetData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = PocketBase('http://127.0.0.1:8090')
        self.users = 'USERS'
        self.aspects = 'ASPECTS'
        self.inventory = 'INVENTORY'
        self.items = 'ITEMS'
        self.rewards = 'REWARDS'

    '''Returns multiple rows from table INVENTORY formated'''
    def get_user_inventory(self, user_id):
        parsed_id = str(user_id)
        try:
            # Get the inventory of the user
            user_inventory = self.client.collection(self.inventory).get_full_list(query_params={"filter": f"user_id='{parsed_id}'"})

            # Sort the data by user, item, and quantity
            sorted_inventory = sorted(
                user_inventory, 
                key=lambda x: (x.user_id, x.item_id, x.quantity)  # Accessing attributes with dot notation
            )

            # Extract relevant attributes (user, item, quantity)
            user_inventory_data = [
                {'user': record.user_id, 'item': record.item_id, 'quantity': record.quantity}  # Accessing attributes with dot notation
                for record in sorted_inventory
            ]
            
            return user_inventory_data
        except Exception as e:
            print(f"Ha ocurrido un error: {e}")

    '''Returns a row from table USERS formated with expand ASPECTS and REWARDS table, rewards as unlocks'''
    def get_user_data(self, user_id:int) -> Dict:
        
        # Parse the id as string because pocketbase 
        # for some reason doesn't let you put the id as int 
        parsed_id = str(user_id)
        try:
            
            # Get the data of the user from database
            user_data = self.client.collection(self.users).get_one(parsed_id, {"expand": 'aspect, unlocks'})
            
            # Get the name of the aspect
            aspect_name = getattr(user_data.expand.get("aspect"), "name", None)
    
            # Get the name of the unlocked items
            unlocks_name = getattr(user_data.expand.get("unlocks"), "name", None)

            # Extract the data in a specific order
            ordered_data = {
                "id": int(user_data.id), # Parse ID as an int
                "username": user_data.username,
                "aspect": aspect_name,
                "level": user_data.level,
                "notes": user_data.notes,
                "knowledge": user_data.knowledge,
                "last_message": self.to_epoch(user_data.last_message), # Parse to epoch time ('cause I like it)
                "last_gacha": self.to_epoch(user_data.last_gacha),
                "pity_counter": user_data.pity_counter,
                "unlocks": unlocks_name
            }
            
            return ordered_data
        except Exception as e:
            print(F"Ha ocurrido un error: {e}")

    '''Convert PocketBase datetime string to epoch time.'''
    def to_epoch(self, time_str: str) -> int:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return int(dt.timestamp())

async def setup(bot):
    await bot.add_cog(GetData(bot))