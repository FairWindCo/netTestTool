import asyncio

from async_io.pool import Pool
from async_io.task import Task


async def main():
    pool = Pool(3)
    for i in range(20):
        await pool.put(Task(i))
    pool.start()
    await pool.join()
    pool.stop()


if __name__ == "__main__":
    asyncio.run(main())
