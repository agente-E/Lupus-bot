import discord
from discord.ext import commands
from discord import app_commands

class UnpanicButton(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @bot.tree.command(name="unpanicbutton", description="Acaba el modo de cuarentena admin")
        @app_commands.default_permissions(administrator=True)
        async def unpanic(interaction: discord.Interaction):
            
            await interaction.response.defer()

            # Gets the guild from the interaction
            guild = interaction.guild 

            # Find quarantine role
            quarantine_role = discord.utils.get(guild.roles, name="Cuarentena")
            if quarantine_role is None:
                await interaction.followup.send("Error: No se encontró el rol 'Cuarentena'.", ephemeral=True)
                return

            # Remove quaranitne role from all users
            removed_members = []
            for member in guild.members:
                if quarantine_role in member.roles:
                    try:
                        await member.remove_roles(quarantine_role)
                        removed_members.append(member.name)
                    except discord.Forbidden:
                        print(f"No se pudo remover el rol de {member.name} (permiso denegado).")

            # When finished, inform 
            await interaction.followup.send(
                f"Modo cuarentena desactivado. Se ha eliminado el rol a {len(removed_members)} usuarios.", ephemeral=False
            )
            print(f"Modo cuarentena desactivado. Se ha eliminado el rol a {len(removed_members)} usuarios.")

async def setup(bot):
    await bot.add_cog(UnpanicButton(bot))
