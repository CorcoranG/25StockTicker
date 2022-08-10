import pandas as pd
from portfolio import table_portfolio

def risk(portfolio):
    VAR = pd.DataFrame(columns=['symbol', 'risk at 90%', 'risk at 95%', 'risk at 99%'])
    for column in portfolio.columns:
        if column != 'stock_date':
            ticker_list = portfolio[column].values.tolist()
            ticker_list.sort()
            risk_90 = ticker_list[round(0.1 * (len(ticker_list) - 1))]
            risk_95 = ticker_list[round(0.05 * (len(ticker_list) - 1))]
            risk_99 = ticker_list[round(0.01 * (len(ticker_list) - 1))]
            VAR.loc[len(VAR)] = [column, risk_90, risk_95, risk_99]

    return VAR

def main():
    ticker, sector, portfolio, table = table_portfolio()
    risk(portfolio)

if __name__ == '__main__':
    main()

# TODO: random choose 25 tickers => 4% each or random
#  => calculate the share value of each ticker at start date => calculate total value of portfolio each day
#  => plot total value with SPY (each day)
#  => create PDF: 1. ticker name, company name, percentage (table)
#                 2. table & pie chart (sector & percentage)
#                 3. table & pie (for each sector, industry & percentage)
#                 4. risk (table (add a column for return (2022 / 2017 - 1)), another column std), 25 return plot compare with SPY(appendix)
#                 5. total value with SPY (each day) (plot)
#                 6. (portfolio everyday return) and VAR and std (add row to risk table), plot portfolio return with SPY return
#                 7. sharp ratio: assume risk free rate (无风险) = 1%. SR = (total return(1-year each ticker) - risk free)/std, add to risk table (column)
#                 8. correlation matrix (with color) (pandas.corr) : close to 1 -> more red; close to -1 -> more green, portfolio needs diversity
#                 9.

# TODO:
#  fix: make annual return: (1+x)^5 = total 5 year return => find x (annual return) => calculate sharp ratio
#  new:
#  1: return contribution: 3 graph (allocation, return contribution, risk contribution)
#       return (P2-P1) contribution: 100 A1 + 50 B1 = P1 & 100 A2 + 50 B2 = P2 => 100 (A2 - A1) + 50 (B2 - B1) = P2 - P1
#                   => A contribution = 100 (A2 - A1) / (P2 - P1); B contribution = 50 (B2 - B1) / (P2 - P1)
#                   ps: A1, A2, B1, B2 adj_close value; 100 & 50 are share value; P1, P2 are total portfolio value
#                   each ticker with one graph: allocation, return contribution, risk contribution
#       risk contribution: A% + B% = P%, ps: A%, B% are daily returns for each ticker; var(A% + B%) = var(P%)
#                   => cov(A% + B%, P%) = var(P%) = cov(A%, P%) + cov(B%, P%) => risk con A = cov(A%, P%) & risk con B = cov(B%, P%)