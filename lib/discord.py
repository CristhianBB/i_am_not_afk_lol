import requests
import json

class DiscordBot(object):
    def __init__(self, webhook=None, username='Bot'):
        self.webhook = webhook
        self.username = username
        self.ok = self.webhook != '' and self.webhook != None
    
    def send_message(self, message='', desc=''):
        return self.send_raw_message(
            cdata={
                'content': message,
            },
        )
    
    def send_raw_message(self, cdata={}, cembed=None):
        data = {}
        data["username"] = self.username
        data["embeds"] = []

        if cembed:
            data["embeds"].append(cembed)

        for field in cdata:
            data[field] = cdata[field]
        
        result = requests.post(self.webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return (False, err)
        else:
            return (True, result.status_code)