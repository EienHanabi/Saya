from datetime import datetime
import discord
import yaml

from funct import best, get_help, recent, profile, register, ptt_recommendation, session_generator
from art import get_random_tweet


class MyClient(discord.Client):
    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="Arcaea"))
        print(f'[{str(datetime.now().time().strftime("%H:%M:%S"))}] '
              f'[INFO] Connecté en tant que: {self.user.name} ({self.user.id})')

    async def on_message(self, message):
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
