import json

class Config:
    @classmethod
    def setup(cls, path):
        with open(path) as f:
            cls.options = json.load(f)
