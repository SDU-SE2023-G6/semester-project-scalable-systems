from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Union
import json

@dataclass
class BitcoinPriceObj:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume_btc: float
    volume_currency: float
    weighted_price: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BitcoinPackageObj:
    payload: Union[BitcoinPriceObj, str]
    correlation_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    schema_version: int = field(default=1)

    def __post_init__(self):
        self.payload = (
            self.str_to_bitcoin_price_obj(self.payload)
            if isinstance(self.payload, str)
            else self.payload
        )

    def str_to_bitcoin_price_obj(self, x: str) -> BitcoinPriceObj:
        return BitcoinPriceObj(**json.loads(x))

    def to_dict(self):
        self.created_at = self.created_at.timestamp()
        self.payload = json.dumps(self.payload.to_dict())
        return asdict(self)


def get_bitcoin_price_obj(
    timestamp: int,
    open: float,
    high: float,
    low: float,
    close: float,
    volume_btc: float,
    volume_currency: float,
    weighted_price: float
) -> BitcoinPriceObj:
    return BitcoinPriceObj(
        timestamp=timestamp,
        open=open,
        high=high,
        low=low,
        close=close,
        volume_btc=volume_btc,
        volume_currency=volume_currency,
        weighted_price=weighted_price
    )


import random

def generate_btc_sample() -> tuple[int, dict]:
    timestamp = datetime.utcnow()
    open_price = round(random.uniform(1, 50000), 2)
    high = round(open_price + random.uniform(0, 1000), 2)
    low = round(open_price - random.uniform(0, 1000), 2)
    close = round(random.uniform(low, high), 2)
    volume_btc = round(random.uniform(0, 10), 8)
    volume_currency = round(volume_btc * close, 10)
    weighted_price = round((high + low) / 2, 2)

    po = BitcoinPackageObj(payload=get_bitcoin_price_obj(
        timestamp=timestamp,
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume_btc=volume_btc,
        volume_currency=volume_currency,
        weighted_price=weighted_price
    ))

    return timestamp, po.to_dict()
