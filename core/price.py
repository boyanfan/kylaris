from core.types import immutable
from core.utilities import datatime_to_milliseconds, milliseconds_to_datatime
from enum import Enum
from typing import Protocol, Iterable, List, Dict, Any, Optional, runtime_checkable
from datetime import datetime
import requests

class PriceInterval(Enum):
    """
    A type that defines the discrete unit or range within which price movements are measured, grouped, or analyzed.
    It aggregates prices into intervals smooths out random fluctuations (noise reduction), enables consistent
    comparison across different time frames or assets (comparability), identifies trends, volatility spikes, or
    reversal patterns (signal detection), and reduces computational load by compressing raw tick data (Performance).
    """
    minute = '1m'
    minute5 = '5m'
    minute15 = '15m'
    minute30 = '30m'
    hour = '1h'
    hour4 = '4h'
    day = '1d'
    week = '1w'
    month = '1mo'

class TradableCategory(Enum):
    """
    A type that defines the broad category of different types of financial assets within a system based on
    its market characteristics, regulatory environment, and settlement mechanics.
    """
    equity = 'equity'
    crypto = 'crypto'

class TradableInstrument(Enum):
    """
    Represents a tradable market instrument supported by the Kylaris Trading System, it defines the specific
    trading symbols currently available for analysis or execution.
    """
    ETHUSDT = 'ETHUSDT'
    BTCUSDT = 'BTCUSDT'
    AAPL = 'AAPL'
    NVDA = 'NVDA'
    TSLA = 'TSLA'

@immutable
class MarketIdentifier:
    """
    A type that defines a short alphanumeric code used to uniquely identify a financial instrument.
    It is used by price data providers, order management, and analytics modules to reference the same instrument
    consistently across different components of the system.
    """

    # The code that uniquely identifies what is being traded
    instrument: TradableInstrument

    # The classification of the instrument, specifying its market type.
    category: TradableCategory

@immutable
class PriceRepresentable:
    """
    A type that defines price movement within a specific time interval, representing a complete snapshot of market
    price and volume information for a single trading symbol at a specific timestamp.
    """

    # The trading symbol or pair identifier used to associate the price data with a specific market instrument.
    symbol: MarketIdentifier

    # The precise time at which this price snapshot was recorded.
    # It should be expressed in UTC for consistency across exchanges.
    timestamp: datetime

    # The price of the first executed trade during the interval.
    open_price: float

    # The highest traded price observed during the interval.
    high_price: float

    # The lowest traded price observed during the interval.
    low_price: float

    # The last traded price at the end of the interval.
    close_price: float

    #  The total traded quantity of the asset during the interval, representing market activity and liquidity.
    volume: float

@immutable
class PriceProviderContext:
    """
    A configuration object that encapsulates all parameters required by a price data provider to fetch
    market price information for a given instrument within a specific time range.
    """

    # The market instrument to fetch price data for. It defines both the trading symbol and its category.
    symbol: MarketIdentifier

    # The time granularity of each price point.
    interval: PriceInterval

    # The starting timestamp of the desired data range, inclusive, must be UTC-aware.
    start_time: datetime

    #  The ending timestamp of the desired data range, exclusive, must be UTC-aware.
    end_time: datetime

    #  The maximum number of data points to fetch in a single request.
    limit: Optional[int]

@runtime_checkable
class PriceProvider(Protocol):
    """
    A protocol that defines the interface for all price data providers used within the system.
    Implementations of this protocol are responsible for connecting to specific data sources, executing queries
    and returning standardized price representations for further analysis.
    """
    def fetch(self, context: PriceProviderContext) -> Iterable[PriceRepresentable]:
        """
        Fetches historical or real-time price data according to the given context, returns an iterable object,
        each representing a single time interval with open, high, low, close, and volume data.

        :param context: The context specifying which instrument, interval, and time range to retrieve.
        :return: A collection of price records standardized into the system’s internal format.
        """
        ...

class BinancePriceProvider(PriceProvider):
    """
    A concrete implementation of PriceProvider that retrieves historical price data from Binance's public REST API.
    This provider sends HTTP GET requests using the specified symbol, interval, and time range defined in the context,
    converts the JSON response from Binance into a collection of standardized PriceRepresentable objects.
    """

    # Base REST API endpoint for Binance price data.
    binance_url: str = "https://api.binance.com/api/v3/klines"

    # Timeout in seconds for HTTP requests to prevent indefinite blocking.
    timeout: int = 5

    def fetch(self, context: PriceProviderContext) -> Iterable[PriceRepresentable]:
        """
        Fetches historical or real-time price data according to the given context, returns an iterable object,
        each representing a single time interval with open, high, low, close, and volume data.

        :param context: The context specifying which instrument, interval, and time range to retrieve.
        :return: A collection of price records standardized into the system’s internal format.
        """

        # Binance uses different string representations for intervals, so convert to Binance format
        binance_price_interval: Dict[PriceInterval, str] = {
            PriceInterval.minute: '1m', PriceInterval.minute5: '5m', PriceInterval.minute15: '15m',
            PriceInterval.minute30: '30m', PriceInterval.hour: '1h', PriceInterval.hour4: '4h',
            PriceInterval.day: '1d', PriceInterval.week: '1w', PriceInterval.month: '1M'
        }
        interval: str = binance_price_interval[context.interval]

        # Convert datetime to milliseconds for Binance API
        start_time: int = datatime_to_milliseconds(context.start_time)
        end_time: int = datatime_to_milliseconds(context.end_time)

        prices: Iterable[PriceRepresentable] = []
        next_start_time: int = start_time

        # Continue fetching while the next start time is before the requested end time
        while next_start_time <= end_time:
            parameters: Dict[str, Any] = {
                'symbol': context.symbol.instrument.value, 'interval': interval,
                'startTime': next_start_time, 'endTime': end_time - 1, 'limit': context.limit,
            }

            # Send the HTTP GET request to Binance API and parse JSON response into Python list of arrays
            response: Response = requests.get(self.binance_url, params=parameters, timeout=self.timeout)
            contents: List[Any] = response.json()

            # Break if no data is returned, as we reached the end of available history
            if not contents:
                break

            # Iterate through each entry returned by Binance
            for content in contents:
                # Binance price data schema: [0] openTime(ms), [1] open, [2] high, [3] low, [4] close, [5] volume,
                # [6] closeTime(ms), [7] quoteAssetVolume, [8] numberOfTrades, [9] takerBuyBaseAssetVolume, ...
                open_time: datetime = milliseconds_to_datatime(int(content[0]))
                prices.append(PriceRepresentable(
                    symbol=context.symbol, timestamp=open_time, open_price=float(content[1]), high_price=float(content[2]),
                    low_price=float(content[3]), close_price=float(content[4]), volume=float(content[5])
                ))

                # Stop early if we exceed the requested limit
                if context.limit is not None and len(prices) > context.limit:
                    return prices

            # Advance to the next starting timestamp after the last price in this batch.
            next_start_time = int(contents[-1][6]) + 1
        return sorted(prices, key=lambda price: price.timestamp)
