from telethon import TelegramClient, events
from app.models import ThingiverseModel
from app.config import settings
from zipfile import ZipFile
import re
import os

# Use your own values from my.telegram.org
api_id = settings.TELEGRAM_API_ID
api_hash = settings.TELEGRAM_API_HASH
client = TelegramClient('anon', api_id, api_hash)
path = settings.DOWNLOAD_PATH
temp_location: str = os.getcwd() + "/tmp/"

# The first parameter is the .session file name (absolute paths allowed)


@client.on(events.NewMessage)
async def my_event_handler(event):
    message = event.raw_text
    if "thingiverse.com" in message:
        url = re.search("(?P<url>https?://[^\s]+)", message).group("url")
        id = url.split(":")[2]
        model = ThingiverseModel(id, True)
        if model.metadata:
            dir_list = os.listdir(path=path)
            temp_file_name = re.sub('[^a-zA-Z0-9_ \n\.]', '', model.title).replace(" ", "_") + f"_{str(model.thing_id)}"
            zipFileName = temp_file_name + ".zip"
            if not temp_file_name in dir_list and not zipFileName in dir_list:
                await event.reply("Downloading " + temp_file_name.replace("_", " "))
                success = model.get_files_zip(temp_file_name)
                if success:
                    await event.reply("Extracting and excluding zip")
                    with ZipFile(temp_location + zipFileName, 'r') as zObject: 
                        # Extracting all the members of the zip  
                        # into a specific location. 
                        zObject.extractall(path=path + temp_file_name)
                    os.remove(temp_file_name + zipFileName)
                    await event.reply("Done")
                else:
                    await event.reply("Failed to download")
            else:
                await event.reply("Model \"" + model.title + "\" already exists")
        else:
            await event.reply("Failed to download")
            

client.start()
client.run_until_disconnected()