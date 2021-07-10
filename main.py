import traceback
from datetime import datetime
import discord
import yaml

import sys
sys.path.insert(1, './commands')
from best import best
from help import get_help
from art import get_random_tweet
from leaderboard import leaderboard
from leaderboard import forceupdate
from profile import profile
from progression import progression
from recent import recent
from register import register
from recommandation import ptt_recommendation
from session import session_generator
from event import event
from pog import pog


class MyClient(discord.Client):
    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="Arcaea"))
        print(f'[{str(datetime.now().time().strftime("%H:%M:%S"))}] '
              f'[INFO] Connecté en tant que: {self.user.name} ({self.user.id})')

    async def on_message(self, message):
        try:
            if type(message.channel) != discord.channel.DMChannel:
                if message.content.startswith("!art"):
                    await get_random_tweet(message)
                if message.content.startswith("!best"):
                    await best(message)
                if message.content.startswith("!help"):
                    await get_help(message)
                if message.content.startswith("!profile"):
                    await profile(message)
                if message.content.startswith("!recent"):
                    await recent(message)
                if message.content.startswith("!rec") and not message.content.startswith("!recent"):
                    await ptt_recommendation(message)
                if message.content.startswith("!session"):
                    await session_generator(message)
                if message.content.startswith("!register"):
                    await register(message)
                if message.content.startswith("!leaderboard"):
                    await leaderboard(message)
                if message.content.startswith("!prog"):
                    await progression(message)
                if message.content.startswith("!pog"):
                    await pog(message)
                if message.content.startswith("!lbupdate"):
                    await forceupdate(message)
                if message.content.startswith("!event"):
                    await event(message)

        except OSError:
            msg_emb = discord.Embed(title="Erreur", type="rich", color=discord.Color.dark_red())
            msg_emb.add_field(name="Exception",value="La websocket ArcAPI a l'air d'être indisponible!")
            await message.reply(embed=msg_emb)
        except Exception as e:
            traceback.print_exc()
            msg_emb = discord.Embed(title="Erreur", type="rich", color=discord.Color.dark_red())
            msg_emb.add_field(name="Exception :",value=str(e))
            await message.reply(embed=msg_emb)


def get_token():
    with open("config.yaml", "r", encoding="UTF-8") as f:
        return yaml.load("".join(f.readlines()), Loader=yaml.FullLoader)["discord"]["token"]


def main():
    # Initialisation
    token_bot = get_token()
    client = MyClient()
    client.run(token_bot)


if __name__ == "__main__":
    main()
