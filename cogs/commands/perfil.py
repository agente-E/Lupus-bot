import discord
from copy import deepcopy
from discord.ext import commands
from discord import app_commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild
from cogs.utils.gacha.give_rewards import GiveRewards

class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
        self.checker: CheckGuild = None

    @app_commands.command(name="perfil", description="Muestra el perfil de un usuario (notas, nivel, aspecto...)")
    @app_commands.describe(usuario="Usuario del que ver el perfil (opcional)")
    async def perfil(self, interaction: discord.Interaction, usuario: discord.User = None):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker

        if await self.checker.check_guild(interaction=interaction) == False:
            return
        
        # Make the interacter user as default
        if usuario is None:
            usuario = interaction.user
               
        # Get the data for the inventory color
        user_data = await self.database.get_user_data(user_id=usuario.id)
        
        # Check if the user can level up to evade visual problems (like have more xp than needed to lvl up, visual error)
        giver = self.bot.get_cog("GiveRewards") # type: GiveRewards
        previous_level = user_data['level']
        user_data = await giver.check_level_up(data=user_data)
        cuser_data = user_data.copy()
        await self.database.save_user_data(user_id=usuario.id, data=cuser_data)

        # Checks if the user has leveled up and save the data
        if user_data['level'] > previous_level:
            await interaction.channel.send(f"¡<@{interaction.user.id}>, has subido al nivel {user_data['level']}!")

        # Parse the data for the embed
        last_gacha_timestamp = user_data['last_gacha'] if user_data['last_gacha'] is not None else 0
        if last_gacha_timestamp > 0:
            
            # Create relative discord timestamp
            last_gacha_str = f"<t:{int(last_gacha_timestamp)}:R>"  # Formato relativo ("hace X minutos")
        else:
            last_gacha_str = "Nunca"

        rewards = await self.database.get_rewards()
        unlock_names = user_data['unlocks']

        # Filter only Role-type rewards
        role_rewards = [r for r in rewards if r['type'] == 'Role']
        role_names = {r['name'] for r in role_rewards}

        # Check which unlocked items are Role-type
        unlocked_roles = [name for name in unlock_names if name in role_names]

        # Calculate percentage safely
        if not role_rewards:
            percentage = 0.0
        else:
            percentage = round(((len(unlocked_roles) / len(role_rewards)) * 100), 2)

        user_aspect = user_data['aspect']

        # Get the colors from database
        aspects = await self.database.get_aspects()
        aspect_data = next((aspect for aspect in aspects if aspect['name'] == user_aspect), None)
        color = discord.Color(int(aspect_data.get('color', "#000000")[1:], 16))
        embed = discord.Embed(title=f"Perfil de {usuario.name}", color=color)
        try:
            avatar_url = usuario.avatar.url
        except AttributeError:
            avatar_url = 'assets/images/defaultAvatar.png'
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="<:etrea:1338471807333957632>Aspecto", value=str(user_data['aspect']), inline=False)
        embed.add_field(name="<:note:1338471019702259763> Notas", value=str(user_data['notes']), inline=True)
        embed.add_field(name="<:knowledge:1338469359906979874> Conocimiento", value=str(user_data['knowledge']), inline=True)
        embed.add_field(name="<:exp:1338472338370596954> Experiencia", value=str(user_data['experience']), inline=True)
        embed.add_field(name="Nivel", value=str(user_data['level']), inline=True)
        if user_data['aspect'] == "Celtor":
            embed.add_field(name="Pity Counter", value=f"{user_data['pity_counter']} / 60", inline=True)
        else:
            embed.add_field(name="Pity Counter", value=f"{user_data['pity_counter']} / 90", inline=True)
        embed.add_field(name="Última tirada", value=last_gacha_str, inline=True)
        embed.add_field(name="Porcentaje de obtención", value=f'{percentage}%', inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Perfil(bot))