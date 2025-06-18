import random
import discord
import time
from datetime import timedelta
from discord import app_commands
from discord.utils import format_dt
from discord.ui import View, Button
from discord.ext import commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild
from cogs.utils.gacha.give_rewards import GiveRewards
class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
        self.checker: CheckGuild = None
        self.giver: GiveRewards = None
        self.pity_threshold = self.bot.config.get("gacha_settings", {})["pity_threshold"]
        self.price_per_roll = self.bot.config.get("gacha_settings", {})["price_per_roll"]
        self.free_cooldown = self.bot.config.get("gacha_settings", {})["free_cooldown"]

    @app_commands.command(name="roll", description="Realiza una tirada de gacha")
    async def roll(self, interaction: discord.Interaction):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker
        self.giver = self.bot.get_cog("GiveRewards") if self.giver is None else self.giver

        # Don't permit to use the bot out the main server
        if await self.checker.check_guild(interaction=interaction) == False:
            return
        
        user_data = await self.database.get_user_data(user_id=interaction.user.id)
        knowledge_to_add = 1
        pity_threshold = self.pity_threshold
        cooldown = self.free_cooldown
        rolls = 1
        aspect = user_data['aspect']
        discount = 1
        price_per_roll = self.price_per_roll
        price_for_ten = round(price_per_roll * 8)

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
            case 'Ganymede':
                discount = 0.5
                price_per_roll = round(self.price_per_roll * discount)
                price_for_ten = round(price_per_roll * 8 * discount)

        current_time = int(time.time())

        # The user has the pity
        if user_data['last_gacha'] == None or current_time - user_data['last_gacha'] > cooldown:
            await self.database.update_last_gacha(interaction.user.id, current_time)
            roll_rewards = []
            knowledge_added = 0
            roll_rewards = await self.do_roll(user_data, pity_threshold, rolls)
            knowledge_added += knowledge_to_add * rolls
            await self.database.increment_knowledge(interaction.user.id, knowledge_to_add)
                
            # ! Add logic to level up (TODO)

            # Give the rewards to the user
            await self.give_rewards(rewards=roll_rewards, interaction=interaction)            
            rewards_display = [{
                "name": roll_reward['name'],
                "probability": roll_reward['probability'],
                "emoji": roll_reward['emoji'],
                "pity_reward": roll_reward['pity_reward']
            } for roll_reward in roll_rewards]

            reward_names = [roll_reward['name'] for roll_reward in roll_rewards]

            rarest_probability = min(r['probability'] for r in rewards_display)
            embed_color = self.get_probability_color(rarest_probability)

            embed = discord.Embed(
                title=f"Tirada de Gacha de {interaction.user.name}",
                color=embed_color
            )
            
            value = "\n".join(f"{reward['name']} {reward['emoji'] if reward['emoji'] else ''} - `{reward['probability']}%`" for reward in rewards_display)

            embed.add_field(
                name="Recompensas obtenidas",
                value=value,
                inline=True
            )

            embed.add_field(
                name="Contador de Pity",
                value=f"{user_data['pity_counter']} / {pity_threshold}",
                inline=False
            )

            embed.add_field(name="Conocimiento acumulado", value=f"{user_data['knowledge'] + knowledge_added}<:knowledge:1338469359906979874> <:Up:1379949622172057710> {knowledge_added}<:knowledge:1338469359906979874>", inline=True)
            embed.add_field(name="Notas restantes", value=f"{user_data['notes']}<:note:1338471019702259763> <:Same:1379951126874685510>", inline=False)
            if any(reward['pity_reward'] for reward in rewards_display):                
                embed.set_footer(text=("¡Has obtenido una recompensa de Pity!"))
            await self.database.save_user_history(interaction.user.id, reward_names)
            await interaction.response.send_message(embed=embed)
        else:
            time_left = cooldown - (current_time - user_data['last_gacha']) 
            minutes_left = (time_left % 3600) // 60
            seconds_left = time_left % 60
            time_left = timedelta(minutes=minutes_left, seconds=seconds_left)
            time_remaining = format_dt(discord.utils.utcnow() + time_left, style='R')
            embed = discord.Embed(
                title="Tirada Gratuita",
                description=f"{interaction.user.mention}, ya has utilizado tu tirada gratuita.\n"
                            f"Tiempo restante para la siguiente tirada gratuita: {time_remaining}",
                color=discord.Color.red()
            )
            embed.add_field(name="Tienes:", value=f"{user_data['notes']} <:note:1338471019702259763>", inline=True)
            button_spend = Button(
                label=f"{price_per_roll} x1",
                emoji="<:note:1338471019702259763>",
                style=discord.ButtonStyle.green
            )

            button_spendx10 = Button(
                label=f"{price_for_ten} x10",
                emoji="<:note:1338471019702259763>",
                style=discord.ButtonStyle.blurple
            )

            view = View(timeout=60)
            view.add_item(button_spend)
            view.add_item(button_spendx10)

            async def on_spend(interaction: discord.Interaction):
                if interaction.user.id != interaction.user.id:
                    await interaction.response.send_message("Este botón no es para ti.", ephemeral=True)
                    return
                
                if user_data['notes'] < price_per_roll:
                    await interaction.response.send_message(f"{interaction.user.mention}, no tienes suficientes <:note:1338471019702259763> para hacer la tirada.", ephemeral=False)
                    return

                await self.database.decrease_notes(user_id=interaction.user.id, notes=price_per_roll)
                user_data['notes'] -= price_per_roll
                roll_rewards = []
                knowledge_added = 0
                roll_rewards = await self.do_roll(user_data, pity_threshold, 1)
                knowledge_added += knowledge_to_add * 1
                await self.database.increment_knowledge(interaction.user.id, knowledge_to_add)
                    
                # ! Add logic to level up (TODO)

                # Give the rewards to the user
                await self.give_rewards(rewards=roll_rewards, interaction=interaction)                
                
                rewards_display = [{
                    "name": roll_reward['name'],
                    "probability": roll_reward['probability'],
                    "emoji": roll_reward['emoji'],
                    "pity_reward": roll_reward['pity_reward']
                } for roll_reward in roll_rewards]

                reward_names = [roll_reward['name'] for roll_reward in roll_rewards]

                rarest_probability = min(r['probability'] for r in rewards_display)
                embed_color = self.get_probability_color(rarest_probability)

                embed = discord.Embed(
                    title=f"Tirada de Gacha de {interaction.user.name}",
                    color=embed_color
                )
                
                value = "\n".join(f"{reward['name']} {reward['emoji'] if reward['emoji'] else ''} - `{reward['probability']}%`" for reward in rewards_display)

                embed.add_field(
                    name="Recompensas obtenidas",
                    value=value,
                    inline=True
                )

                embed.add_field(
                    name="Contador de Pity",
                    value=f"{user_data['pity_counter']} / {pity_threshold}",
                    inline=False
                )
                embed.add_field(name="Conocimiento acumulado", value=f"{user_data['knowledge'] + knowledge_added}<:knowledge:1338469359906979874> <:Up:1379949622172057710> {knowledge_added}<:knowledge:1338469359906979874>", inline=True)
                embed.add_field(name="Notas restantes", value=f"{user_data['notes']}<:note:1338471019702259763> <:Down:1379950128349052928> {price_per_roll}<:note:1338471019702259763>", inline=False)
                if any(reward['pity_reward'] for reward in rewards_display):                
                    embed.set_footer(text=("¡Has obtenido una recompensa de Pity!"))
                await self.database.save_user_history(interaction.user.id, reward_names)
                await interaction.response.send_message(embed=embed, view=view)

            async def on_spendx10(interaction: discord.Interaction):
                if interaction.user.id != interaction.user.id:
                    await interaction.response.send_message("Este botón no es para ti.", ephemeral=True)
                    return
                
                if user_data['notes'] < price_for_ten:
                    await interaction.response.send_message(f"{interaction.user.mention}, no tienes suficientes <:note:1338471019702259763> para hacer la tirada.", ephemeral=False)
                    return

                await self.database.decrease_notes(user_id=interaction.user.id, notes=price_for_ten)
                user_data['notes'] -= price_for_ten
                roll_rewards = []
                knowledge_added = 0
                roll_rewards = await self.do_roll(user_data, pity_threshold, 10)
                knowledge_added += knowledge_to_add * 10
                await self.database.increment_knowledge(interaction.user.id, knowledge_to_add)

                # ! Add logic to level up (TODO)

                # Give the rewards to the user
                await self.give_rewards(rewards=roll_rewards, interaction=interaction)
                
                rewards_display = [{
                    "name": roll_reward['name'],
                    "probability": roll_reward['probability'],
                    "emoji": roll_reward['emoji'],
                    "pity_reward": roll_reward['pity_reward']
                } for roll_reward in roll_rewards]

                reward_names = [roll_reward['name'] for roll_reward in roll_rewards]

                rarest_probability = min(r['probability'] for r in rewards_display)
                embed_color = self.get_probability_color(rarest_probability)

                embed = discord.Embed(
                    title=f"Tirada de Gacha de {interaction.user.name}",
                    color=embed_color
                )

                value = "\n".join(f"{reward['name']} {reward['emoji'] if reward['emoji'] else ''} - `{reward['probability']}%`" for reward in rewards_display)

                embed.add_field(
                    name="Recompensas obtenidas",
                    value=value,
                    inline=True
                )

                embed.add_field(
                    name="Contador de Pity",
                    value=f"{user_data['pity_counter']} / {pity_threshold}",
                    inline=False
                )

                embed.add_field(name="Conocimiento acumulado", value=f"{user_data['knowledge'] + knowledge_added}<:knowledge:1338469359906979874> <:Up:1379949622172057710> {knowledge_added}<:knowledge:1338469359906979874>", inline=True)
                embed.add_field(name="Notas restantes", value=f"{user_data['notes']}<:note:1338471019702259763> <:Down:1379950128349052928> {price_for_ten}<:note:1338471019702259763>", inline=False)
                if any(reward['pity_reward'] for reward in rewards_display):                
                    embed.set_footer(text=("¡Has obtenido una recompensa de Pity!"))
                await self.database.save_user_history(interaction.user.id, reward_names)
                await interaction.response.send_message(embed=embed, view=view)

            button_spend.callback = on_spend
            button_spendx10.callback = on_spendx10
            await interaction.response.send_message(embed=embed, view=view)

    async def give_rewards(self, rewards: list, interaction: discord.Interaction):
        for reward in rewards:
            match reward['type']:
                case 'Experience':
                    await self.database.increment_exp(interaction.user.id, reward['value'])
                case 'Role':
                    await self.database.attach_role(interaction.user.id, reward)
                    role = discord.utils.get(interaction.guild.roles, name=reward['name'])
                    if role:
                        await interaction.user.add_roles(role)
                    else:
                        print(f"Role {reward['name']} not found")
                case 'Item':
                    await self.database.add_item_user(interaction.user.id, reward['name'], 1) 

    async def do_roll(self, user_data: dict, pity_threshold: int, rolls: int):
        rewards = await self.database.get_rewards()
        rare_bonus = 1.5 if user_data['aspect'] == 'Chrysid' else 1

        def calculate_pity_chance(pity_counter):
            base_pity_rate = 0.006

            soft_pity_start = int(pity_threshold * 0.80) # Start incrementing at 80% of the threshold

            if pity_counter >= pity_threshold - 1:
                return 1.0

            if pity_counter < soft_pity_start:
                return base_pity_rate

            progress = (pity_counter - soft_pity_start) / (pity_threshold - soft_pity_start)

            progress = max(0.0, progress)

            increment_factor = (progress ** 3) * 15

            pity_chance = base_pity_rate + (1.0 - base_pity_rate) * increment_factor / 15

            return min(pity_chance, 1.0)

        def adjusted_weight(r):
            return r['probability'] * rare_bonus if r['probability'] <= 30 else r['probability']

        roll_results = []
        for _ in range(rolls):
            available_rewards = [reward for reward in rewards if reward['name'] not in user_data['unlocks']]
            pity_chance = calculate_pity_chance(user_data['pity_counter'])

            is_pity_roll = random.random() < pity_chance
            if is_pity_roll:
                available_pity_rewards = [
                    reward for reward in available_rewards
                    if reward['pity_reward'] and (not reward['unlockable'] or reward['name'] not in user_data['unlocks'])
                ]

                chosen_reward = random.choices(
                    available_pity_rewards,
                    weights=[adjusted_weight(reward) for reward in available_pity_rewards],
                    k=1
                )[0]
                if chosen_reward['unlockable']:
                    user_data['unlocks'].append(chosen_reward['name'])

                await self.database.reset_pity_counter(user_data['id'])
                user_data['pity_counter'] = 0

            else:
                available_non_pity_rewards = [
                    reward for reward in available_rewards
                    if not reward['pity_reward'] and (not reward['unlockable'] or reward['name'] not in user_data['unlocks'])
                ]

                chosen_reward = random.choices(
                    available_non_pity_rewards,
                    weights=[adjusted_weight(reward) for reward in available_non_pity_rewards],
                    k=1
                )[0]

                if chosen_reward['unlockable']:
                    user_data['unlocks'].append(chosen_reward['name'])

                if chosen_reward['pity_reward']:
                    await self.database.reset_pity_counter(user_data['id'])
                    user_data['pity_counter'] = 0

                else:
                    await self.database.increment_pity_counter(user_data['id'])
                    user_data['pity_counter'] += 1

            roll_results.append(chosen_reward)
        return roll_results

    def get_probability_color(self, probability) -> discord.Color:
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
