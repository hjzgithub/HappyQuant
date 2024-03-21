import datetime
from event_driven_backtest.event import FillEvent

class SimExchange:
    def __init__(self, bars, pm, events, multiplier = 1, costs_rate = 2.5/10000):
        self.bars = bars
        self.pm = pm
        self.events = events
        self.multiplier = multiplier
        self.costs_rate = costs_rate
    
    def execute_order(self, event):
        if event.type == 'ORDER':
        
            # 取最后一期作为成交价
            latest_bars = self.bars.get_latest_bars(event.contract_name, 1)[0]
            fill_time = latest_bars[1]
            fill_direction = event.order_direction
            fill_price = latest_bars[2] 
            
            self.pm.current_holdings['record_time'] = fill_time
            
            fill_unit = 0
            if fill_direction == 'BUY':
                while fill_unit < event.order_unit:
                    # 一个一个地成交
                    fill_value = 1 * self.multiplier * fill_price
                    fill_costs = self.costs_rate * fill_value
                    if self.pm.current_holdings['cash'] < fill_value + fill_costs:
                        break
                    else:
                        self.pm.current_holdings['cash'] -= (fill_value + fill_costs)

                        self.pm.current_holdings['costs'] += fill_costs
                        self.pm.current_holdings[event.contract_name] += fill_value
                        self.pm.current_positions[event.contract_name] += 1 * self.multiplier
                    fill_unit += 1

            elif fill_direction == 'SELL':
                while fill_unit < event.order_unit:
                    # 一个一个地成交
                    fill_value = 1 * self.multiplier * fill_price
                    fill_costs = self.costs_rate * fill_value
         
                    self.pm.current_holdings['cash'] += (fill_value - fill_costs)

                    self.pm.current_holdings['costs'] += fill_costs

                    if self.pm.current_holdings[event.contract_name] < fill_value:
                        self.pm.current_holdings[event.contract_name] = 0
                    else:
                        self.pm.current_holdings[event.contract_name] -= fill_value

                    self.pm.current_positions[event.contract_name] -= 1 * self.multiplier
                    fill_unit += 1

            fill_event = FillEvent(
                datetime.datetime.now(),
                'XSHG',
                event.contract_name,
                fill_time,
                fill_direction, 
                fill_price, 
                fill_unit,
                fill_costs
            ) 
            self.events.put(fill_event)