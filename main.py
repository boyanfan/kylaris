from core.indicators import *
from core.price import *
from core.llm import *
from core.execution import *
from core.utilities import datetime_from_past, datatime_now

def main():
    prices: Iterable[PriceRepresentable] = BinancePriceProvider().fetch(PriceProviderContext(
        symbol=MarketIdentifier(instrument=TradableInstrument.ETHUSDT, category=TradableCategory.crypto),
        interval=PriceInterval.minute15, start_time=datetime_from_past(hours=24), end_time=datatime_now(), limit=None
    ))

    prompt: LocalizableString = TradeReviewContext(executions=[
        TradeExecution(
            consumable_buy_timestamp='2025/11/22 17:13', consumable_sell_timestamp='2025/11/22 17:53',
            buy_price=2755, sell_price=2783, profit=-71.08, take_profit=102,
            take_profit_rate=4.7, stop_loss=67, reward_risk_ratio=1.53, win_rate=44, prior_cost_rate=3.09,
            posterior_growth_rate=-3.29, is_sell_before_buy=True
        ),
        TradeExecution(
            consumable_buy_timestamp='2025/11/22 17:55', consumable_sell_timestamp='2025/11/22 18:45',
            buy_price=2792, sell_price=2768, profit=31.39, take_profit=44,
            take_profit_rate=2.1, stop_loss=33.65, reward_risk_ratio=-1, win_rate=-1, prior_cost_rate=1.61,
            posterior_growth_rate=1.5, is_sell_before_buy=True
        )
    ], price_snapshot=PriceIndicatorSnapshot(
        prices=prices, rsi=relative_strength_index(prices=prices, period=14),
        ema20=exponential_moving_average(prices=prices, period=20), ema50=exponential_moving_average(prices=prices, period=50),
        window_size=48
    ), comments=LocalizableString({
        PreferredLanguage.ENGLISH: "-1 in ratios and rates indicates not available.",
        PreferredLanguage.CHINESE: "价格一整个下午都横盘在$2750附近没有波动，而我却想要为了开单而开单导致了亏损，这是基于猜测而非指标的开仓。"
                                   "而连开的第二单则是完全出于补救心理，在亏损一单后急于开新单来补救上一单的损失。"
                                   "另外你无需自己计算盈利数额，因为是杠杆合约交易以及额外的手续费，所以盈利并不直接来自买入与卖出的价差."
    })).build_context()
    print(prompt.get(PreferredLanguage.CHINESE))

    # print(prompt.get(PreferredLanguage.ENGLISH))
    # print(prices)
    # print(f"MA5: {exponential_moving_average(prices=prices, period=5)}")
    # print(f"RSI: {relative_strength_index(prices=prices, period=14)}")
    # print(f"MACD: {moving_average_convergence_divergence(prices=prices, fast_period=12, slow_period=6, signal_period=9)}")
    # print(f"ATR: {average_true_range(prices=prices, period=14)}")

if __name__ == '__main__':
    main()
