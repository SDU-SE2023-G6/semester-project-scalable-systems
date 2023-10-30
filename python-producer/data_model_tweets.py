from dataclasses import dataclass, field, asdict
from datetime import datetime
import random
from typing import Union
import json
import uuid

@dataclass
class TweetObj:
    id: str
    user: str
    fullname: str
    url: str
    timestamp: int
    replies: int
    likes: int
    retweets: int
    text: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TweetPackageObj:
    payload: Union[TweetObj, str]
    correlation_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    schema_version: int = field(default=1)

    def __post_init__(self):
        self.payload = (
            self.str_to_tweet_obj(self.payload)
            if isinstance(self.payload, str)
            else self.payload
        )

    def str_to_tweet_obj(self, x: str) -> TweetObj:
        return TweetObj(**json.loads(x))

    def to_dict(self):
        self.created_at = self.created_at.timestamp()
        self.payload = json.dumps(self.payload.to_dict())
        return asdict(self)


def get_tweet_obj(
    id: str,
    user: str,
    fullname: str,
    url: str,
    timestamp: datetime,
    replies: int,
    likes: int,
    retweets: int,
    text: str
) -> TweetObj:
    return TweetObj(
        id=id,
        user=user,
        fullname=fullname,
        url=url,
        timestamp=timestamp,
        replies=replies,
        likes=likes,
        retweets=retweets,
        text=text
    )


def generate_tweet_sample() -> tuple[str, dict]:
    random_id = str(uuid.uuid4())[:20]

    tweet_data = {
        "user": "Tweetos",
        "fullname": "Twetter User",
        "url": "example.com",
        "timestamp": int(datetime.now().timestamp()),
        "replies": random.randint(0, 10000),
        "likes": random.randint(0, 10000),
        "retweets": random.randint(0, 10000),
        "text": "Sample text"
    }

    po = TweetPackageObj(payload=get_tweet_obj(id=random_id, **tweet_data))
    return random_id, po.to_dict()