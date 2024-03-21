import pandas as pd
from collections import deque
from event_driven_backtest.event import MarketEvent

class DataHandler:
    def __init__(self, events):
        self.events = events
        self.all_data = {}

        # 存放bar生成器
        self.bar_generator_dict = {}

        # 存放生成的bar数据
        self.latest_data = {}

        # 存放bars_columnns
        self.bars_columns_dict = {}

        self.continue_backtest = True
        
    def load_data(self, data_folder_path, contract_list, start_time: str = None, end_time: str = None):
        for contract_name in contract_list:
            # 从本地文件获取数据
            data_path = f"{data_folder_path}/{contract_name}.parquet"
            df_data = pd.read_parquet(data_path)

            # 数据清洗
            data_list, bars_columns = clean_data_by_date(df_data, start_time, end_time)
            self.all_data[contract_name] = data_list
            self.bars_columns_dict[contract_name] = bars_columns

            # 为每一个品种创建一个生成器
            self.bar_generator_dict[contract_name] = self._get_new_bar(contract_name)
    
    def _get_new_bar(self, contract_name):
        for i in range(len(self.all_data[contract_name])):
            yield tuple(self.all_data[contract_name][i])       # row代表一行数据

    def update_bars_by_contract(self, 
                    contract_name, 
                    market_trigger_size: int = 20, # 触发策略需要的最小数据量
                    max_len: int = 10000, # 限制内存存储的最大数据量
                    ):
        '''
        时序策略: 针对单一品种更新数据
        '''
        market_trigger = True
        try:
            # next调用生成器，从数据里面拿出新的一行
            bar = next(self.bar_generator_dict[contract_name])  
        except StopIteration:
            self.continue_backtest = False
        else:
            if bar is not None:
                if contract_name not in self.latest_data:
                    self.latest_data[contract_name] = deque(maxlen=max_len)
                self.latest_data[contract_name].append(bar)

        # 生成market event
        if len(self.latest_data[contract_name]) < market_trigger_size:
            market_trigger = False

        if market_trigger:
            self.events.put(MarketEvent(contract_name))

    def get_latest_bars(self, symbol, N=5):
        try:
            bars = list(self.latest_data[symbol])
        except KeyError:
            print("That symbol is not available in the historical data set.")
        else:
            return bars[-N:]
        
    def update_bars_by_contracts(self, contract_list):
        '''
        每个截面期更新所有contract数据
        '''
        pass

def clean_data_by_date(df, start_date, end_date):
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.sort_values('trade_date', inplace=True)
    data_list = df[(df['trade_date'] >= start_date) & (df['trade_date'] <= end_date)].to_numpy().tolist()
    bars_columns = df.columns
    return data_list, bars_columns 
    

