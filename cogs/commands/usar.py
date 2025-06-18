import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.discord.check_guild import CheckGuild

class Usar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database: InteractWithDatabase = None
        self.checker: CheckGuild = None
        self.guild_id = self.bot.config.get("guild", {})["test"]

    @app_commands.command(name="usar", description="Usa un ítem de tu inventario")
    @app_commands.checks.cooldown(1, 10.0) 
    @app_commands.describe(item="Nombre del item a usar")
    async def usar(self, interaction: discord.Interaction, item: str):
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database
        self.checker = self.bot.get_cog("CheckGuild") if self.checker is None else self.checker

        await interaction.response.defer()

        # Check if the user has the item
        try:
            user_item = await self.database.get_item_user_inventory(interaction.user.id, item_id= await self.database.get_item_id(item_name=item))
            if user_item == None:
                await interaction.followup.send('No tienes este item en tu inventario o no existe.')
                return
            
            match user_item['item']:
                
                case 'Cambiar Aspecto':               
                    await self.change_aspect(interaction)
                    return
                
                case _:
                    await interaction.followup.send('Ha ocurrido un error, notifica a un moderador.')
                    return
        except Exception as e:
            print(f"Error en usar comando: {e}")
            await interaction.followup.send('El item indicado no existe.')

    @usar.autocomplete('item')
    async def item_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        self.database = self.bot.get_cog("InteractWithDatabase") if self.database is None else self.database

        user_inventory = await self.database.get_user_inventory(user_id=interaction.user.id)

        return [
            app_commands.Choice(name=x["item"], value=x["item"])
            for x in user_inventory if x["item"].lower().startswith(current.lower())
        ] or [app_commands.Choice(name="No tienes items en tu inventario", value="no_match")]


    async def change_aspect(self, interaction: discord.Interaction):
        
        user_data = await self.database.get_user_data(interaction.user.id)

        embed = discord.Embed(
            title="Confirmación de cambio de aspecto",
            description="¿Estás seguro de que quieres usar un token para cambiar tu aspecto?",
            color=discord.Color.red()
        )

        embed.add_field(name="Aspecto actual", value=user_data['aspect'], inline=False)

        button_yes = Button(label="Sí, cambiar", style=discord.ButtonStyle.green)
        button_no = Button(label="No, cancelar", style=discord.ButtonStyle.red)

        context = {'user_data': user_data}

        async def confirm_change(interaction: discord.Interaction):
            
            guild = self.bot.get_guild(self.guild_id)

            if interaction.user.id != interaction.user.id:
                await interaction.response.send_message("Este botón no es para ti.", ephemeral=True)
                return
            
            if not await self.database.remove_item_user(interaction.user.id, 'Cambiar Aspecto', 1):
                await interaction.followup.send('Error al eliminar el item de tu inventario, avisa a un desarrollador.')
                return
            
            current_aspect_role = discord.utils.get(guild.roles, name=context['user_data']['aspect'])
            if current_aspect_role in interaction.user.roles:
                await interaction.user.remove_roles(current_aspect_role)

            context['user_data'] = await self.database.reroll_aspect(context['user_data'])

            # Get the new aspect of the user
            new_user_aspect = context['user_data']['aspect']
            
            new_aspect_role = discord.utils.get(guild.roles, name=new_user_aspect)
            if not new_aspect_role in interaction.user.roles:
                await interaction.user.add_roles(new_aspect_role)

            if new_user_aspect == 'Primal Vesperian':
                image_path = f"assets/images/icons/Primal_Vesperian.png"
            else:
                image_path = f"assets/images/icons/{new_user_aspect}.png"

            # And then get color
            aspects = await self.database.get_aspects()
            aspect_data = next((aspect for aspect in aspects if aspect['name'] == new_user_aspect), None)
            color = discord.Color(int(aspect_data.get('color', "#FF00FF")[1:], 16))
            
            new_file = discord.File(image_path)
            embed = discord.Embed(
                title="Cambio de Aspecto",
                color=color
            )
            embed.set_thumbnail(url=f"attachment://{image_path.split('/')[-1]}")
            embed.add_field(name=f"Cambio de aspecto", value=f"{interaction.user.mention}, tu nuevo aspecto ahora es {user_data['aspect']}", inline=False) 
            
            await self.database.save_user_data(user_id=interaction.user.id, data=user_data)
            await interaction.message.delete()
            await interaction.response.send_message(embed=embed, file=new_file)

        async def cancel_change(interaction: discord.Interaction):
            if interaction.user.id != int(interaction.user.id):
                await interaction.response.send_message("Este botón no es para ti.", ephemeral=True)
                return
            if interaction.message:
                await interaction.message.delete()
            await interaction.response.send_message("Has cancelado el cambio de aspecto.", ephemeral=False)

        # Añadir las interacciones de los botones
        button_yes.callback = confirm_change
        button_no.callback = cancel_change

        # Crear una vista para los botones
        view = View(timeout=10)
                
        view.add_item(button_yes)
        view.add_item(button_no)

        sent_message = await interaction.followup.send(embed=embed, view=view)        
        
        await asyncio.sleep(10)
        try:
            await sent_message.delete()
        except:
            pass
        
    @usar.error
    async def command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏳ Debes esperar {round(error.retry_after, 1)} segundos antes de volver a usar este comando.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Usar(bot))