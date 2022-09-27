from collections import namedtuple
from types import NoneType
from _utils.typing import PathLike
from _utils.val import val_instance
import datetime as dt


class Config:
    """
    Abstract base class for trading strategy configuration classes.
    """

    def from_x0(self, *args):
        raise NotImplementedError("Config subclass must override from_x0()")

StrategyResponse = namedtuple("StrategyResponse", ["time", "command", "price"])
StrategyEvent = namedtuple("StrategyEvent", ["time", "name", "value"])

class StrategyResults:
    def __init__(self, date: dt.date | None, buy_time: dt.datetime | None, buy_price: float | None, sell_time: dt.datetime | None, sell_price: float | None):
        val_instance(date, (dt.date, NoneType))
        val_instance(buy_time, (dt.datetime, NoneType))
        val_instance(buy_price, (float, NoneType))
        val_instance(sell_time, (dt.datetime, NoneType))
        val_instance(sell_price, (float, NoneType))

        self.date = date
        self.buy_time = buy_time
        self.buy_price = buy_price
        self.sell_time = sell_time
        self.sell_price = sell_price

    def update(self, date: dt.date | None, buy_time: dt.datetime = None, buy_price: float = None, sell_time: dt.datetime = None, sell_price: float = None) -> None:
        if not date is None:
            val_instance(date, dt.datetime)

            self.date = date
            
        if not buy_time is None:
            val_instance(buy_time, dt.datetime)

            self.buy_time = buy_time

        if not buy_price is None:
            val_instance(buy_price, float)

            self.buy_price = buy_price

        if not sell_time is None:
            val_instance(sell_time, dt.datetime)

            self.sell_time = sell_time

        if not sell_price is None:
            val_instance(sell_price, float)

            self.sell_price = sell_price

    def pnl(self) -> float:
        if self.sell_price is None or self.buy_price is None:
            return 0.0
        
        return self.sell_price - self.buy_price

    def pnl_perc(self) -> float:
        if self.sell_price is None or self.buy_price is None:
            return 0.0
        
        return self.pnl() / self.buy_price

    def pnl_bps(self) -> float:
        if self.sell_price is None or self.buy_price is None:
            return 0.0
        
        return (self.pnl_perc() * 10000)
    
    def __str__(self) -> str:
        sell_price = str(self.sell_price)
        buy_price = str(self.buy_price)
        
        price_len = max(len(sell_price), len(buy_price), 5)
        
        pnl_perc = str(abs(self.pnl_perc()))
        pnl_perc_prefix = "+" if self.pnl_perc() >= 0 else "-"
        
        pnl_bps = str(abs(self.pnl_bps()))
        pnl_bps_prefix = "+" if self.pnl_bps() >= 0 else "-"
        
        if buy_price == "None":
            buy_price = buy_price.ljust(price_len, ' ').rjust(price_len)[:price_len]
        else:
            buy_price.ljust(price_len, '0').rjust(price_len)[:price_len]
            
        if sell_price == "None":
            sell_price = sell_price.ljust(price_len, ' ').rjust(price_len)[:price_len]
        else:
            sell_price.ljust(price_len, '0').rjust(price_len)[:price_len]
        
        _str = [
            f" BUY: $ {buy_price} @ {self.buy_time}",
            f"SELL: $ {sell_price} @ {self.sell_time}",
            f"   %: {pnl_perc_prefix} {pnl_perc.ljust(price_len, '0').rjust(price_len)[:price_len]} %",
            f" bps: {pnl_bps_prefix } {pnl_bps.ljust(price_len, '0').rjust(price_len)[:price_len]} bps",
        ]
        
        return '\n'.join(_str)


class Strategy:
    """
    Abstract base class for trading strategy classes.

    Subclasses must override the next() method.
    """

    def next(self, *args):
        raise NotImplementedError("Strategy subclass must override next()")