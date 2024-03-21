from event_driven_backtest.strategies.template import BaseStrategy
from event_driven_backtest.event import MarketEvent, SignalEvent
import pandas as pd

class DoubleMAStrategy(BaseStrategy):
    def __init__(self, *args) -> None:
        super(DoubleMAStrategy, self).__init__(*args)

    def get_signal(self, event: MarketEvent):
        if event.type == 'MARKET':
            bars = self.bars.get_latest_bars(event.contract_name, N=20) # 导入全部合约数据，分开获取合约数据
            df_raw = pd.DataFrame(bars, columns=self.bars_columns)

            signal_time = df_raw.loc[df_raw.index[-1], 'trade_date'] # 这个有点问题

            double_ma_5_20 = df_raw.loc[df_raw.index[-5:], 'close'].mean() - df_raw.loc[df_raw.index[-20:], 'close'].mean()
            
            # 1 代表看多 -1 代表看空
            signal_type = 'class'
            signal_value = 1 if double_ma_5_20 > 0 else -1

            # 取最后一期作为决定价格
            decision_price = df_raw.loc[df_raw.index[-1], 'close']

            signal = SignalEvent(signal_time, event.contract_name, signal_type, signal_value, decision_price) 
            self.events.put(signal)