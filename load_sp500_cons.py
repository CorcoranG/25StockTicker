from bs4 import BeautifulSoup
import requests
import psycopg2


# 1. wiki page all symbols load into database
# 2. get all data from database <=> you have all symbols
# 3. yahoo finance api page for each symbol you load time series data -> pd.DataFrame
# 4. create a new table (stock_date, symbol, open_price, high, low, close, volume)
# 5. insert time series data into new table

# import wiki data into python
from db import connect


def scrap_sp500_wikipage():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    # get the table we need
    table = soup.find("table", {'id': 'constituents'})

    # create header of the table
    header = []
    for i in table.find_all('th'):
        title = i.text.strip()
        header.append(title)

    # create a table to store header and all other data
    data = []
    data.append(header)

    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        row_data = []
        for col in cols:
            row_data.append(col.text.strip())
        data.append(row_data)

    return data

def load_into_db_sp500(conn, data):
    try:
        cur = conn.cursor()
        # first delete all data from table to ensure no duplication
        cur.execute('DELETE FROM sp500components')

        # inserting all data to table
        insert_script = 'INSERT INTO sp500components (symbol, company, sector,industry) VALUES (%s, %s, %s, %s)'
        for i in range(1, len(data)):
            cur.execute(insert_script, (data[i][0], data[i][1], data[i][3], data[i][4]))

        conn.commit()
    except Exception as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()



def main():
    conn = connect()
    data = scrap_sp500_wikipage()
    load_into_db_sp500(conn, data)
    conn.close()

if __name__ == '__main__':
    main()


# todo random 30 tickers/symbol
# random 1,100 -> 30
# A : 10 10%
# B: 40 40%
# C: 50 50%

# combine the sector, get percentage of each sector

# close adj (or close)
# 1 million => random get percentage for all 30 tickers (list of tuple EX: [('AAPL', 5), ('BA',8)]) => get values for each ticker
# => get the share value of each ticker at the start time (2017) => each day's total value (30 tickers together)
# => each day return (P2/P1 - 1) => std

# SPY symbol (500 together, total) => P2/P1 - 1 => std

# matplotlib: graph SPY and 30 tickers to compare (list of return), plot total value (30 and SPY)

# VAR (value at risk): in one day (time range), 95% (confidence level) sure for loss not over xxx
# find the 1%/5%/10% number (round up/down)



# generate pdf:
