import os
import time
import statsmodels.api as sm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

# Build rm dict 
rm_df = pd.read_excel('D:/Thesis_data/Rm.xlsx')
rm_df['year'] = rm_df['Names Date'].map(lambda x: str(x)[:4])
rm_df['month'] = rm_df['Names Date'].map(lambda x: str(x)[4:6])
rm_dict = {}
for i in range(2005,2019,1):
    rm_dict[i]={}
for _, row in rm_df.iterrows():
    rm_dict[int(row['year'])][int(row['month'])] = row['Value-Weighted Return-incl. dividends']
    
# Build rf dict 
rf_df = pd.read_excel('D:/Thesis_data/Rf.xlsx')
rf_df['year'] = rf_df['Date (SAS). Last Trading Day of the Month'].map(lambda x: str(x)[:4])
rf_df['month'] = rf_df['Date (SAS). Last Trading Day of the Month'].map(lambda x: str(x)[4:6])
rf_dict = {}
for i in range(2005,2020,1):
    rf_dict[i]={}
for _, row in rf_df.iterrows():
    rf_dict[int(row['year'])][int(row['month'])] = row['Risk-Free Return Rate (One Month Treasury Bill Rate)']

# Read Data
df = pd.read_excel('D:/Thesis_data/factorData.xlsx')
df = df.drop('Unnamed: 0', axis=1).reset_index(drop=True)
df = df.drop(df[df['R']=='C'].index)
df['size mark'] = 0
df['book mark'] = 0
df['btm'] = df['B'] / df['price']

final_result_list = []
for year in range(2006,2019,1):
    if year == 2006:
        start_month = 7
    else:
        start_month = 1
    year_df = df[df['year'] == year]
    for month in range(start_month,13,1):
        current_df = year_df[year_df['month'] == month]
        current_df = current_df[current_df['B'] >= 0]

        # Assign by market size
        current_df = current_df.sort_values('market size',ascending=False)
        total_market_size = current_df['market size'].sum()

        current_market_size = 0
        result_list = []
        for _, row in current_df.iterrows():
            current_market_size = current_market_size + row['market size']
            if current_market_size < (0.5*total_market_size):
                row['size mark'] = 'B'
            else:
                row['size mark'] = 'S'
            result_list.append(row)
        result_df = pd.DataFrame(result_list)

        # Assign btm
        result_df = result_df.sort_values('btm')
        n_company = result_df.shape[0]
        current_n_company = 0
        result_list=[]
        for _, row in result_df.iterrows():
            current_n_company = current_n_company + 1
            if current_n_company < (n_company*0.3):
                row['book mark'] = 'L'
            elif current_n_company < (n_company*0.7):
                row['book mark'] = 'M'
            else:
                row['book mark'] = 'H'

            result_list.append(row)
        final_result_list.append(pd.DataFrame(result_list))
df_assigned = pd.concat(final_result_list).sort_index()

portfolio_R_dict = {}
for year in range(2006,2019,1):
    portfolio_R_dict[year] = {}
    if year == 2006:
        start_month = 7
    else:
        start_month = 1
    year_df = df_assigned[df_assigned['year'] == year]
    for month in range(start_month,13,1):
        portfolio_R_dict[year][month]={}
        month_df = year_df[year_df['month'] == month]
        for mark in ['SL', 'SM', 'SH', 'BL', 'BM', 'BH']:
            current_df = month_df[month_df['mark'] == mark]
            R = current_df['market*R'].sum() / current_df['market size'].sum()
            portfolio_R_dict[year][month][mark] = R

Rsize_dict = {}
Rbtm_dict = {}
for year in range(2006,2019,1):
    Rsize_dict[year] = {}
    Rbtm_dict[year] = {}
    if year == 2006:
        start_month = 7
    else:
        start_month = 1
    for month in range(start_month,13,1):
        current_dict = portfolio_R_dict[year][month]
        Rsize = (current_dict['SL']+current_dict['SM']+current_dict['SH']
                 -current_dict['BL']-current_dict['BM']-current_dict['BM'])/3
        Rbtm = (current_dict['SH']+current_dict['BM']-current_dict['SL']-current_dict['BL'])/2
        Rsize_dict[year][month] = Rsize
        Rbtm_dict[year][month] = Rbtm
        
        
with open('D:/Thesis_data/Rsize_dict.pickle', 'wb') as f:
    pickle.dump(Rsize_dict, f)
with open('D:/Thesis_data/Rbtm_dict.pickle', 'wb') as f:
    pickle.dump(Rbtm_dict, f)
    
def build_btm_size_dict(df):
    portfolio_R_dict = {}
    for year in range(2006,2019,1):
        portfolio_R_dict[year] = {}
        if year == 2006:
            start_month = 7
        else:
            start_month = 1
        year_df = df[df['year'] == year]
        for month in range(start_month,13,1):
            portfolio_R_dict[year][month]={}
            month_df = year_df[year_df['month'] == month]
            portfolio_R_dict[year][month]['Rm'] = month_df['market*R'].sum() / month_df['market size'].sum()
            for mark in ['SL', 'SM', 'SH', 'BL', 'BM', 'BH']:
                current_df = month_df[month_df['mark_in'] == mark]
                R = current_df['market*R'].sum() / current_df['market size'].sum()
                portfolio_R_dict[year][month][mark] = R
    return portfolio_R_dict

tone_dict = {}
for year in range(2006,2019,1):
    tone_dict[year] = {}
    if year == 2006:
        start_month = 7
    else:
        start_month = 1
    year_df = df[df['year'] == year]
    for month in range(start_month,13,1):
        month_df = year_df[year_df['month'] == month]
        high_df = month_df[month_df['tone mark'] == 'H']
        low_df = month_df[month_df['tone mark'] == 'L']
        R_high = high_df['market*R'].sum() / high_df['market size'].sum()
        R_low = low_df['market*R'].sum() / low_df['market size'].sum()
        tone_dict[year][month] = R_high - R_low
        
with open('D:/Thesis_data/tone_dict200107.pickle', 'wb') as f:
    pickle.dump(tone_dict, f)