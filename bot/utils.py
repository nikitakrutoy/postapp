import requests
import json

class Config:
    options = None
    
    @classmethod
    def setup(cls, path):
        with open(path) as f:
            cls.options = json.load(f)

class DataStorage:
    def __init__(self, data, exception_class=Exception):
        self.exception = exception_class
        self.profiles = {
            profile["id"]: self._transform_profile(profile)
            for profile in data
        }
    
    def _transform_profile(self, profile):
        profile["pages"] = {
            page["id"]: page for page in profile["pages"]
        }
        return (profile)

    def get_profile(self, uid):
        profile = self.profiles.get(uid)
        if profile is None:
            raise self.exception(f"Your are not authorized for user with id {uid}")
        return profile
    
    def get_pages(self, uid):
        profile = self.get_profile(uid)
        pages = profile.get("pages")
        if pages is None:
            raise self.exception(f"There is no pages for user with id {uid}")
        return pages
    
    def get_page(self, uid, pid):
        pages = self.get_pages(uid)
        page = pages.get(pid)
        if page is None:
            raise self.exception(f"There is no page with id {pid} for user with id {uid}")
        return page


class Query:
    def __init__(self, sid, uid, pid):
        self.sid = sid
        self.uid = uid
        self.pid = pid

    def to_json(self):
        return json.dumps(self.__dict__)
    
    @classmethod
    def from_json(cls, s):
        return cls(**json.loads(s))

    @classmethod
    def from_string(cls, s):
        q = s.split(":")
        q += ([None] * (3 - len(q)))[:3]
        return cls(*q)
    

def set_webhook(token):
    response = requests.get(
        url=f"https://api.telegram.org/bot{token}/setWebhook",
        params=dict(
            url=f"https://nikitakrutoy.ml:8443/bot/{token}"
        )
    )
    print(response.text)

def delete_webhook(token):
    response = requests.get(
        url=f"https://api.telegram.org/bot{token}/deleteWebhook",
    )
    print(response.text)


class ParseMessageException(Exception):
    pass


def parse_message(message):
    if message is None:
        return None, None, []
    temp = message.split("&")
    if len(temp) > 3:
        raise ParseMessageException("There is an extra & or more than two commands in message.")
    if len(temp) == 1:
        return temp[0], None, []
    if len(temp) == 0:
        return None, None, []

    message, commands = temp[0], temp[1:]
    message = message.strip()
    eta = None
    queries = []
    for command in commands:
        command = command.strip().split(" ")
        if len(command) < 2:
            raise ParseMessageException(f"Pass args to command: {command[0]} ")
        command, args = command[0], command[1:]

        if command == "eta":
            if args[0].isdigit():
                eta = int(args[0])
            else:
                raise ParseMessageException(f"eta argument should be a number")
        
        elif command == "pages":
            for arg in args:
                queries.append(Query.from_string(arg))

        else:
            raise ParseMessageException(f"Unknown command: {command}")
    
    return message, eta, queries

def extract_photo(photo_sizes):
    res = photo_sizes[0]
    m = 0
    for size in photo_sizes:
        if size.file_size > m:
            res = size
    f = res.get_file()
    return dict(
        file_id=f.file_id,
        file_unique_id=f.file_unique_id,
        file_path=f.file_path,
        file_size=f.file_size
    )