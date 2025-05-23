# TODO
import random
import discord
from discord.ext import commands

class GiveRewards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_level_up(self, data: dict) -> dict:
        """
        Levels up the level of the user by their remaining exp.

        Arguments:
            data (dict): The input data containing user stats.

        Returns:
            data (dict): Same input data but leveled up.
        """
        experience = data['experience']
        level = data['level']
        required_exp = (100 + level * 20)
        while experience >= required_exp:
            experience -= required_exp
            required_exp = (100 + level * 20)
            level += 1
        if level > data['level']:
            data['level'] = level
            data['experience'] = experience
        return data
    
    async def give_call_reward(self, data: dict, server_booster_role = None) -> dict:
        pass
        # TODO

    async def give_message_reward(self, data: dict, server_booster_role = None) -> dict:
        """
        Gives a random amount of exp and notes, with server boost role gives more.

        Arguments:
            data (dict): The input data containing user stats.
            role: If the user has the server booster role. Default none.

        Returns:
            data (dict): Data with rewards applied and leveled up.
        """
        aspect = data['aspect']

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
        data['notes'] += random.randint(*notes_reward) * booster_multiplier
        exp_multiplier = 2 if aspect == 'Adret' else 1
        data['experience'] += (random.randint(*exp_reward) * exp_multiplier) * booster_multiplier
        data = await self.check_level_up(data=data) 
        
        return data

async def setup(bot):
    await bot.add_cog(GiveRewards(bot))