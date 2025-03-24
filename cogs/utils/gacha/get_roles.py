import discord
import requests
from discord.ext import commands
class GetRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pb_url = 'http://localhost:8090'

    def get_roles(self):
        try:
            roles_url = f'{self.pb_url}/api/collections/ROLES/records'
            response = requests.get(roles_url)
            roles_data = response.json()
            return roles_data
        except Exception as e:
            return {f"{e}"}

async def setup(bot):
    await bot.add_cog(GetRoles(bot))