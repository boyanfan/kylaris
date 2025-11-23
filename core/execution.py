from core.types import immutable

@immutable
class TradeExecution:
    consumable_buy_timestamp: str
    consumable_sell_timestamp: str
    buy_price: float
    sell_price: float
    profit: float
    take_profit: float
    take_profit_rate: float
    stop_loss: float
    reward_risk_ratio: float
    win_rate: float
    prior_cost_rate: float
    posterior_growth_rate: float
    is_sell_before_buy: bool