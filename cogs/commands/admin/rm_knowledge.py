import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase

class RmKnowledge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="rmknowledge", description="Elimina una cantidad de Knowledge al usuario indicado admin")
    @app_commands.default_permissions(administrator=True)
    async def rm_knowledge(self, interaction:discord.Interaction, usuario: discord.Member, cantidad: int):

        # Get cog from the bot to interact with the database
        database = self.bot.get_cog("InteractWithDatabase") # type: InteractWithDatabase

        user_data = await database.get_user_data(user_id=usuario)
        user_data['knowledge'] -= cantidad
        database.save_user_data(user_id=user_data['id'], data=user_data)
        await interaction.response.send_message(f"{cantidad} extraidos al usuario {usuario.name}", ephemeral=True)
        try:
            if cantidad <= 1:
                await usuario.send(f"Se te han quitado {cantidad} <:knowledge:1338469359906979874>")
            else:
                await usuario.send(f"Se te han quitado {cantidad} <:knowledge:1338469359906979874>")
        except discord.Forbidden:
            print(f"No se pudo enviar DM a {usuario.name}.")

async def setup(bot):
    await bot.add_cog(RmKnowledge(bot))
