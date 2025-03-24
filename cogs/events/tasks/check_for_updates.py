import discord
from discord.ext import commands, tasks

class CheckForUpdates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_message = None
        self.updates_channel = self.bot.config.get("channels", {})["deepwoken_updates"]
        self.updates_channel_obj = self.bot.get_channel(self.updates_channel)
        self.dwupdates = self.bot.config.get("roles", {})["deepwoken_updates"]
        self.dwupdates_role = f"<@&{self.dwupdates}>"
        self.is_running = False

    async def set_last_message(self, last_message):
        self.last_message = last_message

    async def run_task(self):
        self.check_for_updates.start()
        self.is_running = True

    @tasks.loop(seconds=1)
    async def check_for_updates(self):
        
        # Checks if a message has been sent
        if self.last_message is None:
            return
        
        # Get the current time
        current_time = discord.utils.utcnow()

        # Check if a minute has been passed since last message
        if self.last_message and (current_time - self.last_message).total_seconds() > 60:
            try:

                # Send the announcement
                await self.updates_channel_obj.send(f"¡Nueva actualización de Deepwoken {self.dwupdates_role}!")
                print("Mensaje de actualización enviado") # TODO LOG
                
                # Return default values
                self.last_message = None
                self.is_running = False
                self.check_for_updates.stop()
            except discord.NotFound:
                print("No se encontró el canal")
            except discord.Forbidden:
                print("El bot no tiene permisos para acceder al canal")
            except Exception as e:
                print(f"Error inesperado al enviar el mensaje: {e}")

async def setup(bot):
    await bot.add_cog(CheckForUpdates(bot))