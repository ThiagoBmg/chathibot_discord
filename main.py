import re
import discord
import requests
from decouple import config

discord_client = config("DISCORD_CLIENT", None)
chathibot_key = config("CHATHIBOT_API_KEY", None)
chathibot_url = config("CHATHIBOT_URL", None)
chathibot_bot_id = config("CHATHIBOT_BOT_ID", None)


class ChathibotClient:
    url = chathibot_url
    headers = {
        "x_key": chathibot_key,
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    def __init__(self, bot_id: str) -> None:
        self.bot_id = bot_id
        pass

    def run(self, sender, text):
        try:
            response = requests.post(
                url=f"{self.url}/v1/{self.bot_id}",
                headers=self.headers,
                json={"sender": str(sender), "text": str(text)},
            )
            return response.json()
        except Exception as err:
            print(err)
            return None


class DiscordClient(discord.Client):
    bot_hook = ChathibotClient(chathibot_bot_id)

    async def on_ready(self):
        print("Logged on as", self.user)

    async def on_message(self, message):
        if message.author == self.user:
            return
        view, text = self.build_message(message.author, message.content)
        await message.channel.send(text, view=view)

    async def on_button_click(self, interaction: discord.Interaction):
        view, text = self.build_message(interaction.user, interaction.data["custom_id"])
        await interaction.response.send_message(text, view=view)

    def build_message(self, author, content):
        response = self.bot_hook.run(author, content)
        view = self.create_view(response)
        text = self.get_text_response(response)
        return view, text

    def create_view(self, response):
        view = discord.ui.View()
        text = "".join(response["response"])
        options = re.findall(
            '<span class="sugg-options" value="(.*?)">(.*?)</span>', text
        )

        if options:
            for i, x in options:
                button = discord.ui.Button(label=x, custom_id=i, disabled=False)
                button.callback = self.on_button_click
                view.add_item(button)

        return view

    @staticmethod
    def get_text_response(response):
        plain_text = []
        for text in response["response"]:
            result = re.search(r'(.*)<div class="sugg-title">', text)
            plain_text.append(result.group(1)) if result else plain_text.append(text)
        return "".join(plain_text)


intents = discord.Intents.default()
intents.message_content = True
DiscordClient(intents=intents).run(discord_client)
