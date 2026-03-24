# Getting started

The library exposes three low level classes to access the GME API: ``MercatiElettrici``, ``MercatiGas`` and ``MercatiAmbientali``. A further class, ``MGP``, offers a higher level interface over the day-ahead electricity market. All classes require valid GME credentials.

```python
from mercati_energetici import MercatiElettrici, MercatiGas, MercatiAmbientali, MGP
```

Since the library is asynchronous, it is required to use it within an ``async`` function. All classes are used as async context managers, which handle authentication and session cleanup automatically:

```python
import asyncio
from mercati_energetici import MGP
from datetime import date

async def main():
    async with MGP("myuser", "mypassword") as mgp:
        print("PUN avg: ", await mgp.daily_pun(date(2023, 3, 28)))

if __name__ == "__main__":
    asyncio.run(main())
```

Dates are accepted as ``datetime.date`` objects or a ``str`` in the format ``YYYYMMDD`` like ``20230328`` for 28 March 2023. The default date is today.

## MGP

[What is the day-ahead market? (Mercato del Giorno Prima, MGP)](https://www.mercatoelettrico.org/en/Mercati/MercatoElettrico/MPE.aspx)

This class retrieves the average price of electricity in Italy (PUN) and allows access to hourly prices, volumes and liquidity of the day-ahead market.

```python
async with MGP("myuser", "mypassword") as mgp:

    # Get average PUN price
    print("PUN avg: ", await mgp.daily_pun(date(2023, 3, 28)))

    # Get PUN hourly prices
    print(await mgp.get_prices(date(2023, 3, 28)))

    # Get hourly volumes
    print(await mgp.get_volumes(date(2023, 3, 28)))

    # Get market liquidity
    print(await mgp.get_liquidity('20230328'))
```

The last three methods return a dictionary like:

```python
{
    0: 131.77,
    1: 120.0,
    2: 114.63154,
    3: 102.11652,
    4: 95.8797,
    5: 109.69628,
    6: 132.8,
    7: 158.1019,
    8: 167.17296,
    9: 169.0,
    ...
}
```

with hours as keys and the price [EUR/MWh] / volume [MWh] / liquidity [%] as values.

By default, prices and volumes refer to the whole Italy, but it is possible to specify a region (``CALA``, ``CNOR``, ``CSUD``, ``NORD``, ``PUN``, ``SARD``, ``SICI``, ``SUD``):

```python
await mgp.get_prices(date(2023, 3, 28), zone="SUD")
```

## MercatiElettrici

This class provides raw access to electricity market data for any segment (MGP, MI-A1, MI-A2, etc.). See [the GME website](https://www.mercatoelettrico.org/En/Mercati/MercatoElettrico/IlMercatoElettrico.aspx) for an explanation of the markets.

```python
async with MercatiElettrici("myuser", "mypassword") as mercati_elettrici:

    # Get hourly prices for the MI-A2 segment
    print(await mercati_elettrici.get_prices("MI-A2"))

    # Get hourly volumes
    print(await mercati_elettrici.get_volumes("MI-A2"))

    # Get market liquidity
    print(await mercati_elettrici.get_liquidity())
```

Unlike ``MGP``, these methods return data as delivered by the API, for all zones:

```python
[
    {"data": 20230404, "ora": 1, "mercato": "MI-A2", "zona": "CALA", "prezzo": 112.0},
    {"data": 20230404, "ora": 1, "mercato": "MI-A2", "zona": "CNOR", "prezzo": 112.0},
    {"data": 20230404, "ora": 1, "mercato": "MI-A2", "zona": "CSUD", "prezzo": 112.0},
    {"data": 20230404, "ora": 1, "mercato": "MI-A2", "zona": "NORD", "prezzo": 112.0},
    ...
]
```

## MercatiGas

This class wraps the API for the gas markets, covering continuous trading, auction mode and stored gas. See [the GME website](https://www.mercatoelettrico.org/en/Mercati/MGAS/MGas.aspx) for more details.

```python
async with MercatiGas("myuser", "mypassword") as mercati_gas:

    # Continuous trading results for a specific product and date
    await mercati_gas.get_continuous_trading_results("MGP-2023-04-06", date(2023, 4, 5))

    # Auction results
    await mercati_gas.get_auction_trading_results("MI-2023-04-05", date(2023, 4, 5))

    # Stored gas results for a specific company
    await mercati_gas.get_stored_gas_trading_results("Stogit", date(2023, 4, 5))
```

## MercatiAmbientali

This class wraps the API for the environmental markets (GO certificates and TEE). See [the GME website](https://www.mercatoelettrico.org/En/Mercati/TEE/CosaSonoTee.aspx) for an explanation.

```python
async with MercatiAmbientali("myuser", "mypassword") as mercati_ambientali:

    # Get trading results for a specific market and date
    await mercati_ambientali.get_trading_results("GO", date(2023, 3, 23))
```

## AuthenticatedMercatiEnergetici

All the above classes inherit from ``AuthenticatedMercatiEnergetici``, which provides direct access to the GME authenticated API. You can use it to query any dataset not covered by the higher-level classes:

```python
from mercati_energetici import AuthenticatedMercatiEnergetici

async with AuthenticatedMercatiEnergetici("myuser", "mypassword") as client:

    # Check your API quota usage
    quotas = await client.get_quotas()

    # Request any dataset by platform, segment and data name
    data = await client.request_data(
        platform="PublicMarketResults",
        segment="MGP",
        data_name="ME_ZonalPrices",
        interval_start="20230328",
        interval_end="20230328",
    )
```
