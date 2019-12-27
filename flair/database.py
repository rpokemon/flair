import json
from donphan import Column, Table

# TODO: use SQL DB

with open('flair/static/data/flairs.json') as f:
    public_flairs = json.load(f)

with open('flair/static/data/defaults.json') as f:
    default_flairs = json.load(f)


class UserBallFlairs(Table):
    username: str = Column(primary_key=True, index=True)
    flairclass: str = Column(primary_key=True, index=True)

    @classmethod
    def is_valid_flair(cls, css_class):
        return css_class in public_flairs

    @classmethod
    def get_ballflair(cls, redditor):
        return default_flairs.get(redditor.name)
