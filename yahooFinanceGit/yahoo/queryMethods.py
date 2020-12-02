import  datetime
from yahoo.test import Symbol,Ticker
from sqlalchemy import and_
from pprint import pprint
'''  here just provide query operation for mysql  for other module'''

def check_last5_day_for_all():
    now = datetime.datetime.now()
    nowMinus5 = now + datetime.timedelta(days=-5)  #
    print('From %s to %s'%(nowMinus5,now))
    qry = Ticker.query.filter(Ticker.last_trade_date.between(nowMinus5, now)).all()
    pprint(qry)
    return qry

def check_last5_day_by_name(name):
    print('symbol name : %s'%(name))
    now = datetime.datetime.now()
    nowMinus5 = now + datetime.timedelta(days=-5)  #
    pprint('From %s to %s'%(nowMinus5,now))
    sm = Symbol.query.filter(Symbol.symbolname ==name).first()
    qry = Ticker.query.filter(and_(Ticker.last_trade_date.between(nowMinus5, now), Ticker.sym_id == sm.id)).all()
    model = Ticker.query.filter(and_(Ticker.last_trade_date.between(nowMinus5, now), Ticker.sym_id == sm.id))
    pprint(qry)
    return model
def check_last5_day_by_names(symlist):
    l = []
    for name in symlist:
        l.append(check_last5_day_by_name(name))
    return l