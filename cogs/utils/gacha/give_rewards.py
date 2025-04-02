# TODO
import random
import discord
from discord.ext import commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase

class GiveRewards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_level_up(self, data: dict, message:discord.Message = None, interaction:discord.Interaction = None):
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

    '''Gives the user a random amount of notes and exp when called'''
    async def give_message_reward(self, user_data: dict, server_booster_role) -> dict:
        database = self.bot.get_cog("InteractWithDatabase") # type: InteractWithDatabase
        aspects = database.get_aspects()
        aspect = user_data['aspect']

        booster_multiplier = 3 if server_booster_role else 1

        exp_reward = (1, 5)

        match aspect:
            case 'Canor':
                notes_reward = (5, 10)
            case 'Etrean':
                notes_reward = (0, 10)
            case _:
                notes_reward = (1, 5)

        # Generate random rewards
        user_data['notes'] += random.randint(*notes_reward) * booster_multiplier
        exp_multiplier = 2 if aspect == 'Adret' else 1
        user_data['experience'] += (random.randint(*exp_reward) * exp_multiplier) * booster_multiplier
        
        await self.check_level_up()

async def setup(bot):
    await bot.add_cog(GiveRewards(bot))
