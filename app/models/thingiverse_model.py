import requests
import time
import os
import re

class ThingiverseModel:
    __base_url = "https://www.thingiverse.com/thing:"
    thing_id: int = None
    thing_url: str = None
    keywords: list[str] = None
    title: str = None
    author: str = None
    description: str = None
    image_url: str = None
    metadata: str = None
    thing_exists: bool = False
    filename: str = None
    temp_location: str = os.getcwd() + "/tmp/"

    max_retries: int = 4
    retry_interval_seconds: int = 4
    metadata_on_init: bool = False
    auto_download: bool = False

    def __init__(self, thing_id: int, metadata_on_init: bool = False, auto_download: bool = False) -> None:
        self.thing_id = thing_id
        self.thing_url = self.__base_url + str(self.thing_id)
        self.metadata_on_init = metadata_on_init
        self.auto_download = auto_download

        if metadata_on_init:
            self.get_metadata()

    def get_metadata(self):
        response = None
        for i in range(4):
            temp_response = requests.get(self.thing_url)
            if temp_response.status_code == 200:
                response = temp_response.text
                self.thing_exists = True
                break
            time.sleep(self.retry_interval_seconds)
        self.metadata = response

        if self.metadata:
            self.__parse_description()
            self.__parse_title_and_author()
            self.__parse_keywords()
            self.__parse_image_url()

            if self.auto_download:
                self.get_files_zip()
        
    def get_files_zip(self, filename: str = None):
        output_file = filename
        if not filename:
            output_file = re.sub('[^a-zA-Z0-9_ \n\.]', '', self.title).replace(" ", "_") + f"_{str(self.thing_id)}"
        r = requests.get(self.thing_url + "/zip", stream=True)
        if r.status_code == 200:
            with open(self.temp_location + output_file + ".zip", 'wb') as file:
                for chunk in r.iter_content(chunk_size=10240):
                    if chunk:
                        file.write(chunk)
            return True

    def __parse_description(self):
        pattern = r'<meta property=["\']og:description["\'] content=["\']([^"\'<>]+)["\']>'
        description = re.findall(pattern, self.metadata)
        if len(description):
            self.description = description[0]
    
    def __parse_title_and_author(self):
        pattern = r'<meta property=["\']og:title["\'] content=["\']([^"\'<>]+)["\']>'
        title_and_author = re.findall(pattern, self.metadata)
        if not len(title_and_author):
            return
        
        title_and_author = title_and_author[0]
        self.title = title_and_author[:title_and_author.rindex("by") -1]
        self.author = title_and_author[title_and_author.rindex("by") + 3:]
    
    def __parse_keywords(self):
        pattern = r'<meta name=["\']keywords["\'] content=["\']([^"\'<>]+)["\']>'
        keywords = re.findall(pattern, self.metadata)
        if len(keywords):
            self.keywords = keywords[0].split(",")

    def __parse_image_url(self):
        pattern = r'<meta property=["\']og:image["\'] content=["\']([^"\'<>]+)["\']>'
        image_url = re.findall(pattern, self.metadata)
        if len(image_url):
            self.image_url = image_url[0]