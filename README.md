## Stock Chart and Info Dash

Basic python stock chart, info, earnings and peers stocks dashboard. 

**NOTE: Relies on 3rd partY packages to scrape data. Always install the latest dependencies.**

**This repository is fOr archive purposes only and will not be updated. You may still find some code here useful for your own projects.**

## Installation and setup

Either create a virtual environment `python3 -m venv venv` in the repository folder or install the requirements anyway without a venv 

Activate virtual environment (if created): `source venv/bin/activate`

Install requirements: `pip install -r requirements.txt`

[Get a FREE API KEY from Fmp Cloud](https://fmpcloud.io/)

[Get a FREE API KEY from Finnhub](https://finnhub.io/)

Edit the `config.yaml` and enter the API keys, select a port to run the python server on and define a lookback period in days to fetch stock OHLCV data for (uses [yfinance](https://pypi.org/project/yfinance/)).

Run the python dash: `python charting.py`