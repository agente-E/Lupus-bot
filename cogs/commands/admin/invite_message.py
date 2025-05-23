import discord
from discord.ext import commands
from discord import app_commands

class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_link = "https://discord.gg/deephsp"  # Personalized invite link
        self.image_path = "assets/images/TinkyWinky.png"  # Path to the image used for the embed

    @app_commands.command(name="invite", description="Genera un mensaje de invite (admin)")
    @app_commands.default_permissions(administrator=True)
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def invite_command(self, interaction: discord.Interaction):
        
        # Create the embed
        embed = discord.Embed(
            title="¡Invitación al servidor!",
            description=( 
                ".•° ✿ °•..•° ✿ °•..•° ✿ °•.\n"
                "¡Esta es la invitación del servidor! Con ella, puedes invitar a tus amigos y pasar un buen rato en esta comunidad basada en Deepwoken.\n"
                f"`{self.invite_link}`\n"
                ".•° ✿ °•..•° ✿ °•..•° ✿ °•."
            ),
            color=discord.Color.purple(),
        )

        # Set the image for the embed
        embed.set_thumbnail(url=f"attachment://TinkyWinky.png")
        try:
            
            # Open the image
            with open(self.image_path, "rb") as image_file:
                file = discord.File(image_file, filename="TinkyWinky.png")
                
                # Send the embed with the file
                await interaction.response.send_message(embed=embed, file=file)
        except FileNotFoundError:
            
            # If the image can't be loaded, response with error
            await interaction.response.send_message(
                "No se pudo encontrar la imagen para la invitación. Por favor, revisa la ruta.",
                ephemeral=True,
            )
            
async def setup(bot):
    await bot.add_cog(Invite(bot))
