import datetime
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine
import random
from pandas_datareader import data


def table_portfolio():
    alchemyEngine = create_engine('postgresql+psycopg2://postgres:5747@localhost/postgres')
    dbConnection = alchemyEngine.connect()
    table = pd.read_sql("select * from \"yahoo\"", dbConnection)
    sp500_table = pd.read_sql("select * from \"sp500components\"", dbConnection)


    ticker_table = table.loc[table['stock_date'] == datetime.date(2017, 5, 31), 'symbol'].values.tolist()

    # get random 30 tickers and its percentage
    random.seed(0)
    ticker_list = []
    percent_list = []
    for i in range(0,25):
        index = random.randint(0,len(ticker_table) -1)
        percent = random.randint(1,100)
        ticker_list.append(ticker_table[index])
        percent_list.append(percent)

    ticker = sp500_table[sp500_table['symbol'].isin(ticker_list)].reset_index(drop=True)
    ticker['value'] = percent_list
    sum = ticker['value'].sum()

    ticker['value'] = ticker['value'] * (100/sum) # value for 1 million

    # get unique sector and see the percentage of each sector
    sec_column_name = ['sector', 'percentage']
    sector = pd.DataFrame(columns=sec_column_name)
    for i in sp500_table.sector.unique():
        p = 0
        for j in ticker['symbol']:
            if sp500_table.loc[sp500_table.symbol == j, 'sector'].values[0] == i:
                p = p + ticker.loc[ticker.symbol == j, 'value'].values[0]
        sector.loc[len(sector)] = [i, p]

    # TODO: sector transfer to percentage, get pie chart
    # TODO: shift to do portfolio, use time to test
    # pd.set => see all data

    portfolio = pd.DataFrame()
    portfolio['stock_date'] = table.loc[(table['symbol'] == ticker['symbol'][0]), 'stock_date'].values.tolist()
    for i in ticker['symbol']:
        table_i = table[table['symbol'] == i].reset_index()
        share_value = ticker.loc[ticker.symbol == i, 'value'].values[0] / table.loc[(table.symbol == i) & (table.stock_date == datetime.date(2017, 5, 31)), 'adj_close'].values[0]
        portfolio[i] = table_i['adj_close'] / table_i['adj_close'].shift() - 1

    # SPY table
    start_date = '2017-05-31'
    end_date = '2022-05-31'
    SPY = data.DataReader('SPY', 'yahoo', start_date, end_date)
    SPY_share = 1000000 / SPY['Adj Close'][0]
    portfolio['SPY'] = (SPY['Adj Close'] / SPY['Adj Close'].shift() - 1).values

    dbConnection.close()
    return ticker, sector, portfolio, table



def plot_portfolio(portfolio):
    for column in portfolio.columns:
        if column == 'SPY':
            plt.plot(portfolio['stock_date'], portfolio[column], linewidth=3, alpha=0.5, label = column)
        elif column != 'stock_date':
            plt.plot(portfolio['stock_date'], portfolio[column], label = column)
    # TODO: plot each ticker with SPY
    # portfolio.plot(x='stock_date')
    plt.title("Each day's return for 30 random tickers From 2017-05-31 to 2022-05-31")
    plt.xlabel('Date')
    plt.ylabel('Return')
    plt.yticks()
    plt.legend(bbox_to_anchor=(1, 1))

    plt.show()





def main():
    ticker, sector, portfolio, table = table_portfolio()
    print(ticker)
    print(sector)
    print(portfolio)
    plot_portfolio(portfolio)


if __name__ == '__main__':
    main()