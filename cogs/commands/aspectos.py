import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
from cogs.utils.gacha.interact_with_data import InteractWithDatabase

class Aspectos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_map = {
            "Adret": "😊",
            "Auroran": "<:Auroran:1345924564659601418>",
            "Canor": "<:Canor:1342040477272375360>",
            "Capra": "<:Capra:1341356908032036925>",
            "Celtor": "<:Celtor:1341356917397913670>",
            "Chrysid": "<:Chrysid:1341356925551644683>",
            "Etrean": "<:Etrean:1341356935483752508>",
            "Felinor": "<:Felinor:1341356942475530240>",
            "Ganymede": "<:Ganymede:1341356948636962897>",
            "Gremor": "<:Gremor:1341666668245553153>",
            "Khan": "<:Khan:1341356954722898000>",
            "Lightborn": "😊",
            "Primal Vesperian": "<:PrimalVesperian:1346139457056800828>",
            "Tiran": "<:Tiran:1341356961001635882>",
            "Vesperian": "<:Vesperian:1341356967750402099>",
        }

    @app_commands.command(name="aspectos", description="Muestra los aspectos disponibles")
    async def aspectos(self, interaction: discord.Interaction):
        
        # Get cog from the bot to interact with the database
        database = self.bot.get_cog("InteractWithDatabase") # type: InteractWithDatabase
        
        aspects = database.get_aspects()
        
        aspect_options = [
            (aspect['name'], self.emoji_map.get(aspect['name'], "❓"))
            for aspect in aspects
        ]

        # Create the embed
        embed = discord.Embed(
            title="Aspectos Disponibles",
            description="Selecciona sobre qué aspecto quieres ver información",
            color=discord.Color.purple()
        )

        select_menu = Select(
            placeholder="Selecciona un aspecto",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label=name, emoji=emoji)
                for name, emoji in aspect_options
            ]
        )
        async def select_callback(interaction: discord.Interaction):
            selection = select_menu.values[0]
            aspect_data = next((aspect for aspect in aspects if aspect['name'] == selection), None)
            color = discord.Color(int(aspect_data.get('color', "#000000")[1:], 16))
            embed = discord.Embed(title=f'{selection}', colour=color)
            if selection == 'Primal Vesperian':
                image_path = 'assets/images/icons/Primal_Vesperian.png'
            else:
                image_path = f"assets/images/icons/{selection}.png"
            icon = discord.File(image_path)
            print(aspect_data.get('passive'))
            embed.set_thumbnail(url=f"attachment://{image_path.split('/')[-1]}")
            embed.add_field(name="Descripción", value=aspect_data.get('description', "No hay descripción para este aspecto"), inline=False)
            embed.add_field(name="Pasiva", value=aspect_data.get('passive', "No hay pasiva para este aspecto"), inline=False)
            embed.add_field(name="Probabilidad", value=f'{aspect_data.get('probability', 0.0)}%', inline=False)
            if aspect_data.get('exclusive', None):
                embed.set_footer(text=aspect_data.get('exclusive', 'Si ves esto, contacta a agente E'))
            await interaction.response.edit_message(embed=embed, view=view, attachments=[icon])
        
        select_menu.callback = select_callback

        view = View()
        view.add_item(select_menu)

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Aspectos(bot))