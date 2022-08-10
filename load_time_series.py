from pandas_datareader import data


# get symbol data and get finance data and import to database
from db import connect


def table_yahoo(conn):
    start_date = '2017-05-31'
    end_date = '2022-05-31'

    try:
        cur = conn.cursor()

        # get all symbols from database
        cur.execute('SELECT * FROM sp500components')  # use * to replace 'symbol' can get all data from database
        ticker = []
        for i in cur.fetchall():
            ticker.append(i[0])
        ticker.append('SPY')

        cur.execute('TRUNCATE TABLE yahoo;')

        insert_script = '''INSERT INTO yahoo (stock_date, symbol, open_price, high, low, close, adj_close, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''

        table = data.DataReader(ticker, 'yahoo', start_date, end_date)
        # some symbol may fail to read, so replace all NaN data to zero
        table = table.dropna(axis = 1)
        ticker = table['Close'].iloc[0].index.tolist()
        index = table.index
        index = index.strftime('%Y-%m-%d')
        for i in range(0, len(index)):
            for j in ticker:
                cur.execute(insert_script, (
                index[i], j, table['Open'][j].values.tolist()[i], table['High'][j].values.tolist()[i],
                table['Low'][j].values.tolist()[i], table['Close'][j].values.tolist()[i], table['Adj Close'][j].values.tolist()[i],
                table['Volume'][j].values.tolist()[i]))

        conn.commit()

    except Exception as error:
        print(error)

    finally:
        if cur is not None:
            cur.close()

def main():
    conn = connect()
    table_yahoo(conn)
    conn.close()


if __name__ == '__main__':
    main()