# import required packages
import os
import requests
import pandas as pd
import time
from sec_edgar_downloader import Downloader

# api related info.
dl = Downloader('D:/Thesis_data')
tickers = pd.read_excel('D:\\Thesis_data\\cik_ticker.xlsx')
nyse_nas = pd.concat([tickers[tickers['Exchange'] == 'NYSE'], tickers[tickers['Exchange'] == 'NASDAQ']], axis=0)

n_cik = nyse_nas.shape[0]
error_list=[]
print('Number of Stocks: ' + str(n_cik))
n = 0
# 從清單中刪除已下載
def diff(first, second):
    n = len(os.listdir('D:\\Thesis_data\\sec_edgar_filings'))
    second = set(second)
    return [item for item in first if str(item) not in second], n
download_list, n = diff(list(nyse_nas['CIK']),os.listdir('D:\\Thesis_data\\sec_edgar_filings'))

for cik in download_list:
    if n % 10 == 0:
        print('No.'+ str(n) +' is processing...' + str(n/n_cik) + '%')
    try:
        response = dl.get_10k_filings(cik,25)
    except:
        error_list.append(cik)
        continue
    if not response:
        os.mkdir('D:\\Thesis_data\\sec_edgar_filings\\'+str(cik))
    time.sleep(5)
    n = n+1