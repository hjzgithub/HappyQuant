import datetime
from queue import Queue
import importlib

# 导入本地库
from utils.log_tools import output
from event_driven_backtest.data_handler import DataHandler
from event_driven_backtest.portfolio_manager import PortfolioManager
from event_driven_backtest.sim_exchange import SimExchange

class BackTestEngine:
    def init_engine(self, init_cash, start_time: str, end_time: str):

        # 初始化现金
        self.init_cash = init_cash

        # 初始化日期
        self.start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d")
        self.end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d")

        # 初始化事件队列
        self.events = Queue() # 由于事件队列是可变对象，所以传入到其他类里面，会使其发生改变

        # 初始化一些对象
        self.bars = DataHandler(self.events)
        self.strategies = {}

        # 这里mypm和mydh的self.events是互通的吗
        self.init_path()

    def init_path(self):
        '''
        初始化文件路径
        '''
        self.sample_folder_path = 'happyquant/sample_data'
    
    def init_strategies(self, strategy_name, **params):
        '''
        初始化策略参数
        '''
        strategy_file = ".".join(["event_driven_backtest", "strategies", strategy_name]) # 这个路径需要放在yaml文件里面
        strategy_module = importlib.import_module(strategy_file)
        model_class = getattr(strategy_module, strategy_name)
        self.strategies[strategy_name] = model_class(self.bars, self.events)
        self.strategies[strategy_name].set_params(**params)

        self.init_contract_info(params['contract_list'])

    def init_contract_info(self, contract_list, cost_rules = None):
        '''
        交易费用等信息应该保存在某个文件夹
        '''
        self.contract_list = contract_list
        self.cost_rules = cost_rules

    def run_backtest(self, strategy_name):
        output('========= 开始历史数据回放 ========')
        self.bars.load_data(self.sample_folder_path, self.contract_list, self.start_time, self.end_time)
        
        for contract_name in self.contract_list:
            self.bars.continue_backtest = True

            self.pm = PortfolioManager(self.bars, self.events, self.init_cash, self.start_time)  
            self.pm.init_contract_positions(contract_name)

            # 仓位信息需要放在模拟交易所
            self.sim_exchange = SimExchange(self.bars, self.pm, self.events, costs_rate=0)

            self.strategies[strategy_name].set_bars_columns(self.bars.bars_columns_dict[contract_name])

            max_iterations = 2000 # 控制循环次数
            count = 0
            while True:

                output("======== Before Trading ========")
                output(self.pm.all_holdings[-1])  
                output(self.pm.current_positions)

                # 每次更新bar，就插入一个market事件，每次取出market事件，就得到一个signal
                if self.bars.continue_backtest == True:
                    self.bars.update_bars_by_contract(contract_name)
                else:
                    break

                while True:
                    
                    try:
                        # 从事件队列中获取事件
                        event = self.events.get(False)
                    except:
                        # 如果没有事件，则跳出循环
                        break
                    else:
                        if event is not None:
                            output(f"======== {event.type} ========")
                
                            output(vars(event))

                            if event.type == 'MARKET':
                                self.strategies[strategy_name].get_signal(event) # 调用策略模块，所有合约的market事件全部解决后，才轮到signal event

                            elif event.type == 'SIGNAL':
                                self.pm.generate_order(event) # 将signal转化为order

                            elif event.type == 'ORDER':
                                self.sim_exchange.execute_order(event) # 将order转化为fill

                            elif event.type == 'FILL':
                                self.pm.update_fill(event)
                        else:
                            break

                if self.bars.continue_backtest == True:
                    output("======== After Trading ========")
                    self.pm.daily_summary()

                count += 1

                # 检查退出条件
                if count >= max_iterations:
                    break
            
            self.pm.summary(contract_name, strategy_name=strategy_name)

        output("======== 回测结束 ========")