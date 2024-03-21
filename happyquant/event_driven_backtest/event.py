class Event(object):
    """
    Event is base class providing an interface for all subsequent 
    (inherited) events, that will trigger further events in the 
    trading infrastructure.   
    """
    pass

class MarketEvent(Event):
    def __init__(self, contract_name):
        self.type = 'MARKET'
        self.contract_name = contract_name

class SignalEvent(Event):
    def __init__(self, signal_time, contract_name, signal_type, signal_value, decision_price):
        self.type = 'SIGNAL'
        self.signal_time = signal_time
        self.contract_name = contract_name
        self.signal_type = signal_type
        self.signal_value = signal_value
        self.decision_price = decision_price

class OrderEvent(Event):
    def __init__(self, contract_name, order_type, order_direction, order_unit):
        self.type = 'ORDER'
        self.contract_name = contract_name
        self.order_type = order_type
        self.order_direction = order_direction
        self.order_unit = order_unit

class FillEvent(Event):
    def __init__(self, record_time, exchange, contract_name, fill_time, fill_direction, fill_price, fill_unit, costs):
        self.type = 'FILL'
        self.record_time = record_time
        self.exchange = exchange
        self.contract_name = contract_name
        self.fill_time = fill_time
        self.fill_direction = fill_direction
        self.fill_price = fill_price
        self.fill_unit = fill_unit
        self.costs = costs