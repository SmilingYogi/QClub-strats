import datetime  
import backtrader as bt
import os
import argparse
from strats import RSI_GCross, BB

parser = argparse.ArgumentParser(description='Backtest the strategy')
parser.add_argument('-df','--datafile',type=str,default='NBANK.csv',help='Path to the data file')
parser.add_argument('-C','--CASH',type=float,default=100000.0,help='Total Cash')
parser.add_argument('-S','--STAKE',type=float,default=3,help='Stake')
parser.add_argument('-CM','--COMMISSION',type=float,default=0.001,help='Commission')

args = parser.parse_args()

cerebro = bt.Cerebro()

# Add/Change the strategy
# You may want to change the default cash for different strategy
cerebro.addstrategy(RSI_GCross)

datapath = os.getcwd() + '/data/'+ args.datafile

# Creating a Data Feed
data = bt.feeds.GenericCSVData(
    dataname=datapath,
    dtformat=('%Y-%m-%d'),   #You need to change the date format according to the datafile
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

cerebro.adddata(data)

cerebro.broker.setcash(args.CASH)
cerebro.addsizer(bt.sizers.FixedSize, stake = args.STAKE)
cerebro.broker.setcommission(commission= args.COMMISSION)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.plot()
