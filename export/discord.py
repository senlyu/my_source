import requests
import pytz

class DiscordExporter:
    def __init__(self, channel_url):
        self.channel_url = channel_url

    def export(self, messages):
        r = requests.post(self.channel_url, data={'content': messages})