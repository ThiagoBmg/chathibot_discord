import discord
import requests
from decouple import config

discord_client = config("DISCORD_CLIENT", None)
chathibot_key = config("CHATHIBOT_API_KEY", None)
chathibot_url = config("CHATHIBOT_URL", None)


class ChathibotClient():
    url = chathibot_url
    headers = {"x_key": chathibot_key, 'accept': 'application/json',
               'Content-Type': 'application/json'}

    def __init__(self, bot_id: str) -> None:
        self.bot_id = bot_id
        pass

    def run(self, sender, text):
        try:
            response = requests.post(
                url=f"{self.url}/v1/bot/{self.bot_id}/speak",
                headers=self.headers,
                json={"sender": str(sender), "text": str(text)}
            )
            return response.json()
        except:
            return None


class MyClient(discord.Client):
    bot_hook = ChathibotClient("1bcc17c6-58d2-4491-9c78-2963d84f8d5e")

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        if message.author == self.user:
            return
        response = self.bot_hook.run(message.author, message.content)
        await message.channel.send(str(response["response"]))


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(discord_client)
