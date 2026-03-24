"""How to get the average price of electricity in Italy (PUN) for a specific date."""
import asyncio
import os
from datetime import date

from mercati_energetici import MGP

USERNAME = os.environ["GME_USERNAME"]
PASSWORD = os.environ["GME_PASSWORD"]


async def main() -> None:
    async with MGP(USERNAME, PASSWORD) as mgp:
        print("PUN avg: ", await mgp.daily_pun(date(2023, 3, 28)))


if __name__ == "__main__":
    asyncio.run(main())
