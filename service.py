import json
import aiofiles


# {"1":{"title":"", "time":"", "category":""}}
class JSONManager():
    def __init__(self, filename="notebook.json"):
        self.filename = filename

    async def save_note(self, title, time, category):
        try:
            async with aiofiles.open(self.filename, "r", encoding="UTF-8") as f:
                data = json.load(await f.read())
        except:
            data = {}

    