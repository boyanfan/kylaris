from core.price import PriceRepresentable
from core.types import IndicatorRepresentable
from typing import Sequence, Iterable

def exponential_moving_average(prices: Iterable[PriceRepresentable], period: int) -> IndicatorRepresentable:
    """
    The Exponential Moving Average (EMA) is an indicator that smooths out price data to reveal trends more clearly.
    Unlike the Simple Moving Average (SMA), which gives equal weight to all data points, the EMA gives more weight
    to recent prices, making it more responsive to new information.

    :param prices: A collection of price records standardized into the system’s internal format.
    :param period: The number of periods over which to calculate the EMA.
    :return: EMA values where the first few entries are None due to insufficient data for initialization.
    """

    # Use close price to calculate EMA
    values: Sequence[float] = [price.close_price for price in prices]

    # Initial EMA by simple moving average of the first period prices
    previous_moving_average: float = sum(values[:period]) / period

    # Smoothing factor that determines weighting of recent prices
    alpha: float = 2.0 / (period + 1.0)

    # Initialize result list with Nones for the first values
    results: IndicatorRepresentable = [None] * (period - 1)
    results.append(previous_moving_average)

    # Iteratively apply the EMA formula for subsequent prices
    for price in values[period:]:
        previous_moving_average = alpha * price + (1.0 - alpha) * previous_moving_average
        results.append(previous_moving_average)
    return results

def relative_strength_index(prices: Iterable[PriceRepresentable], period: int) -> IndicatorRepresentable:
    """
    The Relative Strength Index (RSI) is a momentum oscillator to measure the speed and magnitude of recent
    price changes, helping traders identify overbought or oversold market conditions. Market is considered overbought
    and therefore price may fall soon when RSI > 70, while market is considered oversold and therefore price may rise
    soon when RSI < 30. However, thresholds can vary depending on the asset’s volatility, like 80/20 for crypto.

    :param prices: A collection of price records standardized into the system’s internal format.
    :param period: Number of periods to use for RSI calculation, the most common value is 14.
    :return: RSI values where the first few entries are None due to insufficient data for initialization.
    """

    # Use close price to calculate RSI
    values: Sequence[float] = [price.close_price for price in prices]
    gains: Sequence[float] = [0.0]
    losses: Sequence[float] = [0.0]

    # Compute gains and losses per period
    for value in range(1, len(values)):
        difference: float = values[value] - values[value - 1]
        gains.append(max(difference, 0.0))
        losses.append(max(-difference, 0.0))

    # Initial average gain/loss
    average_gain: float = sum(gains[1:period + 1]) / period
    average_loss: float = sum(losses[1:period + 1]) / period

    # Compute first RSI value
    results: IndicatorRepresentable = [None] * period
    results.append(100.0 if average_loss == 0.0 else 100.0 - (100.0 / (1.0 + average_gain / average_loss)))

    # Smoothing for subsequent values
    for value in range(period + 1, len(values)):
        average_gain = (average_gain * (period - 1) + gains[value]) / period
        average_loss = (average_loss * (period - 1) + losses[value]) / period
        results.append(100.0 if average_loss == 0.0 else 100.0 - (100.0 / (1.0 + average_gain / average_loss)))
    return results

def moving_average_convergence_divergence(
        prices: Iterable[PriceRepresentable], fast_period: int, slow_period: int, signal_period: int
    ) -> (IndicatorRepresentable, IndicatorRepresentable, IndicatorRepresentable):
    """
    Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator. It measures how two EMAs,
    fast and slow, are converging or diverging, revealing when momentum is accelerating or weakening, showing the
    relationship between short-term and long-term trends.

    :param prices: A collection of price records standardized into the system’s internal format.
    :param fast_period: Period for the fast EMA, default to be 12.
    :param slow_period: Period for the slow EMA, default to be 6.
    :param signal_period:  Period for the signal line EMA, default to be 9.
    :return: [0]: a MACD line as the difference between the fast EMA and slow EMA,
             [1]: an EMA of the MACD line,
             [2]: a histogram as the difference between MACD line and signal line.
    """

    # Compute fast and slow exponential moving averages over the price series
    moving_average_fast: IndicatorRepresentable = exponential_moving_average(prices, fast_period)
    moving_average_slow: IndicatorRepresentable = exponential_moving_average(prices, slow_period)

    # Compute the MACD line as the difference between the fast and slow EMAs
    moving_average_line: IndicatorRepresentable = [
        None if (value_fast is None or value_slow is None) else (value_fast - value_slow)
        for value_fast, value_slow in zip(moving_average_fast, moving_average_slow)
    ]

    # Compute the EMA of the MACD line
    signal_values: IndicatorRepresentable = exponential_moving_average([
        PriceRepresentable(symbol=None, timestamp=None, open_price=None, high_price=None, low_price=None, close_price=value, volume=None)
        for value in moving_average_line if value is not None
    ], signal_period)

    # Align the signal EMA result back to the full timeline
    signal_line: IndicatorRepresentable = [None] * (len(moving_average_line) - len(signal_values)) + list(signal_values)

    # Compute the MACD histogram as the difference between the MACD line and signal line
    histgram: IndicatorRepresentable = [
        None if (moving_average_value is None or signal_value is None) else (moving_average_value - signal_value)
        for moving_average_value, signal_value in zip(moving_average_line, signal_line)
    ]

    return moving_average_line, signal_line, histgram

