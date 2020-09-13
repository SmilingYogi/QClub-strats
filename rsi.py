import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('stperiod', 5), ('ltperiod', 21), ('rsitperiod',5)
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.signal = 0

        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0].close, period = self.params.stperiod)
        self.rsi = bt.indicators.RelativeStrengthIndex(self.datas[0].close, period = self.params.rsitperiod)
        self.ema = bt.indicators.ExponentialMovingAverage(self.datas[0].close, period = self.params.ltperiod)
        self.cross = bt.indicators.CrossOver(self.sma, self.ema)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f \n' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            
            if self.rsi[0] > 70:
                if (self.cross[0] == 1) :

                    self.log('SELL CREATE, %.2f' % self.dataclose[0])

                    self.signal = -1
                    self.order = self.sell()

            elif self.rsi[0] < 30:
                if (self.cross[0] == -1) :

                    self.log('BUY CREATE, %.2f' % self.dataclose[0])

                    self.signal = 1
                    self.order = self.buy()

        else:  #for checking exit conditions
            if self.signal < 0:
                if self.rsi[0]<= 35 :
                    
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])

                    self.signal = 0
                    self.order = self.buy()

            else:
                if self.rsi[0] >= 65 :
                
                    self.log('SELL CREATE, %.2f' % self.dataclose[0])

                    self.signal = 0
                    self.order = self.sell()
                   


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)
 
    datapath = '/home/srimahn/Desktop/qclub/data/NBANK.csv'

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        dtformat=('%Y-%m-%d'),
        tmformat=('%H.%M.%S'),
        datetime=0,
        high=2,
        low=3,
        open=1,
        close=4,
        volume=5,
        fromdate=datetime.datetime(2015, 1, 1),
        #todate=datetime.datetime(2000, 12, 31),
        )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake = 3)

    # Set the commission
    #cerebro.broker.setcommission(commission=0.005)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()
