import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib3
import os
''' 
What does this piece of code do :
1. Get data from the cision new and Yahoo Finance,Then save it as csv to current directory.

'''
#-------data aquisition--------------
def get_html_page(url):
    headers = {
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
     }
    urllib3.disable_warnings()
#     requests.packages.urllib3.disable_warnings()
    response = requests.get(url,headers=headers,verify=False)
    response_str = ''
    if response.status_code == 200:
        response_str = response.content.decode()
    return response_str

'''
# 1. locate the news by <a class = ticket-symbol>
'''
def tickerFromCision(url):
    htmlPage_str = get_html_page(url)
    bs = BeautifulSoup(htmlPage_str,"lxml")
    a_ResultSet = bs.find_all('a',class_ ="news-release")

    first_part = "https://www.prnewswire.com/{}"
    symbol_list= []
    url_list = []
    i=0
    for ele in a_ResultSet: # continue to find the news have ticker, and return the first one.
        print('Searching for news %d'%(i),end='')
        i+=1
        second_part= ele['href']
        news_url = first_part.format(second_part)
        news_page_str = get_html_page(news_url)
        bs1 = BeautifulSoup(news_page_str,"lxml")
        # <a class="ticket-symbol" data-toggle="modal" href="#financial-modal">REGN</a>
        tag = bs1.find(name="a", attrs={"class" :"ticket-symbol"})

        if tag != None:
            symbol_list.append(tag.string)
            url_list.append(news_url)
            print(" ",tag.string,news_url)
        else:
            print(' no ticker')

    if symbol_list: # if there is at least one symbol in list
        c = pd.DataFrame(data=[symbol_list,url_list])
        tdf = pd.DataFrame(c.values.T)
        return tdf
    else:
        print('No symbol in all news.')
        return pd.DataFrame()

def getData(): # return symboldf, column names, row list
    url = "https://www.prnewswire.com/news-releases/news-releases-list/"
    symbol_df = tickerFromCision(url)

    if symbol_df.empty == False:
        tickerList = symbol_df.iloc[:,0].tolist() # all symbols
        for symbol in tickerList:
            if symbol == None: continue
            url = 'https://finance.yahoo.com/quote/{}/options?'.format(symbol)
            print(url)
            response = get_html_page(url)
            soup = BeautifulSoup(response,"lxml")
            tag = soup.find(name='tr', class_="C($tertiaryColor)")
            if tag == None: # In yahoo finance, if this ticker has no data, in 'option'
                print("Option data for ticker %s is not available in yahoo finance,locating next tiker"%(symbol))
            else:
                 spans = tag.find_all(name='span')
                 colmuns_name = [ele.string for ele in spans]  # ----step 1 get colmns names---
                 firstrow = soup.find(name='tr',
                             class_="data-row0 Bgc($hoverBgColor):h BdT Bdc($seperatorColor) H(33px) in-the-money Bgc($hoverBgColor)")
                 restrows = firstrow.find_next_siblings()  # -----step 2 get data list------
                 row_list = []
                 tem1 = []

                 for ele in firstrow:
                    tem1.append(ele.string)

                 row_list.append(tem1)# add first row in yahoo dataframe

                 for ele in restrows:
                    temp = []
                    for inner in ele:
                        temp.append(inner.string) # one row of data frame in yahooo finance
                    row_list.append(temp)
                 sybol_df = pd.DataFrame(data=[symbol, url])

                 return sybol_df,colmuns_name,row_list
                 # we only want the data from the first ticker(that have data in yahoo finance in 'option'),so we break in here as long as find it.
    else:
        print('No symbol in the latest news list')
        return -1

def removeSimpbol(row_list):
    for li in row_list:
        for i in range(len(li)):
            if ',' in li[i]:
                newNumber = ''.join(li[i].split(','))
                li[i] = newNumber
            if '%' in li[i]:
                newNumber = ''.join(li[i].split("%"))
                li[i] = newNumber
    return row_list

def changeToDate(datlist):
    newlist = []
    for date in datlist:
        l = date.split(" ")
        date_str = l[0]
        day_str = l[1]
        hour_str, min_str = day_str.split(":")
        hour_int = int(hour_str)
        min_st = min_str[:-2]  # min

        am_or_pm = min_str[-2:]  # PM or AM
        if am_or_pm == 'PM':  # 12:48PM EST  don't need to add 12 hours
            if hour_int != 12:
                hour_int += 12
        li = [date_str, " ", str(hour_int), ":", min_st]
        newlist.append("".join(li))
    return newlist

def changeColmnformat(colmuns_name,row_list):
    row_list = removeSimpbol(row_list)
    stock_df = pd.DataFrame(data=row_list, columns=colmuns_name)
    datelist = stock_df['Last Trade Date'].values.tolist()
    datetime_str_list = changeToDate(datelist)

    stock_df['Last Trade Date'] = pd.Series(data=datetime_str_list)
    newdf = stock_df.drop(columns=['Contract Name', 'Last Trade Date'])
    newdf[newdf == '-'] = 0
    newdfw = newdf.apply(pd.to_numeric)
    stock_df['Last Trade Date'] = pd.to_datetime(stock_df['Last Trade Date'])
    ndf = stock_df[['Contract Name', 'Last Trade Date']]
    final_df = pd.concat([newdfw, ndf], axis=1)
    newcol = ['Contract Name',
              'Last Trade Date', 'Strike', 'Last Price', 'Bid', 'Ask', 'Change', '% Change',
              'Volume', 'Open Interest', 'Implied Volatility', ]

    final_df = final_df.loc[:, newcol]
    return  final_df

def savecsv(path,df):
        df.to_csv(path)
        print('save %s sucessful!'%(path))
def process():
    res = getData()
    if res == -1:
        return -1
    else:
        symboldf = res[0]
        colname = res[1]
        rowlist=res[2]
        print(symboldf)
        savecsv('./symbol.csv',symboldf)
        final_df = changeColmnformat(colname,rowlist)
        print(final_df)
        savecsv('./yahoo.csv',final_df)

