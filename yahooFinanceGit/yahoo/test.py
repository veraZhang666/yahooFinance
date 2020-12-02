import sys,os
current_directory = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.dirname(current_directory) + os.path.sep + ".")
sys.path.append(root_path)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from yahoo import getTickerData
import time
import  datetime
''' 
What does this piece of code do :
1. Create relationship model for mysql database, create two tables,"tickers" and 'symbols'
2. save the csv file in current dierectery to to the database. 
3. provide method for both mannual crawl and atuo crawl

'''


app = Flask(__name__)
# if you try to connect to you database,
# replace
#'mysql+pymysql://root:dbpassword@127.0.0.1:3306/yahoo'
# with
# [datbase user name ]:[password]@[127.0.0.1]:3306/[database name in mysql]
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dbpassword@127.0.0.1:3306/yahoo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Symbol(db.Model):
    __tablename__ = 'symbols'
    id = db.Column(db.Integer,primary_key=True)
    symbolname = db.Column(db.String(64),unique=True)
    url = db.Column(db.String(512))
    crawlTime = db.Column(db.String(512))
    yahoo = db.relationship("Ticker",backref ='symbol')
    def __repr__(self):
        return "id: %d, name: %s, url:%s" % (self.id, self.symbolname, self.url)


class Ticker(db.Model):
    __tablename__= 'tickers'
    id = db.Column(db.Integer, primary_key=True)
    contractname = db.Column(db.String(64))
    last_trade_date = db.Column(db.DateTime)
    strike = db.Column(db.Float)
    last_price = db.Column(db.Float)
    bid = db.Column(db.Float)
    ask = db.Column(db.Float)
    change = db.Column(db.Float)
    change_percent = db.Column(db.Float)
    volume = db.Column(db.Integer)
    open_interest = db.Column(db.Integer)
    implied_volocity = db.Column(db.Float)
    sym_id = db.Column(db.Integer, db.ForeignKey('symbols.id'))
    def __repr__(self):
        return "sym_id:%s %s contractname: %s strike:%.2f lastprice:%.2f bid:%s ask:%s change:%s change%%:%s valume:%s openInterest:%s Implied volocity:%s" % \
               (self.sym_id,self.last_trade_date, self.contractname,self.strike,self.last_price,self.bid,self.ask,self.change,\
                self.change_percent,self.volume,self.open_interest,self.implied_volocity)
def toPythonDatetime(s):
    date,time = s.split(" ")
    year,month,day = date.split("-")
    hour,mins,second = time.split(":")
    dt = datetime.datetime(int(year),int(month),int(day), int(hour), int(mins),int(second))
    return dt

def addData():
    res  = getTickerData.process()
    if res== -1:
        print('No incoming data, Please check Precision and yahoo Finance')
        return -1
    else:
        path = "./symbol.csv"
        if os.path.exists(path):
            file = open(path, 'r')
            df = pd.read_csv(path)
            file.close()
            sm = df.iloc[0, 1]
            url = df.iloc[1, 1]
            print(sm)
            print(url)
            symbolmodel = Symbol.query.filter_by(symbolname =sm).first()
            if symbolmodel !=None:
            # already have this symbol in table 'symbols',just need to insert data into 'tickers'
                 print('symbol exist in db, still saving ticker data from yahoo finance')
            else:
                print("try to save symbols here...")
                smb = Symbol(symbolname=sm, url=url,crawlTime =time.asctime( time.localtime(time.time())) )
                db.session.add(smb)
                db.session.commit()
                print("successfully saved ticker data to mysql!")

         # ----save tickers info to mysql database
            model_list = []
            path1 = './yahoo.csv'
            if os.path.exists(path1):
                file = open(path, 'r')
                df_yahoo= pd.read_csv(path1)
                file.close()
                df_yahoo = df_yahoo.drop(columns=['Unnamed: 0'])
                for i in range(df_yahoo.shape[0]):
                    # find the max_symbol_id in database
                    symbolmodel = Symbol.query.filter_by(symbolname=sm).first()
                    max_sybol_id = symbolmodel.id
                    t = Ticker(
                        contractname=str(df_yahoo.iloc[i, 0]),
                        last_trade_date=toPythonDatetime(df_yahoo.iloc[i, 1]),
                        strike=float(df_yahoo.iloc[i, 2]),
                        last_price=float(df_yahoo.iloc[i, 3]),
                        bid=float(df_yahoo.iloc[i, 4]),
                        ask=float(df_yahoo.iloc[i, 5]),
                        change=float(df_yahoo.iloc[i, 6]),
                        change_percent=float(df_yahoo.iloc[i, 7]),
                        volume=int(df_yahoo.iloc[i, 8]),
                        open_interest=int(df_yahoo.iloc[i, 9]),
                        implied_volocity=float(df_yahoo.iloc[i, 10]),
                        sym_id=max_sybol_id
                    )
                    model_list.append(t)
                    db.session.add_all(model_list)
                    db.session.commit()
                print("successfully saved ticker %s %s to database!"%(sm,url))
        else:
            print("%s not exists." %(path))



if __name__ == '__main__':
    print("Running, please wait ... ... ")
    db.create_all() # when there is no tables in db, run this for only once will create two tables. after create tables in db. mark this as comments

    # addData() # mannual crawl

    # while True:
    #     addData()
    #     time.sleep(3600) # auto crawl, interval every two hours



















