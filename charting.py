import datetime as dt
import yfinance as yf
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from dash import dash_table
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import yaml

def check_round(val):

    if val is None:
        return 0

    return np.round(val, 2)


def get_data(ticker):

    start_time = dt.datetime.now() - dt.timedelta(days=400)
    print(start_time)

    # DOWNLOAD DATA FOR TICKER
    try:
        print('downloading stock data for: ', ticker)
        price_data = yf.download(ticker, start=start_time.strftime('%Y-%m-%d'), end=dt.datetime.today().strftime('%Y-%m-%d'))
        print('downloaded stock data for: ', ticker)
    except Exception as e:
        print('error fetching data for: ', ticker, e)
        price_data = None
    # END DOWNLOAD DATA FOR TICKER

    return price_data


def calc_rs(spy, data):
    return data/spy[-len(data):]


def get_ticker_name(symbol):
    """
    Get company name for ticker
    :param symbol:
    :return: company name
    """
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)

    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name']


def get_earnings_surprise(ticker, apikey):

    url = "https://fmpcloud.io/api/v3/earnings-surpises/{}?apikey={}".format(ticker, apikey)

    result = requests.get(url).json()

    return result


def scrap_next_earnings(ticker):

    url = 'https://stocksearning.com/stocks/{}/earnings-date'.format(ticker)
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    earndate = soup.find(id='ContentPlaceHolder1_lblEarningDate')
    epsest = soup.find(id='ContentPlaceHolder1_lblEstimatedEPS')

    return earndate.text, epsest.text


def get_fin_ratios(ticker, apikey):

    url = "https://fmpcloud.io/api/v3/ratios/{}?period=quarter&limit=1&apikey={}".format(ticker, apikey)

    result = requests.get(url).json()

    return result


def get_fin_growth(ticker, apikey):

    url = "https://fmpcloud.io/api/v3/financial-growth/{}?limit=1&apikey={}".format(ticker, apikey)

    result = requests.get(url).json()

    return result


def get_peers(ticker, apikey):

    url = 'https://finnhub.io/api/v1/stock/peers?symbol={}&token={}'.format(ticker, apikey)

    result = requests.get(url).json()

    return result


def get_basic_fins(ticker, apikey):

    url = 'https://finnhub.io/api/v1/stock/metric?symbol={}&metric=all&token={}'.format(ticker, apikey)

    result = requests.get(url).json()

    return result


def get_annual_income(ticker, apikey):

    url = 'https://fmpcloud.io/api/v3/income-statement/{}?limit=9&apikey={}'.format(ticker, apikey)

    result = requests.get(url).json()

    return result


def get_quarter_income(ticker, apikey):

    url = 'https://fmpcloud.io/api/v3/income-statement/{}?period=quarter&limit=6&apikey={}'.format(ticker, apikey)

    result = requests.get(url).json()

    return result


def filter_info(ticker, info):

    ## yf info dict keys ##
    # dict_keys(['zip', 'sector', 'fullTimeEmployees', 'longBusinessSummary', 'city', 'phone', 'state', 'country',
    #           'companyOfficers', 'website', 'maxAge', 'address1', 'industry', 'previousClose', 'regularMarketOpen',
    #           'twoHundredDayAverage', 'trailingAnnualDividendYield', 'payoutRatio', 'volume24Hr', 'regularMarketDayHigh',
    #           'navPrice', 'averageDailyVolume10Day', 'totalAssets', 'regularMarketPreviousClose', 'fiftyDayAverage',
    #           'trailingAnnualDividendRate', 'open', 'toCurrency', 'averageVolume10days', 'expireDate', 'yield', 'algorithm',
    #           'dividendRate', 'exDividendDate', 'beta', 'circulatingSupply', 'startDate', 'regularMarketDayLow', 'priceHint',
    #           'currency', 'regularMarketVolume', 'lastMarket', 'maxSupply', 'openInterest', 'marketCap',
    #           'volumeAllCurrencies', 'strikePrice', 'averageVolume', 'priceToSalesTrailing12Months', 'dayLow', 'ask',
    #           'ytdReturn', 'askSize', 'volume', 'fiftyTwoWeekHigh', 'forwardPE', 'fromCurrency', 'fiveYearAvgDividendYield',
    #           'fiftyTwoWeekLow', 'bid', 'tradeable', 'dividendYield', 'bidSize', 'dayHigh', 'exchange', 'shortName',
    #           'longName', 'exchangeTimezoneName', 'exchangeTimezoneShortName', 'isEsgPopulated', 'gmtOffSetMilliseconds',
    #           'quoteType', 'symbol', 'messageBoardId', 'market', 'annualHoldingsTurnover', 'enterpriseToRevenue',
    #           'beta3Year', 'profitMargins', 'enterpriseToEbitda', '52WeekChange', 'morningStarRiskRating', 'forwardEps',
    #           'revenueQuarterlyGrowth', 'sharesOutstanding', 'fundInceptionDate', 'annualReportExpenseRatio', 'bookValue',
    #           'sharesShort', 'sharesPercentSharesOut', 'fundFamily', 'lastFiscalYearEnd', 'heldPercentInstitutions',
    #           'netIncomeToCommon', 'trailingEps', 'lastDividendValue', 'SandP52WeekChange', 'priceToBook',
    #           'heldPercentInsiders', 'nextFiscalYearEnd', 'mostRecentQuarter', 'shortRatio', 'sharesShortPreviousMonthDate',
    #           'floatShares', 'enterpriseValue', 'threeYearAverageReturn', 'lastSplitDate', 'lastSplitFactor', 'legalType',
    #           'lastDividendDate', 'morningStarOverallRating', 'earningsQuarterlyGrowth', 'dateShortInterest', 'pegRatio',
    #           'lastCapGain', 'shortPercentOfFloat', 'sharesShortPriorMonth', 'category', 'fiveYearAverageReturn',
    #           'regularMarketPrice', 'logo_url'])
    ## ##

    try:
        earndate, esteps = scrap_next_earnings(ticker)
    except Exception as e:
        earndate, esteps = 'NA', 'NA'

    try:
        name = ticker##get_ticker_name(ticker)
        open = info['open']
        close = info['previousClose']
        mcap = info['marketCap']
        ma200 = info['twoHundredDayAverage']
        ma50 = info['fiftyDayAverage']
        avgvol = info['averageVolume']
        vol = info['volume']

        prev_close = info['previousClose']
        day_pct_change = ((open - prev_close) / prev_close) * 100.
        pct_of_50dma = ((open - ma50) / ma50) * 100.
        pct_of_200dma = ((open - ma200) / ma200) * 100.

        new_info =          {'Next Earnings': earndate,
                             'Est. EPS': esteps,
                             'Ticker': ticker,
                             'Name': name,
                             'Sector': info['sector'],
                             'Industry': info['industry'],
                             'MCAP [M]': check_round(mcap) / 1e6,
                             'Open [$]': open,
                             'Close [$]': close,
                             '% Change': check_round(day_pct_change),
                             'Vol. [M]': check_round(info['volume']) / 1e6,
                             'Avg. Vol. [M]': check_round(info['averageVolume']) / 1e6,
                             'Avg. 10D Vol. [M]': check_round(info['averageDailyVolume10Day']) / 1e6,
                             'Trailing EPS': check_round(info['trailingEps']),
                             'Forward EPS': check_round(info['forwardEps']),
                             'EPS QoQ': check_round(info['earningsQuarterlyGrowth']),
                             'Rev. Q Growth': check_round(info['revenueQuarterlyGrowth']),
                             '% Inst. Holdings': check_round(info['heldPercentInstitutions']),
                             '% of 200DMA': check_round(pct_of_200dma),
                             '% of 50DMA': check_round(pct_of_50dma),
                             'Forward PE': check_round(info['forwardPE']),
                             'Shares Outstanding': check_round(info['sharesOutstanding']),
                             'Float [M]': check_round(info['floatShares']) / 1e6,
                             '% Short Float': check_round(info['shortPercentOfFloat']),
                             '52W High': check_round(info['fiftyTwoWeekHigh'])
                             }
    except Exception as e:
        print('error filtering info: ', ticker, e)
        return {}

    return new_info, name


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# load filter config
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

app.layout = html.Div([

    html.Div([
        dcc.Input(id='ticker', type='text', value='TICKER'),
        html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    ]),

    html.Div(id='name', children=''),

    dcc.Loading(id="ohlc_loading",
                type="default",
                children=[dcc.Graph(id='chart')]
            ),

    html.P(id='summary'),

    html.Div([
        html.Div(id='table_info', children=[''], className="six columns"),
        html.Div(id='earn_table', children=[''], className="six columns"),
        html.Div(id='fin_ratio_table', children=[''], className="six columns"),
        html.Div(id='peers_table', children=[''], className="six columns"),
        ], className='row',),

])


@app.callback(
    Output('chart', 'figure'),
    Output('name', 'children'),
    Output('table_info', 'children'),
    Output('summary', 'children'),
    Output('earn_table', 'children'),
    Output('fin_ratio_table', 'children'),
    Output('peers_table', 'children'),
    [Input('submit-button-state', 'n_clicks')],
    [State('ticker', 'value')])
def update_output(n_clicks, ticker):
    if n_clicks > 0:
        price_data = get_data(ticker)
    else:
        raise PreventUpdate

    if price_data is None:
        return None, 'cannot get data for ' + ticker

    # get spy data and cal rs
    spy_data = get_data('SPY')
    dates = price_data.index
    rs_df = calc_rs(spy_data['Adj Close'], price_data['Adj Close'])

    # get info from yfinance
    share = yf.Ticker(ticker)
    info = share.info
    new_info, name = filter_info(ticker, info)

    # remake df so table is vertical
    info_df = pd.DataFrame(data={'Info': [x for x in new_info.keys()], 'Value': [y for y in new_info.values()]})

    summary = info['longBusinessSummary']

    # get earnings surprise
    earnings_surprise = get_earnings_surprise(ticker, config['fmpcloud_api_key'])
    earnings_df = pd.DataFrame.from_dict(earnings_surprise)
    try:
        est_earns = [y for y in earnings_df['estimatedEarning']]
    except Exception as e:
        est_earns = []
    try:
        actual_earns = [z for z in earnings_df['actualEarningResult']]
    except Exception as e:
        actual_earns = []
    earn_surprise = list(np.round((np.abs(np.array(actual_earns)) / np.abs(np.array(est_earns))) * 100 - 100, 2))
    try:
        new_earnings_df = pd.DataFrame(data={'Date': [x for x in earnings_df['date']],
                                             'Earnings Est.': est_earns,
                                             'Actual Earnings': actual_earns,
                                             '% Surprise': earn_surprise})
    except Exception as e:
        new_earnings_df = pd.DataFrame(data={})
    fin_ratios = get_fin_ratios(ticker, config['fmpcloud_api_key'])

    try:
        fin_ratios_df = pd.DataFrame(data={'Info': [x for x in fin_ratios[0].keys()], 'Value': [np.round(y,2) for y in fin_ratios[0].values()]})
    except Exception as e:
        fin_ratios_df = pd.DataFrame(data={})

    peers = get_peers(ticker, config['finnhub_api_key'])
    peers_df = pd.DataFrame(data={'Num': [i for i in range(len(peers))], 'Ticker': peers})

    # set vol bars colour
    close_open_diff = price_data['Adj Close'] - price_data['Open']
    volume_color = np.empty(price_data['Volume'].shape, dtype=object)
    volume_color[close_open_diff > 0] = 'green'
    volume_color[close_open_diff == 0] = 'gray'
    volume_color[close_open_diff < 0] = 'red'
    upvol = len(price_data['Volume'][close_open_diff > 0][-50:])
    downvol = len(price_data['Volume'][close_open_diff < 0][-50:])
    up_down_vol = np.round(upvol/downvol, 1)

    fig = go.Figure(data=[
                          go.Scatter(x=dates,
                             y=spy_data['Adj Close'],
                             name='SPY',
                             mode='lines',
                             line=dict(color='black'),
                             xaxis='x',
                             yaxis='y4'),
                         go.Scatter(x=dates,
                             y=rs_df,
                             name='RS',
                             mode='lines',
                             line=dict(color='black'),
                             xaxis='x',
                             yaxis='y3'),
                          go.Ohlc(x=dates,
                             open=price_data['Open'],
                             high=price_data['High'],
                             low=price_data['Low'],
                             close=price_data['Adj Close'],
                             name='OHLC',
                             yaxis='y2',
                             xaxis='x'
                              ),
                          go.Bar(
                              x=dates,
                              y=price_data['Volume'],
                              marker_color=volume_color,
                              marker_line_width=0,
                              name='Volume',
                              yaxis='y',
                              xaxis='x'
                          )
                    ],
                    layout=
                    dict(
                        margin=dict(b=40, t=20),
                        hovermode="closest",
                        xaxis=dict(
                            spikemode='across+marker',
                        ),
                        yaxis=dict(
                            domain=[0, 0.2],
                            spikemode='across+marker',
                            title='Volume',
                        ),
                        yaxis2=dict(
                            domain=[0.2, 0.7],
                            spikemode='across+marker',
                            title='Price',
                        ),
                        yaxis3=dict(
                            domain=[0.7, 0.9],
                            spikemode='across+marker',
                            title='RS',
                        ),
                        yaxis4=dict(
                            domain=[0.9, 1],
                            spikemode='across+marker',
                            title='Price',
                        ),
                        bargap=0
                    )
                )

    #fig.update_traces(name='Price', selector=dict(type='ohlc'))
    fig.update(layout_xaxis_rangeslider_visible=False) # make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=dates, y=price_data['Adj Close'].ewm(span=3).mean(), name='3EMA', mode='lines',
                                line=dict(color='green'), xaxis='x', yaxis='y2'),)
    fig.add_trace(go.Scatter(x=dates, y=price_data['Adj Close'].ewm(span=8).mean(), name='8EMA', mode='lines',
                                line=dict(color='purple'), xaxis='x', yaxis='y2'),)
    fig.add_trace(go.Scatter(x=dates, y=price_data['Adj Close'].ewm(span=21).mean(), name='21EMA', mode='lines',
                                line=dict(color='gold'), xaxis='x', yaxis='y2'),)
    fig.add_trace(go.Scatter(x=dates, y=price_data['Adj Close'].ewm(span=34).mean(), name='34EMA', mode='lines',
                                line=dict(color='black'), xaxis='x', yaxis='y2'),)
    fig.add_trace(go.Scatter(x=dates, y=price_data['Adj Close'].rolling(window=50).mean(), name='50MA', mode='lines',
                                line=dict(color='black'), xaxis='x', yaxis='y2'),)
    fig.add_trace(go.Scatter(x=dates, y=price_data['Adj Close'].rolling(window=200).mean(), name='200MA', mode='lines',
                                line=dict(color='red'), xaxis='x', yaxis='y2'),)
    #fig.update_yaxes(title_text="Price")
    fig.add_trace(go.Scatter(x=dates, y=price_data['Volume'].rolling(window=50).mean(), name='50VMA', mode='lines',
                                line=dict(color='black'), xaxis='x', yaxis='y'),)
    fig.add_trace(go.Scatter(x=dates, y=rs_df.rolling(window=13).mean(), name='RS MA13', mode='lines',
                                line=dict(color='dimgray'), xaxis='x', yaxis='y3'),)

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
        )
    )

    fig.update_layout(
        title=ticker,
        autosize=False,
        width=1300,
        height=600
    )

    infotable = dash_table.DataTable(
        id='info-table',
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'width': 80,
        },
        columns=[{"name": i, "id": i} for i in info_df.columns],
        data=info_df.to_dict('records')
    )

    earntable = dash_table.DataTable(
        id='earn-table',
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'width': 80,
        },
        columns=[{"name": i, "id": i} for i in new_earnings_df.columns],
        data=new_earnings_df.to_dict('records')
    )

    finratiotable = dash_table.DataTable(
        id='fin-ratio-table',
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'width': 80,
        },
        columns=[{"name": i, "id": i} for i in fin_ratios_df.columns],
        data=fin_ratios_df.to_dict('records')
    )

    peerstable = dash_table.DataTable(
        id='peers-table',
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'width': 80,
        },
        columns=[{"name": i, "id": i} for i in peers_df.columns],
        data=peers_df.to_dict('records')
    )

    return fig, name, infotable, summary, earntable, finratiotable, peerstable


if __name__ == '__main__':
    app.run_server(debug=config['debug'], port=config['port'])