import discord
from discord.ext import commands
from discord import app_commands
from cogs.utils.gacha.interact_with_data import InteractWithDatabase

class AddNotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="addnotes", description="Añade una cantidad de Notas al usuario indicado (admin)")
    @app_commands.default_permissions(administrator=True)
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def add_notes(self, interaction:discord.Interaction, usuario: discord.Member, cantidad: int):

        # Get cog from the bot to interact with the database
        database = self.bot.get_cog("InteractWithDatabase") # type: InteractWithDatabase
        
        user_data = await database.get_user_data(user_id=usuario.id)
        user_data['notes'] += cantidad
        await database.save_user_data(user_id=user_data['id'], data=user_data)
        rewards = await database.get_rewards()
        await database.remove_item_user(user_id=interaction.user.id, item_name='Cambiar Aspecto', quantity=1)
        await interaction.response.send_message(f"{cantidad} añadidos al usuario {usuario.name}", ephemeral=True)
        try:
            if cantidad <= 1:
                await usuario.send(f"Se te ha añadido {cantidad} <:note:1338471019702259763>")
            else:
                await usuario.send(f"Se te han añadido {cantidad} <:note:1338471019702259763>")
        except discord.Forbidden:
            print(f"No se pudo enviar DM a {usuario.name}.")

async def setup(bot):
    await bot.add_cog(AddNotes(bot))
