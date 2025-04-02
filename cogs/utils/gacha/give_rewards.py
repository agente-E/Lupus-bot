# TODO
import random
import discord
from discord.ext import commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase

class GiveRewards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__booster_role_name = "Server Booster"

    async def check_and_level_up(self, user_data, message:discord.Message = None, interaction:discord.Interaction = None):
        if message is None and interaction is None: 
            return
        user = message.author.id if message is not None else interaction.user.id
        channel = message.channel if message is not None else interaction.channel 
        experiencia = user_data['experiencia']
        nivel = user_data['nivel']
        exp_requerida = (100 + nivel * 20)
        while experiencia >= exp_requerida:
            experiencia -= exp_requerida
            exp_requerida = (100 + nivel * 20)
            nivel += 1
        if nivel > user_data['nivel']:
            user_data['nivel'] = nivel
            user_data['experiencia'] = experiencia
            await channel.send(f"¡<@{user}> ha subido al nivel {nivel}!")
        return user_data


    async def give_time_reward(self, user_data: dict, server_booster_role):
        database = self.bot.get_cog("InteractWithDatabase") # type: InteractWithDatabase
        aspects = database.get_aspects()
        aspect = user_data['aspect']
        
        booster_multiplier = 3 if server_booster_role else 1

        # Base reward ranges for notes
        notes_rewards = {
            "Canor": (5, 10),
            "Etrean": (0, 10),
            "default": (1, 5),
        }

        # Base reward ranges for experience
        experience_rewards = {
            "Adret": (1, 5),
            "default": (1, 5),
        }

        user_data = await check_and_level_up(user_data)

async def setup(bot):
    await bot.add_cog(GiveRewards(bot))
