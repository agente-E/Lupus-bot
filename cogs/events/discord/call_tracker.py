
import discord
import logging
from datetime import datetime
from discord. ext import commands, tasks
from threading import RLock
from cogs.utils.gacha.interact_with_data import InteractWithDatabase
from cogs.utils.gacha.give_rewards import GiveRewards

class CallTracker(commands.cog):
    def __init__(self, bot):
        self.bot
        self.user_times = {}
        self.lock = RLock()
        self.server_booster = self.bot.config.get("roles", {})["booster"]
        self.call_cooldown = self.bot.config.get("gacha_settings", {})["call_cooldown"]

    def add_to_track(self, user_id: int, tracking:bool = True):
        self.lock.acquire()
        print(f"Estado del usuario {user_id}: {tracking}")
        try:
            if tracking:
                self.user_times[user_id] = datetime.now()
            else:
                self.user_times.pop(user_id)
        except Exception as e:
            print(f"Error al añadir el estado de actualización del usuario {user_id}, mensaje de error: {e}")
        finally:
            self.lock.release()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            self.add_to_track(member.id)
        elif before.channel is not None and after.channel is None:
            self.track_user(member.id, False)

    @tasks.loop(seconds=1)
    async def hourglass_task(self):
        giver = self.bot.get_cog("GiveRewards") # type: GiveRewards
        database = self.bot.get_cog("InteractWithDatabase") # type: InteractWithDatabase
        now = datetime.now()
        self.lock.acquire()
        try:
            for user_id, time in self.user_times.items:
                if (now - time).total_seconds() >= self.call_cooldown:
                    self.user_times[user_id] = now
                    user_data = await database.get_user_data(user_id=user_id)
                    
                    # TODO
                    booster_role = user_id.get_role(self.server_booster) if user_id.get_role(self.server_booster) else None
                    await giver.give_call_reward(data=user_data, server_booster_role=booster_role)
        except Exception as e:
            logging.error('Error at %s', exc_info=e)
        finally:
            self.lock.release()

    async def get_user_times(self) -> list:
        return [user for user, _ in self.user_times.items()]

async def setup(bot):
    await bot.add_cog(CallTracker(bot))