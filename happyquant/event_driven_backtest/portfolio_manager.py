import os
import pandas as pd

from event_driven_backtest.event import OrderEvent
from utils.log_tools import output
from utils.plot_tools import get_series_plot

class PortfolioManager:
    def __init__(self, bars, events, init_cash, start_time):
        self.bars = bars
        self.events = events
        self.init_cash = init_cash
        self.start_time = start_time

        # 初始化持仓信息
        self.all_holdings = [
            {
                'record_time': self.start_time,
                'total_asset': self.init_cash,
                'cash': self.init_cash,
            }
        ]
        self.current_holdings = {
            'record_time': self.start_time,
            'cash': self.init_cash, 
            'costs': 0,
        }

        self.all_positions = [{}]
        self.current_positions = {}

    def init_contract_positions(self, contract_name):
        # 添加品种信息
        self.all_holdings[-1][contract_name] = 0
        self.all_positions[-1][contract_name] = 0
        self.current_holdings[contract_name] = 0
        self.current_positions[contract_name] = 0

    def generate_order(self, event, order_type: str = 'MKT'):
        if event.type == 'SIGNAL':
            if event.signal_type == 'class':
                # 先确定目标权重
                target_weight = 1 if event.signal_value == 1 else 0

                # 将目标仓位进行向下取整
                target_position = int(self.all_holdings[-1]['total_asset'] * target_weight / event.decision_price)

                current_position = self.all_positions[-1][event.contract_name]
            
            if order_type == 'MKT':
                if target_position > current_position:
                    order_direction = 'BUY'
                    order_unit = abs(target_position-current_position)
                    order = OrderEvent(event.contract_name, order_type, order_direction, order_unit)
                elif target_position < current_position:
                    order_direction = 'SELL'
                    order_unit = abs(target_position-current_position)
                    order = OrderEvent(event.contract_name, order_type, order_direction, order_unit)
                else:
                    order = None
            self.events.put(order)

    def update_fill(self, event):
        if event.type == 'FILL':
            self.update_all_positions()             # 这个的意义是将current_position同步到all_positions

    def update_all_positions(self):
        self.all_positions.append(self.current_positions)

    def daily_summary(self):
        # 这里需要得到close_price，更新holding_value
        for contract_name, position in self.current_positions.items():
            close_price = self.bars.get_latest_bars(contract_name, 1)[0][2]
            self.current_holdings[contract_name] = close_price * position

        holdings_dict = {}
        for contract_name, value in self.current_holdings.items():
            if contract_name not in ['record_time', 'costs']:
                holdings_dict[contract_name] = value

        total_asset = sum(holdings_dict.values())
        holdings_dict['total_asset'] = total_asset

        record_time = self.bars.get_latest_bars(contract_name, 1)[0][1]
        holdings_dict['record_time'] = record_time
        self.all_holdings.append(holdings_dict)

    def summary(self, contract_name, **kwargs):
        save_folder_path = 'happyquant/sample_results'
        os.makedirs(save_folder_path, exist_ok=True)

        df_res = pd.DataFrame(self.all_holdings[1:])
        df_res.set_index('record_time', inplace=True)
        output(df_res)

        save_id = f"pnl_{contract_name}_{kwargs['strategy_name']}"
        df_res.to_csv(f'{save_folder_path}/{save_id}.csv')
        get_series_plot(df_res['total_asset'], save_folder_path, save_id)
