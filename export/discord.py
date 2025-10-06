import requests

class DiscordExporter:
    def __init__(self, channel_url):
        self.channel_url = channel_url

    @staticmethod
    def chunk_string(string, chunk_size):
        chunks = []
        for i in range(0, len(string), chunk_size):
            chunks.append(string[i:i + chunk_size])
        return chunks

    def export_by_model(self, messages, analyse):
        result = analyse.make_standard(messages)
        return [ requests.post(self.channel_url, data={'content': m}) for m in result]

    def export(self, messages):
        if len(messages) <= 2000:
            return requests.post(self.channel_url, data={'content': messages})

        chunk_size = 1000
        result = DiscordExporter.chunk_string(messages, chunk_size)

        r = []
        for m in result:
            r.append(requests.post(self.channel_url, data={'content': m}))
        return r