import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View

class PanicBUtton(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
        @bot.tree.command(name="panicbutton", description="Empieza el modo cuarentena admin")
        @app_commands.default_permissions(administrator=True)
        async def panic(interaction: discord.Interaction):
            await interaction.response.defer()

            # Create the embed
            embed = discord.Embed(
                title="Confirmación",
                description="¿Estás seguro que quieres activar el modo cuarentena?",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Explicación",
                value="Esto provocará que todos los usuarios tengan temporalmente el rol de cuarentena e impedirá la posibilidad de usar el servidor temporalmente.",
                inline=False
            )

            # Create confirmation button
            button = Button(label="Confirmar", style=discord.ButtonStyle.danger)

            # Handle button interaction
            async def confirmation_button_callback(button_interaction: discord.Interaction):
                await button_interaction.response.send_message(
                    f"Modo cuarentena activado.", ephemeral=False
                )

                guild = button_interaction.guild

                # Get quarantine role
                quarantine_role = discord.utils.get(guild.roles, name="Cuarentena")
                
                # If it can't find the role
                if quarantine_role is None:
                    await button_interaction.response.send_message("Error: No se encontró el rol 'Cuarentena'.", ephemeral=True)
                    return

                # Add quarantine role to all users in server
                added_members = []
                for member in guild.members:
                    if quarantine_role not in member.roles:
                        try:
                            await member.add_roles(quarantine_role)
                            added_members.append(member.name)
                            print(f"Rol añadido a {member.name}")
                        except discord.Forbidden:
                            print(f"No se pudo agregar el rol a {member.name} (permiso denegado).")

                print(f"Modo cuarentena activado. {len(added_members)} usuarios han sido afectados.")

            # Assign the callback to the function
            button.callback = confirmation_button_callback

            # Create the view with the button (send embed)
            view = View()
            view.add_item(button)

            await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(PanicBUtton(bot))
