
from test import Ticker,Symbol
import matplotlib.pyplot as plt
from yahoo import queryMethods
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
''' run method below to take look at the stock exchange information , as well as the visualizaiton '''

engine = create_engine('mysql+pymysql://root:dbpassword@127.0.0.1:3306/yahoo') # if you try to run the code, change this to your db configuration.
Session = sessionmaker()
Session.configure(bind=engine)
sess = Session()

def savefig(X,Y,path):
    fig = plt.figure(figsize=(20, 8), dpi=100)
    plt.bar(X, Y, width=0.2, label="")
    plt.title("Rank by implied volocity", fontsize=30, color='r')
    plt.show()
    fig.savefig(path, format='png', transparent=True, dpi=300, pad_inches=0)

def vizVolocity(symbolname):
    dates = []
    cname = []
    volocity = []
    for instance in queryMethods.check_last5_day_by_name(symbolname):
        dates.append(instance.last_trade_date)
        cname.append(instance.contractname)
        volocity.append(instance.implied_volocity)
    stock_df = pd.concat([pd.Series(data=dates),pd.Series(data=cname),pd.Series(data=volocity)],axis=1)
    savefig(stock_df.iloc[:,1],stock_df.iloc[:,2],'./plots/volocity.png')
    print(stock_df)

def vizInterest(symbolname):
    dates = []
    cname = []
    volocity = []
    for instance in queryMethods.check_last5_day_by_name(symbolname):
        dates.append(instance.last_trade_date)
        cname.append(instance.contractname)
        volocity.append(instance.open_interest)
    stock_df = pd.concat([pd.Series(data=dates), pd.Series(data=cname), pd.Series(data=volocity)], axis=1)
    savefig(stock_df.iloc[:, 1], stock_df.iloc[:, 2],'./plots/openinterest.png')
    print(stock_df)


'''Run those method will save the figure for volocity for the past 5 days for symbol 'CASH',path: './yahoo/volocity.png'''
'''
1.The implied volatility indicate risk level of this share, it's been predicted by the market price model, the higher this number is, 
in the future this share will largely go up  or down, vice versa.
'''
# vizVolocity('EMN')

'''
2. The open interest indicate the how many open contract out there. it can go and down or flat, this indicate the transaction .
'''
vizInterest('EMN')


'''run thouse method to print data list in the output area.'''
# queryMethods.check_last5_day_for_all()
# queryMethods.check_last5_day_by_name('EMN')
# queryMethods.check_last5_day_by_names(['EMN','CASH'])



