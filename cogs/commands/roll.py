import random
import discord
import time
from discord import app_commands
from discord.ui import View, Button
from discord.ext import commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
        self.checker: CheckGuild = None
        self.pity_threshold = self.bot.config.get("gacha_settings", {})["pity_threshold"]
        self.price_per_roll = self.bot.config.get("gacha_settings", {})["price_per_roll"]
        self.free_cooldown = self.bot.config.get("gacha_settings", {})["free_cooldown"]

    @app_commands.command(name="roll", description="Realiza una tirada de gacha")
    async def roll(self, interaction: discord.Interaction):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker

        # Don't permit to use the bot out the main server
        if await self.checker.check_guild(interaction=interaction) == False:
            return
        
        user_data = await self.database.get_user_data(user_id=interaction.user.id)
        knowledge_to_add = 1
        pity_threshold = self.pity_threshold
        cooldown = self.free_cooldown
        rolls = 1
        aspect = user_data['aspect']
        match aspect:
            case 'Vesperian':
                cooldown = self.free_cooldown / 2
            case 'Primal Vesperian':
                cooldown = round(self.free_cooldown / 3.33)
            case 'Auroran':
                rolls = 5
            case 'Gremor':
                rolls = 3
            case 'Tiran':
                knowledge_to_add = 5
            case 'Celtor':
                pity_threshold -= 30
        print(user_data) # ! Debug
        current_time = int(time.time())
        if user_data['last_gacha'] == None or current_time - user_data['last_gacha'] > cooldown: 
            await self.database.update_last_gacha(interaction.user.id, current_time)
            roll_rewards = []
            for _ in range(rolls):
                roll_rewards.append(await self.do_roll(user_data, pity_threshold))
                await self.database.increment_knowledge(interaction.user.id, knowledge_to_add)
            
            # ! Add logic to level up

            rewards_display = [{
                "name": roll_reward['name'],
                "probability": roll_reward['probability']
            } for roll_reward in roll_rewards]

            rarest_probability = min(r['probability'] for r in rewards_display)
            embed_color = self.get_probability_color(rarest_probability)

        embed = discord.Embed(
            title=f"Tirada de Gacha de {interaction.user.name}",
            color=embed_color
        )

        value = "\n".join(f"{reward['name']} - {reward['probability']}%" for reward in rewards_display)

        embed.add_field(
            name="Recompensas obtenidas",
            value=value or "Nada (Porqué tienes esto??)",
            inline=True
        )

        embed.add_field(
            name="Contador de Pity",
            value=f"{user_data['pity_counter']} / {pity_threshold}",
            inline=False
        )

        embed.add_field(name="Conocimiento acumulado", value=f"{user_data['knowledge']} <:knowledge:1338469359906979874>", inline=True)
        embed.add_field(name="Notas restantes", value=f"{user_data['notes']} <:note:1338471019702259763>", inline=False)
    
        await interaction.response.send_message(embed=embed)


    async def do_roll(self, user_data: dict, pity_threshold: int):
        rewards = await self.database.get_rewards()
        pity_threshold = self.pity_threshold - 30 if user_data['aspect'] == 'Celtor' else self.pity_threshold
        rare_bonus = 1.5 if user_data['aspect'] == 'Chrysid' else 1

        available_rewards = [reward for reward in rewards if reward['name'] not in user_data['unlocks']]

        def adjusted_weight(r):
            if r['probability'] <= 30:
                return r['probability'] * rare_bonus
            return r['probability']
        
        # Check if the user has reached the pity
        if user_data['pity_counter'] >= pity_threshold:
            
            available_pity_rewards = [
                reward for reward in available_rewards
                if reward['pity_reward'] and (not reward['unlockable'] or reward['name'] not in user_data['unlocks'])
            ]
            
            chosen_reward = random.choices(
                available_pity_rewards,
                weights=[adjusted_weight(reward) for reward in available_pity_rewards],
                k=1
            )[0]
            await self.database.reset_pity_counter(user_data['id'])
            return chosen_reward

        chosen_reward = random.choices(
            available_rewards,
            weights=[adjusted_weight(reward) for reward in available_rewards],
            k=1
        )[0]
        await self.database.increment_pity_counter(user_data['id'])
        return chosen_reward

    def get_probability_color(self, probability):
        match probability:
            case p if p <= 2.3:
                return discord.Color.red()
            case p if p <= 15:
                return discord.Color.gold()
            case p if p <= 45:
                return discord.Color.purple()
            case p if p <= 80:
                return discord.Color.blue()
            case _:
                return discord.Color.green()
        
# Add cog to the bot
async def setup(bot):
    await bot.add_cog(Roll(bot))
