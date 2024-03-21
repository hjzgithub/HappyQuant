from event_driven_backtest import backtest_engine
import joblib

def main(strategy_name):
    be_test = backtest_engine.BackTestEngine()
    be_test.init_engine(
        init_cash=10000, 
        start_time='2019-01-01', 
        end_time='2023-12-31',
    )

    # 实现多品种多策略（独立账户）的时序策略的回测
    be_test.init_strategies(
        strategy_name,
        contract_list=['000016', '000300'],
    )
    be_test.run_backtest(strategy_name)

if __name__ == "__main__":
    strategy_list = ['DoubleMAStrategy', 'TSMomentumStrategy']

    '''
    # 单进程
    for strategy_name in strategy_list:
        main(strategy_name)
    '''

    # 多进程
    joblib.Parallel(n_jobs=min(16, len(strategy_list)), backend='loky', verbose=0)(
        joblib.delayed(main)(
            strategy_name
        ) for strategy_name in strategy_list
    )