import queue
import py_files.online_trader_advisor as ota
import pandas as pd
import numpy as np

class TurtleBuyOnlyOnlineStrategy(ota.OnlineStrategiesCrypto):
    """
    Simple only buy turtle strat
    Code is messy
    """
    def __init__(self, parameters_dict):
        super(TurtleBuyOnlyOnlineStrategy, self).__init__(parameters_dict)
        self.buy_coefficient = parameters_dict['buy_coefficient']
        self.sell_coefficient = parameters_dict['sell_coefficient']
        self.delta1 = parameters_dict['delta1']
        self.delta2 = parameters_dict['delta2']
        assert self.time_resolution_delta == self.delta2, print("Time resolutions must equal: delta==delta1")
        self.window_delta1 = parameters_dict['window_delta1']
        self.window_delta2 = parameters_dict['window_delta2']
        self.high_delta1 = queue.Queue(self.window_delta1)
        self.low_delta1 = queue.Queue(self.window_delta2)
        self.high_minus_low_delta1 = queue.Queue(self.window_delta1)
        self.counter = 0
        self.high_delta2 = 0
        self.low_delta2 = np.inf
        self.turtle_upper_bound = 0
        self.turtle_lower_bound = 0
        self.turtle_TR_queue = queue.Queue(self.window_delta1)
        self.turtle_TR = 0
        self.turtle_N = 0
        self.price = 0
        self.initial_feeder_done = 0
        self.buy_order_floating = []

    def initial_feeder(self, feed):
        """
        feed mid price

        """

        if feed == []:
            self.initial_feeder_done = 0

        else:
            assert len(feed) == self.window_delta1 * int(self.delta1 / self.delta2), "No match data size in the initial price feeder"

            for i, x in enumerate(feed):

                if ((i) % int(self.delta1 / self.delta2) == 0) & (i > 0):

                    if (self.high_delta1.full()):
                        self.high_delta1.get()
                        self.high_delta1.put(self.high_delta2)

                    else:
                        self.high_delta1.put(self.high_delta2)

                    if (self.low_delta1.full()):
                        self.low_delta1.get()
                        self.low_delta1.put(self.low_delta2)

                    else:
                        self.low_delta1.put(self.low_delta2)

                    TR = max(np.abs(self.high_delta2 - self.low_delta2),
                             np.abs(x - self.low_delta2),
                             np.abs(self.high_delta2 - x))

                    if self.turtle_TR_queue.full():
                        self.turtle_TR_queue.get()
                        self.turtle_TR_queue.put(TR)

                    else:
                        self.turtle_TR_queue.put(TR)

                    self.turtle_N = np.mean(list(self.turtle_TR_queue.queue))
                    self.turtle_upper_bound = np.max(list(self.high_delta1.queue))
                    self.turtle_lower_bound = np.min(list(self.low_delta1.queue))
                    self.high_delta2 = 0
                    self.low_delta2 = np.inf

                else:
                    self.high_delta2 = max(self.high_delta2, x)
                    self.low_delta2 = min(self.low_delta2, x)

            self.initial_feeder_done = 1

    def update(self, feed):
        x = feed['bid'] / 2 + feed['ask'] / 2

        if ~self.initial_feeder_done:

            if (self.counter == self.window_delta1 * int(self.delta1 / self.delta2)):
                self.initial_feeder_done = 1

            else:

                if ((self.counter) % int(self.delta1 / self.delta2) == 0) & (self.counter > 0):

                    if (self.high_delta1.full()):
                        self.high_delta1.get()
                        self.high_delta1.put(self.high_delta2)
                    else:
                        self.high_delta1.put(self.high_delta2)

                    if (self.low_delta1.full()):
                        self.low_delta1.get()
                        self.low_delta1.put(self.low_delta2)

                    else:
                        self.low_delta1.put(self.low_delta2)

                    TR = max(np.abs(self.high_delta2 - self.low_delta2),
                             np.abs(x - self.low_delta2),
                             np.abs(self.high_delta2 - x))

                    if self.turtle_TR_queue.full():
                        self.turtle_TR_queue.get()
                        self.turtle_TR_queue.put(TR)

                    else:
                        self.turtle_TR_queue.put(TR)

                    self.turtle_N = np.mean(list(self.turtle_TR_queue.queue))
                    self.turtle_upper_bound = np.max(list(self.high_delta1.queue))
                    self.turtle_lower_bound = np.min(list(self.low_delta1.queue))
                    self.high_delta2 = 0
                    self.low_delta2 = np.inf

                else:
                    self.high_delta2 = max(self.high_delta2, x)
                    self.low_delta2 = min(self.low_delta2, x)

        if self.initial_feeder_done:

            if ((self.counter) % int(self.delta1 / self.delta2) == 0):

                if (self.high_delta1.full()):
                    self.high_delta1.get()
                    self.high_delta1.put(self.high_delta2)
                else:
                    self.high_delta1.put(self.high_delta2)

                if (self.low_delta1.full()):
                    self.low_delta1.get()
                    self.low_delta1.put(self.low_delta2)
                else:
                    self.low_delta1.put(self.low_delta2)

                TR = max(np.abs(self.high_delta2 - self.low_delta2),
                         np.abs(x - self.low_delta2),
                         np.abs(self.high_delta2 - x))

                if self.turtle_TR_queue.full():
                    self.turtle_TR_queue.get()
                    self.turtle_TR_queue.put(TR)
                else:
                    self.turtle_TR_queue.put(TR)

                self.turtle_N = np.mean(list(self.turtle_TR_queue.queue))
                self.turtle_upper_bound = np.max(list(self.high_delta1.queue))
                self.turtle_lower_bound = np.min(list(self.low_delta1.queue))
                self.high_delta2 = 0
                self.low_delta2 = np.inf

            elif ((self.counter) % int(self.delta1 / self.delta2) != 0):
                self.high_delta2 = max(self.high_delta2, x)
                self.low_delta2 = min(self.low_delta2, x)

        self.counter = self.counter + 1

    def buy(self, feed):
        self.capital_before_lastbuy = max(self.capital, self.capital_before_lastbuy)
        self.capital_floating = self.crypto_initial * feed['bid'] * (1 - self.fees)
        self.add_msg1 = 'Capital before last buy :' + str(self.capital_before_lastbuy)
        self.add_msg2 = ', Capital floating :' + str(self.capital_floating)

    if ( feed['ask'] > self.turtle_upper_bound and len(self.buy_order_floating) == 0 ):
            self.capital_before_lastbuy = self.capital
            step = self.capital * (1.0 - self.fees)
            self.crypto_initial += np.round(step / feed['ask'], 8)
            self.capital = 0.0  # all capital used
            self.stop_loss = feed['ask'] - self.buy_coefficient * self.turtle_N  # set stop loss

            self.positions += [{"time": feed['timestamp'], "symbol": self.crypto_symbol, "price": feed['ask'], 'order': 'buy'}]
            self.buy_order_floating = self.positions[-1]
            self.send_email_order(self.positions[-1], self.add_msg1 + self.add_msg2)
            self.buy_order_floating = self.positions.copy()

    def sell(self, feed):

        if len(self.buy_order_floating) > 0 and (
                feed['bid'] < self.turtle_lower_bound  # we are lower than lower bound
                or feed['bid'] < self.stop_loss * self.sell_coefficient  # we are lower than stop loss
        ):
            self.positions += [
                {"time": feed['timestamp'], "symbol": self.crypto_symbol, "price": feed['bid'], 'order': 'sell'}]
            self.capital = self.crypto_initial * feed['bid'] * (1 - self.fees)
            self.capital_floating = self.capital
            self.capital_before_lastbuy = self.capital
            self.stop_loss, self.crypto_initial = 0.0, 0.0
            self.buy_order_floating = []
            self.add_msg1 = 'Capital before last buy :' + str(self.capital_before_lastbuy)
            self.add_msg2 = ', Capital floating :' + str(self.capital_floating)
            self.send_email_order(self.positions[-1], self.add_msg1 + self.add_msg2)

    def print_capital(self ):

        print('Capital before last buy order: ', self.capital_before_lastbuy)
        print('Capital floating: ', self.capital_floating)

    def run(self, feed):

        self.update(feed)

        if self.initial_feeder_done:
            self.buy(feed)
            self.sell(feed)






