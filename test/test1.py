import asyncio
import time
from data import myanimelist

async def main():
    anime_name = "Ave Mujica"
    start_time = time.time()
    id = await myanimelist.get_id(anime_name)
    print(id)
    print(f"{time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
