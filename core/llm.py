from core.types import immutable, IndicatorRepresentable
from core.price import PriceRepresentable
from core.execution import TradeExecution
from typing import Iterable, Dict, Protocol, runtime_checkable
from enum import Enum
from zoneinfo import ZoneInfo

class PreferredLanguage(Enum):
    ENGLISH = "English"
    CHINESE = "Chinese"

class LocalizableString:
    contents: Dict[PreferredLanguage, str]

    def __init__(self, strings: Dict[PreferredLanguage, str]):
        self.contents = strings

    def get(self, preference: PreferredLanguage):
        return self.contents[preference]

    def append(self, other: 'LocalizableString') -> None:
        for language in self.contents.keys():
            self.contents[language] = self.contents[language] + other.contents[language]

    def append_break(self, prefix: str = '\n', suffix: str = '\n'):
        for language in self.contents.keys():
            self.contents[language] = self.contents[language] + f"{prefix}<break>{suffix}"

    def append_begin(self, prefix: str = '\n', suffix: str = '\n'):
        for language in self.contents.keys():
            self.contents[language] = self.contents[language] + f"{prefix}<begin>{suffix}"

    def append_end(self, prefix: str = '\n', suffix: str = '\n'):
        for language in self.contents.keys():
            self.contents[language] = self.contents[language] + f"{prefix}<end>{suffix}"

@runtime_checkable
class LLMConsumable(Protocol):
    def to_consumable(self) -> LocalizableString:
        ...

@runtime_checkable
class LLMContext(Protocol):
    def build_context(self) -> LocalizableString:
        ...

@immutable
class PriceIndicatorSnapshot(LLMConsumable):
    prices: Iterable[PriceRepresentable]
    rsi: IndicatorRepresentable
    ema20: IndicatorRepresentable
    ema50: IndicatorRepresentable
    window_size: int

    def to_consumable(self) -> LocalizableString:
        result: LocalizableString = LocalizableString({
            PreferredLanguage.ENGLISH: "Symbol: ", PreferredLanguage.CHINESE: "交易代码："
        })
        symbol: str = self.prices[0].symbol.instrument.value
        result.append(LocalizableString({PreferredLanguage.ENGLISH: symbol, PreferredLanguage.CHINESE: symbol}))
        result.append_break()

        price_interval: str = self.prices[0].interval.value
        result.append(LocalizableString({
            PreferredLanguage.ENGLISH: f"Prices & Indicators({price_interval}): ", PreferredLanguage.CHINESE: f"价格指标表（{price_interval}）："
        }))

        result.append(LocalizableString({
            PreferredLanguage.ENGLISH: "Timestamp, Open, High, Low, Close, Volume, EMA20, EMA50, RSI;",
            PreferredLanguage.CHINESE: "时间戳，开盘，最高，最低，收盘，成交量，EMA20，EMA50，RSI；"
        }))
        result.append_begin()

        for index in range(len(self.prices) - self.window_size, len(self.prices)):
            price: PriceRepresentable = self.prices[index]
            rsi_value: str = str(int(self.rsi[index])) if self.rsi[index] is not None else 'nan'
            ema20_value: str = str(int(self.ema20[index])) if self.ema20[index] is not None else 'nan'
            ema50_value: str = str(int(self.ema50[index])) if self.ema50[index] is not None else 'nan'

            values: str = (f"{price.timestamp.astimezone(ZoneInfo('America/New_York')).strftime('%H:%M')}, "
                           f"{int(price.open_price)}, {int(price.high_price)}, {int(price.low_price)},"
                           f" {int(price.close_price)}, {int(price.volume)}, {ema20_value}, {ema50_value}, {rsi_value};\n")

            result.append(LocalizableString({
                PreferredLanguage.ENGLISH: values, PreferredLanguage.CHINESE: values
            }))

        result.append_end(prefix='', suffix='')
        return result

@immutable
class TradeReviewContext(LLMContext):
    executions: Iterable[TradeExecution]
    price_snapshot: PriceIndicatorSnapshot
    comments: LocalizableString

    def build_context(self) -> LocalizableString:
        result: LocalizableString = LocalizableString({
            PreferredLanguage.ENGLISH: "You are now a trade reviewer, and you need to conduct a post-trade analysis "
                                       "of this transaction based on the following information: ",
            PreferredLanguage.CHINESE: "你现在是一位交易复盘师，你需要根据下列信息复盘本次交易："
        })

        for execution in self.executions:
            result.append_begin()

            result.append(LocalizableString({
                PreferredLanguage.ENGLISH: f"At ${execution.buy_price} at {execution.consumable_buy_timestamp} I opened a position ",
                PreferredLanguage.CHINESE: f"我在{execution.consumable_buy_timestamp}以${execution.buy_price}开仓"
            }))
            result.append(LocalizableString({
                PreferredLanguage.ENGLISH: "on short, " if execution.is_sell_before_buy else "on long, ",
                PreferredLanguage.CHINESE: "看空，" if execution.is_sell_before_buy else "看多，"
            }))
            result.append(LocalizableString({
                PreferredLanguage.ENGLISH: f"at ${execution.consumable_sell_timestamp} at {execution.sell_price} I closed the position, ",
                PreferredLanguage.CHINESE: f"{execution.consumable_sell_timestamp}以${execution.sell_price}平仓"
            }))
            result.append(LocalizableString({
                PreferredLanguage.ENGLISH: f"realizing a profit of {execution.profit}."
                                           f"My position settings were a "
                                           f"take-profit at ${execution.take_profit} ({execution.take_profit_rate}% of "
                                           f"total equity) and a stop-loss at ${execution.stop_loss} "
                                           f"({execution.prior_cost_rate}% of total equity). My estimated win rate "
                                           f"was {execution.win_rate}%, with an expected risk-reward ratio of "
                                           f"{execution.reward_risk_ratio}:1 based on this. This trade resulted in a "
                                           f"{execution.posterior_growth_rate}% growth in the account. ",
                PreferredLanguage.CHINESE: f"盈利${execution.profit}。"
                                           f"我的仓位设置是，${execution.take_profit}止盈（{execution.take_profit_rate}%总资产），"
                                           f"${execution.stop_loss}止损（{execution.prior_cost_rate}%总资产）。我的预估胜率是{execution.win_rate}%，"
                                           f"基于此的期望盈亏比是{execution.reward_risk_ratio}:1。本单实现{execution.posterior_growth_rate}%的账户增长。"
            }))
            result.append_end(suffix='')

        result.append_break()
        result.append(LocalizableString({
            PreferredLanguage.ENGLISH: "Below are the price and indicator data for that period: ",
            PreferredLanguage.CHINESE: "下面是那段时间的价格和指标数据："
        }))

        result.append_break()
        result.append(self.price_snapshot.to_consumable())

        result.append_break()
        result.append(self.comments)

        result.append_break()
        result.append(LocalizableString({
            PreferredLanguage.ENGLISH: "Based on the information above, provide a post-trade analysis.",
            PreferredLanguage.CHINESE: "基于上述信息进行交易复盘。"
        }))

        return result
