"""Shared test utilities and fixture data for mocked API responses."""
import base64
import io
import json
import zipfile

AUTH_URL = "https://api.mercatoelettrico.org/request/api/v1/Auth"
REQUEST_URL = "https://api.mercatoelettrico.org/request/api/v1/RequestData"
QUOTAS_URL = "https://api.mercatoelettrico.org/request/api/v1/GetMyQuotas"

AUTH_OK = {"success": True, "token": "test-token"}
AUTH_FAIL = {"success": False, "reason": "Invalid credentials"}


def make_zip_response(data) -> str:
    """Encode data as base64 zip with data.json, matching the API response format."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("data.json", json.dumps(data))
    return base64.b64encode(buf.getvalue()).decode()


def api_response(data) -> dict:
    return {"contentResponse": make_zip_response(data)}


def error_response(message="Data not found") -> dict:
    return {"resultRequest": message}


# ── Electricity fixtures ──────────────────────────────────────────────────────

_PRICE_ZONES = ["CALA", "CNOR", "CSUD", "NORD", "PUN", "SARD", "SICI", "SUD"]
_VOLUME_ZONES = ["CALA", "CNOR", "CSUD", "NORD", "SARD", "SICI", "SUD", "TOTALE"]
_HOURS = range(1, 25)


def make_prices_data(market="MGP", date_val="20230328"):
    return [
        {"FlowDate": str(date_val), "Hour": str(h), "Market": market, "Zone": z, "Price": str(100.0 + h), "Period": "0"}
        for z in _PRICE_ZONES
        for h in _HOURS
    ]


def make_volumes_data(market="MGP", date_val="20230328"):
    return [
        {
            "FlowDate": str(date_val), "Hour": str(h), "Market": market, "Zone": z,
            "Purchased": str(500.0 + h), "Sold": str(1000.0 + h), "Period": "0",
        }
        for z in _VOLUME_ZONES
        for h in _HOURS
    ]


def make_liquidity_data(date_val="20230328"):
    return [{"FlowDate": str(date_val), "Hour": str(h), "Liquidity": "74.47", "Period": "0"} for h in _HOURS]


# ── Gas fixtures ──────────────────────────────────────────────────────────────

CONTINUOUS_TRADING_DATA = [
    {
        "data": 20230405, "mercato": "MGP", "prodotto": "MGP-2023-04-06",
        "primoPrezzo": 50.5, "ultimoPrezzo": 51.151, "prezzoMinimo": 50.2,
        "prezzoMassimo": 52.5, "prezzoMedio": 51.357, "prezzoControllo": 51.995,
        "volumiMw": 10217.0, "volumiMwh": 245208.0,
    }
]

AUCTION_TRADING_DATA = [
    {
        "data": 20230405, "mercato": "MI", "prodotto": "MI-2023-04-05",
        "prezzo": None, "volumiMw": 0.0, "volumiMwh": 0.0,
        "acquistiTso": 0.0, "venditeTso": 0.0,
    }
]

STORED_GAS_DATA = [
    {
        "data": 20230405, "dataFlusso": 20230405, "impresaStoccaggio": "Stogit",
        "tipologia": None, "prezzo": 49.95, "volumi": 12036.924,
        "acquistiSrg": 2036.924, "venditeSrg": 0.0,
    }
]

# ── Environmental fixtures ────────────────────────────────────────────────────

ENV_RESULTS_DATA = [
    {
        "data": 20230323, "mercato": "GO", "tipologia": "Altro",
        "periodo": "Altri Mesi 2022", "prezzoRiferimento": 6.833425,
        "prezzoMinimo": 6.1, "prezzoMassimo": 9.0, "volumi": 3115.0,
    },
    {
        "data": 20230323, "mercato": "GO", "tipologia": "Eolico",
        "periodo": "Altri Mesi 2022", "prezzoRiferimento": 7.611801,
        "prezzoMinimo": 7.25, "prezzoMassimo": 8.0, "volumi": 5567.0,
    },
]

# ── Quotas fixture ────────────────────────────────────────────────────────────

QUOTAS_DATA = {
    "dailyLimit": 100,
    "dailyUsed": 5,
    "monthlyLimit": 1000,
    "monthlyUsed": 42,
}
