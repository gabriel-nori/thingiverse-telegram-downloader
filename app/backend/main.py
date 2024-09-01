from telethon import TelegramClient, events
from app.models import ThingiverseModel
from app.config import settings
from app.logger import Logger
from zipfile import ZipFile
import re
import os

# Use your own values from my.telegram.org
api_id = settings.TELEGRAM_API_ID
api_hash = settings.TELEGRAM_API_HASH
client = TelegramClient('anon', api_id, api_hash)
path = settings.DOWNLOAD_PATH
temp_location: str = os.getcwd() + "/tmp/"

logger = Logger("main")

logger.info("Starting application")

if not os.path.exists(temp_location):
    logger.debug(
        "TMP directory is not created. Creating it now",
        extra={
            "temp_location": temp_location
        }
    )
    try:
        os.makedirs(temp_location)
    except Exception as e:
        logger.critical(
        "TMP directory was not created!",
        extra={
            "temp_location": temp_location,
            "exception": e
        }
    )


@client.on(events.NewMessage)
async def my_event_handler(event):
    message = event.raw_text
    if "thingiverse.com" in message:
        url = re.search("(?P<url>https?://[^\s]+)", message).group("url")
        id = url.split(":")[2]

        logger.info(
            "Got a Thingiverse model from message. Starting check",
            extra={
                "id": id,
                "url": url
            }
        )

        model = ThingiverseModel(id, True)
        if model.metadata:
            dir_list = os.listdir(path=path)
            temp_file_name = re.sub('[^a-zA-Z0-9_ \n\.]', '', model.title).replace(" ", "_") + f"_{str(model.thing_id)}"
            zipFileName = temp_file_name + ".zip"
            if not temp_file_name in dir_list and not zipFileName in dir_list:
                logger.info(
                    "Thingiverse model from message is not yet in download location. Starting download",
                    extra={
                        "id": id,
                        "url": url,
                        "directory_name": temp_file_name
                    }
                )
                await event.reply(f"Downloading \"{model.title}\"")
                success = model.get_files_zip(temp_file_name)
                if success:
                    logger.info(
                        "Finished downloading model",
                        extra={
                            "id": id,
                            "url": url,
                            "directory_name": temp_file_name
                        }
                    )
                    await event.reply("Extracting and excluding zip")
                    logger.debug(
                        "Starting zip decompression on temp folder",
                        extra={
                            "id": id,
                            "url": url,
                            "directory_name": temp_file_name,
                            "zip_location": temp_location + zipFileName
                        }
                    )
                    with ZipFile(temp_location + zipFileName, 'r') as zObject: 
                        # Extracting all the members of the zip  
                        # into a specific location. 
                        zObject.extractall(path=path + temp_file_name)
                        
                    logger.debug(
                        "Finished zip decompression on temp folder. Cleaning old file",
                        extra={
                            "id": id,
                            "url": url,
                            "directory_name": temp_file_name,
                            "zip_location": temp_location + zipFileName
                        }
                    )
                    os.remove(temp_location + "/" + zipFileName)
                    await event.reply("Done")
                else:
                    await event.reply("Failed to download")
            else:
                await event.reply("Model \"" + model.title + "\" already exists")
                logger.info(
                    "Thingiverse model from message is already in download location",
                    extra={
                        "id": id,
                        "url": url,
                        "directory_name": temp_file_name
                    }
                )
        else:
            await event.reply("Failed to download")
            logger.error(
                "Failed to get Thingiverse model from message",
                extra={
                    "id": id,
                    "url": url
                }
            )
            

client.start()
client.run_until_disconnected()