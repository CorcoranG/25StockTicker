from fpdf import FPDF
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data
from portfolio import table_portfolio
from risk import risk




ticker, sector, portfolio, table = table_portfolio()
unique_sector = sector[sector['percentage']!=0].reset_index(drop=True)
VAR = risk(portfolio)
column_name = ["Ticker", "Company", "Sector", "Industry", "Percentage"]
ticker.columns = column_name
print(ticker, '\n', sector, '\n', portfolio, '\n', VAR)

def SPY():
    start_date = '2017-01-01'
    end_date = '2022-05-31'
    SPY = data.DataReader('SPY', 'yahoo', start_date, end_date)
    return SPY

def ticker_info():
    # table for ticker, company, percentage
    ticker_info = ticker[['Ticker', 'Company', 'Percentage']]
    return ticker_info

def indus_per(sector_name):
    industry_list = ticker.loc[ticker.Sector == sector_name, 'Industry'].unique()
    sec_table = ticker[ticker['Sector'] == sector_name].reset_index(drop = True)
    percent_list=[]
    for i in industry_list:
        p = 0
        for j in range(0, len(sec_table)):
            if sec_table['Industry'][j] == i:
                p += sec_table['Percentage'][j]
        p = p/sector.loc[sector['sector'] == sector_name, 'percentage'].values[0] * 100
        percent_list.append(p)
    industry = pd.DataFrame()
    industry['Industry'] = industry_list
    industry['Percentage'] = percent_list
    return industry

def total_value(SPY):
    table_name = pd.DataFrame()
    for i in ticker.Ticker:
        table_name[i] = table.loc[table['symbol'] == i, 'adj_close'].reset_index(drop=True)
        share_value = 10000 * ticker.loc[ticker['Ticker'] == i, 'Percentage'].values[0] / table_name[i][0]
        table_name[i] = table_name[i] * share_value
    table_name['SPY'] = SPY['Adj Close'].reset_index(drop=True) * 1000000 / SPY['Adj Close'][0]
    portfolio_total = table_name.iloc[:, :-1].sum(axis = 1)
    table_name['Portfolio'] = portfolio_total
    return table_name

def risk_return(SPY, table_name):
    t_list = table_name.iloc[:, :-2].sum(axis = 1)
    total = t_list / t_list.shift() - 1
    final_portfolio = portfolio
    final_portfolio['portfolio'] = total
    total = total.values.tolist()
    total.sort()

    risk_90 = total[round(0.1 * (len(total) - 1))]
    risk_95 = total[round(0.05 * (len(total) - 1))]
    risk_99 = total[round(0.01 * (len(total) - 1))]
    VAR.loc[len(VAR)] = ['Portfolio', risk_90, risk_95, risk_99]

    year_return = []
    for i in VAR.symbol[:-2]:
        value = table.loc[table.symbol == i, 'adj_close'].values[-1] / table.loc[table.symbol == i, 'adj_close'].values[0] - 1
        year_return.append(value)
    year_return.append(SPY['Adj Close'][-1] / SPY['Adj Close'][0] - 1)
    year_return.append(t_list[len(t_list)-1] / t_list[0] - 1)

    VAR['1-Year Return'] = year_return
    VAR['1-Year Return'] = (VAR['1-Year Return']+1) ** (1/5) - 1

    std = portfolio.std().reset_index(drop=True)

    VAR['STD'] = std

    VAR['Sharp Ratio'] = (VAR['1-Year Return'] - 0.01) / VAR['STD']
    return VAR, final_portfolio

def corr_matrix():
    matrix = portfolio.corr()
    return matrix

def contribution(table_name, final_portfolio):
    new_table = table_name[table_name.columns.difference(['SPY', 'Portfolio'])]

    con_table = pd.DataFrame(columns = ticker['Ticker'])
    con_table.loc[len(con_table.index)] = ticker['Percentage'].values.tolist()

    return_list = (new_table.iloc[-1] - new_table.iloc[0])/(table_name['Portfolio'].iat[-1] - table_name['Portfolio'].iat[0]) * 100
    con_table.loc[len(con_table.index)] = return_list

    risk_list = []
    for i in new_table.columns:
        cov = (final_portfolio[i] * 100).cov(final_portfolio['portfolio'] * 100)
        risk_list.append(cov)
    con_table.loc[len(con_table.index)] = risk_list

    return con_table


def create_pdf():

    # create pdf subject
    pdf = FPDF('P', 'mm', 'A4')

    # add page
    pdf.set_auto_page_break(auto = True, margin = 15)
    pdf.add_page()

    # create a title of the report
    pdf.set_font('times', 'B', 20)
    pdf.cell(0,10, "Portfolio Report", align = 'C')
    pdf.ln(15)

    # insert ticker table
    ticker_table = ticker_info()
    pdf.set_font('times', 'B', 15)
    pdf.cell(0,10, "1.   25 Tickers' Information", 0, 2, align = 'L')
    pdf.ln(5)
    ticker_column = list(ticker_table.columns)
    pdf.set_font('times', 'B', 11)
    pdf.cell(10, 10, ' ', 1, 0, 'C')
    pdf.cell(40, 10, ticker_column[0], 1, 0, 'C')
    pdf.cell(70, 10, ticker_column[1], 1, 0, 'C')
    pdf.cell(35, 10, ticker_column[-1], 1, 1, 'C')
    pdf.set_font('times', '', 11)
    for i in range(0, len(ticker_table)):
        pdf.cell(10, 7, str(i+1), 1, 0, 'C')
        pdf.cell(40, 7, ticker_table['Ticker'][i], 1, 0, 'C')
        pdf.cell(70, 7, ticker_table['Company'][i], 1, 0, 'C')
        pdf.cell(35, 7, str(round(ticker_table['Percentage'][i], 2)), 1, 0, 'C')
        pdf.ln()


    pdf.add_page()
    # insert sector table
    pdf.ln(10)
    pdf.set_font('times', 'B', 15)
    pdf.cell(0, 10, "2.   Sectors' Information", 0, 2, align='L')
    pdf.ln(5)
    pdf.set_font('times', 'B', 11)
    pdf.cell(10, 10, ' ', 1, 0, 'C')
    pdf.cell(70, 10, 'Sector', 1, 0, 'C')
    pdf.cell(35, 10, 'Percentage', 1, 1, 'C')
    pdf.set_font('times', '', 11)
    for i in range(0, len(sector)):
        pdf.cell(10, 7, str(i + 1), 1, 0, 'C')
        pdf.cell(70, 7, sector['sector'][i], 1, 0, 'C')
        pdf.cell(35, 7, str(round(sector['percentage'][i], 2)), 1, 0, 'C')
        pdf.ln()

    # insert sector pie chart

    plt.pie((unique_sector['percentage'] != 0), labels = (unique_sector['sector']), autopct='%.2f%%')
    plt.title("Pie Chart of Sectors' Percentage", fontweight='bold')
    plt.savefig('sector.png', dpi=300, bbox_inches = "tight")
    pdf.image('sector.png', x = 126, y = 45, w = 80, type = '', link = '')
    plt.clf()

    # insert each industry table and pie chart
    pdf.ln(10)
    pdf.set_font('times', 'B', 15)
    pdf.cell(0, 10, "3.   Industries' Information", 0, 2, align='L')
    name_num = 0
    ypo = 155
    page_in = 0
    for name in unique_sector['sector']:
        name_num += 1
        page_in += 1
        if name_num == 3:
            pdf.add_page()
        pdf.ln(5)
        pdf.set_font('times', 'B', 15)
        title_name = '  3.'+str(name_num)+':   '+str(name)
        pdf.cell(0, 10, txt = title_name, border = 0, ln = 2, align='L')
        indus_table = indus_per(name)
        pdf.set_font('times', 'B', 11)
        pdf.cell(10, 10, ' ', 1, 0, 'C')
        pdf.cell(70, 10, 'Industry', 1, 0, 'C')
        pdf.cell(35, 10, 'Percentage', 1, 1, 'C')
        pdf.set_font('times', '', 11)


        for i in range(0, len(indus_table)):
            pdf.cell(10, 7, str(i + 1), 1, 0, 'C')
            pdf.cell(70, 7, indus_table['Industry'][i], 1, 0, 'C')
            pdf.cell(35, 7, str(round(indus_table['Percentage'][i], 2)), 1, 0, 'C')
            pdf.ln()

        pie = plt.pie(indus_table['Percentage'], autopct='%.2f%%')
        pie_title = "Pie Chart of " + name + " Percentage"
        plt.title(pie_title, fontweight='bold')
        plt.legend(pie[0], indus_table['Industry'], loc='center left', bbox_to_anchor=(-0.5,0.5), bbox_transform=plt.gcf().transFigure)
        plt.subplots_adjust(left=-2, bottom=0.1, right=0.45)
        image_name = 'industry' + str(name_num)+'.png'
        plt.savefig(image_name, dpi=300, bbox_inches="tight")

        if name_num == 1:
            ypo = 155
            pdf.image(image_name, x=130, y=ypo, h=45, type='', link='')
            plt.clf()

        else:
            if len(indus_per(unique_sector['sector'][name_num - 2])) < 2:
                if len(indus_table) < 3:
                    height = 30
                elif len(indus_table) < 4:
                    height = 35
                else:
                    height = 40
                times = 34
                ypo = ypo + times
                if ypo > 250:
                    page_in = 1
                    ypo = 17
                if (height == 40) & (ypo == 17):
                    ypo = 25
                    height = 45
                pdf.image(image_name, x=135, y=ypo, h=height, type='', link='')
                plt.clf()

            elif len(indus_per(unique_sector['sector'][name_num - 2])) < 3:
                times = 40
                if len(indus_table) < 3:
                    height = 30
                    times -= 5
                elif len(indus_table) < 4:
                    height = 35
                else:
                    height = 40
                ypo = ypo + times
                if ypo > 250:
                    page_in = 1
                    ypo = 17
                if (height == 40) & (ypo == 17):
                    ypo = 25
                    height = 45
                pdf.image(image_name, x=135, y=ypo, h=height, type='', link='')
                plt.clf()

            elif len(indus_per(unique_sector['sector'][name_num - 2])) < 4:
                xpo = 135
                if len(indus_table) < 3:
                    height = 30
                elif len(indus_table) < 4:
                    height = 35
                else:
                    height = 40
                times = 45
                ypo = ypo + times
                if ypo > 250:
                    page_in = 1
                    ypo = 17
                if (height == 40) & (ypo == 17):
                    ypo = 25
                    height = 45
                    xpo = 127
                pdf.image(image_name, x=xpo, y=ypo, h=height, type='', link='')
                plt.clf()

            else:
                if len(indus_table) < 3:
                    height = 30
                elif len(indus_table) < 4:
                    height = 35
                else:
                    height = 40
                times = 60
                ypo = ypo + times

                if ypo > 250:
                    page_in = 1
                    ypo = 17
                if (height == 40) & (ypo == 17):
                    ypo = 25
                    height = 45
                pdf.image(image_name, x=135, y=ypo, h=height, type='', link='')
                plt.clf()



    # insert risk table
    SPY_table = SPY()
    table_name = total_value(SPY_table)
    VAR, final_portfolio = risk_return(SPY_table, table_name)
    pdf.add_page()
    pdf.ln(10)
    pdf.set_font('times', 'B', 15)
    pdf.cell(0, 10, "4.   Risk Table For 25 Tickers, SPY, & Portfolio", 0, 2, align='L')
    pdf.ln(5)
    pdf.set_font('times', 'B', 11)
    risk_column = VAR.columns
    pdf.cell(5, 10, ' ', 1, 0, 'C')
    for i in risk_column[:-1]:
        pdf.cell(26, 10, i, 1, 0, 'C')
    pdf.cell(26, 10, risk_column[-1], 1, 1, 'C')
    for i in range(0, len(VAR)):
        if VAR['symbol'][i] == 'SPY':
            pdf.set_font('times', 'B', 11)
        elif VAR['symbol'][i] == 'Portfolio':
            pdf.set_font('times', 'B', 11)
            pdf.set_text_color(194, 8, 8)
        else:
            pdf.set_font('times', '', 11)
            pdf.set_text_color(0, 0, 0)
        pdf.cell(5, 7, str(i + 1), 1, 0, 'C')
        pdf.cell(26, 7, VAR['symbol'][i], 1, 0, 'C')
        for j in risk_column[1:]:
            pdf.cell(26, 7, str(round(VAR[j][i], 4)), 1, 0, 'C')
        pdf.ln()

    pdf.set_text_color(0, 0, 0)
    # insert total value plot
    plt.figure(figsize=(10, 7))
    pdf.add_page()
    pdf.ln(10)
    pdf.set_font('times', 'B', 15)
    pdf.cell(0, 10, "5.   Chart of Portfolio (25 Tickers) Total Value Compare With SPY", 0, 2, align='L')
    plt.plot(final_portfolio['stock_date'], table_name['SPY'], label = 'SPY', linewidth=2, alpha=0.5)
    plt.plot(final_portfolio['stock_date'], table_name['Portfolio'], label = 'Portfolio', linewidth=2, alpha=0.5)
    plt.legend()
    plt.title("Portfolio & SPY's Total Value From 2017-01-03 to 2022-05-31", fontweight='bold')
    plt.xlabel("Date")
    plt.ylabel("Total Value ($)")
    plt.ticklabel_format(style='plain', axis='y')
    plt.savefig("totalvalue.png", dpi=300, bbox_inches="tight")
    pdf.image("totalvalue.png", x = 36, y = 30, w = 130, type='', link='')
    plt.clf()

    # insert return chart
    plt.figure(figsize=(10, 7))
    pdf.ln(93)
    pdf.set_font('times', 'B', 15)
    pdf.cell(0, 10, "6.   Chart of Portfolio (25 Tickers) Return Compare With SPY", 0, 2, align='L')
    plt.plot(final_portfolio['stock_date'], final_portfolio['SPY'], label='SPY', linewidth=2, alpha=0.5)
    plt.plot(final_portfolio['stock_date'], final_portfolio['portfolio'], label='Portfolio', linewidth=2, alpha=0.5)
    plt.legend()
    plt.title("Portfolio & SPY's Everyday Return From 2017-01-03 to 2022-05-31", fontweight='bold')
    plt.xlabel("Date")
    plt.ylabel("Return ($)")
    plt.savefig("return.png", dpi=300, bbox_inches="tight")
    pdf.image("return.png", x=33, y=135, w=140, type='', link='')
    plt.clf()

    # insert correlation matrix
    pdf.add_page()
    pdf.ln(10)
    pdf.set_font('times', 'B', 15)
    pdf.cell(0, 10, "7.   Correlation Map for 25 Tickers & SPY", 0, 2, align='L')
    matrix = corr_matrix()
    plt.matshow(matrix, cmap='RdYlGn_r')
    location = list(range(0, 27))
    plt.xticks(location, matrix.columns.tolist(), rotation='vertical', fontsize=7)
    plt.yticks(location, matrix.columns.tolist(), fontsize=7)
    plt.colorbar(shrink = 0.7)
    plt.clim(-1, 1)
    plt.title("Correlation Matrix For 25 Tickers & SPY", fontweight='bold')
    plt.savefig("corr_matrix.png", dpi=300, bbox_inches="tight")
    plt.clf()
    pdf.image("corr_matrix.png", x=40, y=30, w=140, type='', link='')

    # graph for risk contribution
    contri = contribution(table_name, final_portfolio)
    pdf.add_page()
    pdf.ln(10)
    pdf.cell(0, 10, "8.   Allocation, Return Contribution, Risk Contribution", 0, 2, align='L')
    k = 0
    column = contri.columns.tolist()
    x_name = ['Allocation', 'Return\nContribution', 'Risk\nContribution']

    def addlabels(x, y):
        for i in range(len(x)):
            plt.text(i, y[i], round(y[i], 2))
    for i in range(0, len(column)):
        plt.bar(x_name, contri[column[i]])
        addlabels(x_name, contri[column[i]])
        title = str(column[i]) + "'s Contribution Graph From 2017-01-03 to 2022-05-31"
        plt.title(title, fontweight='bold')
        plt.ylabel("Percentage (%)")
        im_name = "contribution" + str(i + 1) + ".png"
        plt.savefig(im_name, dpi=300, bbox_inches="tight")
        plt.clf()
        if i == 8:
            pdf.add_page()
            k = 0
        if i == 16:
            pdf.add_page()
            k = 0
        if i == 24:
            pdf.add_page()
            k = 0
        if i % 2 == 0:
            y_po = 30 + 33 * k
            pdf.image(im_name, x=20, y=y_po, w=80, type='', link='')
        else:
            y_po = 30 + 33 * (k - 1)
            pdf.image(im_name, x=100, y=y_po, w=80, type='', link='')
        k += 1

    # appendix
    pdf.add_page()
    pdf.ln(10)
    pdf.cell(0, 10, "9.   Appendix", 0, 2, align='L')
    column = portfolio.columns[1:-1].tolist()
    k = 0
    for i in range(0, len(column)-1):
        plt.plot(portfolio['stock_date'], portfolio['SPY'], label='SPY', linewidth=2, alpha=0.5)
        plt.plot(portfolio['stock_date'], portfolio[column[i]], label=column[i], linewidth=2, alpha=0.5)
        plt.legend()
        title = str(column[i]) + " & SPY's Everyday Return From 2017-01-03 to 2022-05-31"
        plt.title(title, fontweight='bold')
        plt.xlabel("Date")
        plt.ylabel("Return ($)")
        im_name = "return" + str(i+1) + ".png"
        plt.savefig(im_name, dpi=300, bbox_inches="tight")
        plt.clf()
        if i == 8:
            pdf.add_page()
            k = 0
        if i == 16:
            pdf.add_page()
            k = 0
        if i == 24:
            pdf.add_page()
            k = 0
        if i % 2 == 0:
            y_po = 30 + 32 * k
            pdf.image(im_name, x=20, y=y_po, w=80, type='', link='')
        else:
            y_po = 30 + 32 * (k-1)
            pdf.image(im_name, x=100, y=y_po, w=80, type='', link='')
        k += 1



    pdf.output('report.pdf')


if __name__ == '__main__':
    create_pdf()