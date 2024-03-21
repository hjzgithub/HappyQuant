class BaseStrategy:
    def __init__(self, bars, events) -> None:
        self.bars = bars 
        self.events = events

    def set_params(self, **params):
        self.params = params

    def set_bars_columns(self, bars_columns):
        self.bars_columns = bars_columns