from typing import Literal

# Limits
MAX_FINANCIAL_STATEMENTS = 5

# Endpoints
KEY_METRICS = "key-metrics"

# Query string parameters
APIKEY_PARAM = "apikey"
LIMIT_PARAM = "limit"
PERIOD_PARAM = "period"
SYMBOL_PARAM = "symbol"

# Fields
CAPEX_TO_REVENUE = "capexToRevenue"
FISCAL_YEAR = "fiscalYear"

# Periods
type EarningsPeriod = Literal["Q1", "Q2", "Q3", "Q4", "FY", "annual", "quarter"]

# Symbols
type Symbol = Literal[
    "AAPL",
    "TSLA",
    "AMZN",
    "MSFT",
    "NVDA",
    "GOOGL",
    "META",
    "NFLX",
    "JPM",
    "V",
    "BAC",
    "PYPL",
    "DIS",
    "T",
    "PFE",
    "COST",
    "INTC",
    "KO",
    "TGT",
    "NKE",
    "SPY",
    "BA",
    "BABA",
    "XOM",
    "WMT",
    "GE",
    "CSCO",
    "VZ",
    "JNJ",
    "CVX",
    "PLTR",
    "SQ",
    "SHOP",
    "SBUX",
    "SOFI",
    "HOOD",
    "RBLX",
    "SNAP",
    "AMD",
    "UBER",
    "FDX",
    "ABBV",
    "ETSY",
    "MRNA",
    "LMT",
    "GM",
    "F",
    "LCID",
    "CCL",
    "DAL",
    "UAL",
    "AAL",
    "TSM",
    "SONY",
    "ET",
    "MRO",
    "COIN",
    "RIVN",
    "RIOT",
    "CPRX",
    "VWO",
    "SPYG",
    "NOK",
    "ROKU",
    "VIAC",
    "ATVI",
    "BIDU",
    "DOCU",
    "ZM",
    "PINS",
    "TLRY",
    "WBA",
    "MGM",
    "NIO",
    "C",
    "GS",
    "WFC",
    "ADBE",
    "PEP",
    "UNH",
    "CARR",
    "HCA",
    "TWTR",
    "BILI",
    "SIRI",
    "FUBO",
    "RKT",
]
