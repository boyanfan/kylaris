from core.indicators import *
from core.price import *
from core.utilities import datetime_from_past, datatime_now

def main():
    print("Welcome to Kylaris! Here are prices of ETH:")

    prices: Iterable[PriceRepresentable] = BinancePriceProvider().fetch(PriceProviderContext(
        symbol=MarketIdentifier(instrument=TradableInstrument.ETHUSDT, category=TradableCategory.crypto),
        interval=PriceInterval.minute15, start_time=datetime_from_past(hours=4), end_time=datatime_now(), limit=None
    ))

    print(prices)
    print(f"MA5: {exponential_moving_average(prices=prices, period=5)}")
    print(f"RSI: {relative_strength_index(prices=prices, period=14)}")
    print(f"MACD: {moving_average_convergence_divergence(prices=prices, fast_period=12, slow_period=6, signal_period=9)}")

if __name__ == '__main__':
    main()