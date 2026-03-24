<p align="center">
  <img src="docs/logo.svg" width="80" height="80" alt="mercati-energetici logo">
</p>

# mercati-energetici

## Async python library for Italian energy markets

Python async client for the official GME ([Gestore dei Mercati Energetici S.p.A.](https://mercatoelettrico.org/It/Default.aspx)) authenticated API. It allows to retrieve prices and volumes traded on the Italian energy markets (electricity, gas and environmental) in a simple and asynchronous way.

### Disclaimer

This library is not affiliated with GME ([Gestore dei Mercati Energetici S.p.A.](https://mercatoelettrico.org/It/Default.aspx)) in any way. It is provided as is, without any warranty. All data belongs to GME and cannot be used for profit.

### Example

```python
"""How to get the average price of electricity in Italy (PUN) for a specific date."""
import asyncio
from mercati_energetici import MGP
from datetime import date


async def main():
    async with MGP("myuser", "mypassword") as mgp:
        print("PUN avg: ", await mgp.daily_pun(date(2023, 3, 28)))


if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

The library exposes three low level classes to access the GME API: ``MercatiElettrici``, ``MercatiGas`` and ``MercatiAmbientali``. A further class, ``MGP``, offers a higher level interface over the day-ahead electricity market. All classes require valid GME credentials (username and password), obtainable by registering at [api.mercatoelettrico.org](https://api.mercatoelettrico.org/users/RegistrationForm/RegistrationRequest).

### Installation

```bash
pip install git+https://github.com/sammyrulez/mercati-energetici.git
```

### Usage

See the [documentation](https://sammyrulez.github.io/mercati-energetici/) for more details.

## Authors

- **Davide Marcato** — original author
- **Sam Reghenzi** — contributor
