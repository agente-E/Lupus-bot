import random
import discord
import time
from discord import app_commands
from discord.ext import commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 776247434384375818
        self.pity_threshold = self.bot.config.get("gacha_settings", {})["pity_threshold"]
        self.price_per_roll = self.bot.config.get("gacha_settings", {})["price_per_roll"]
        self.free_cooldown = self.bot.config.get("gacha_settings"), {}["free_cooldown"]

    @app_commands.command(name="roll", description="Realiza una tirada de gacha")
    async def roll(self, interaction: discord.Interaction):
        
        # Don't permit to use the bot out the main server
        if interaction.guild is None or interaction.guild.id == self.guild_id:
            await interaction.response.send_message("No puedes usar este comando aquí. Por favor, usa un canal del servidor https://discord.com/channels/776247434384375818/1312478372357603399.")
            return
        
        # Get cog from the bot to interact with the database
        database = self.bot.get_cog("InteractWithDatabase") # type: InteractWithDatabase
        user_data = await database.get_user_data(user_id=interaction.user.id)
        current_time = int(time.time())
        aspect = user_data['aspect']
        match aspect:
            case 'Vesperian':
                cooldown = self.free_cooldown / 2
            case 'Primal Vesperian':
                cooldown = round(self.free_cooldown / 3.33)
            case _:
                cooldown = self.free_cooldown
        if current_time - user_data['last_gacha'] > cooldown: 
            roll_rewards = [{}]
            user_data['last_gacha'] = current_time
            rolls = 5 if user_data['aspect'] == 'Auroran' else 3 if user_data['aspect'] == 'Gremor' else 1

            
        # # Get the cog from the bot to give rewards
        # giver = self.bot.get_cog("GiveRewards") # type: GiveRewards


# Add cog to the bot
async def setup(bot):
    await bot.add_cog(Roll(bot))
