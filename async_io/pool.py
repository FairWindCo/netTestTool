import asyncio
from typing import Optional

from async_io.task import Task


class Pool:
    def __init__(self, max_rate: int, interval: int = 1, concurrent_level: int = None):
        self.max_rate = max_rate
        self.interval = interval
        self.concurrent_level = concurrent_level
        self.is_running = False
        self._query = asyncio.Queue()
        self._scheduler: Optional[asyncio.Task] = None
        self._sem = asyncio.Semaphore(concurrent_level or max_rate)
        self.current_level = 0
        self._event = asyncio.Event()

    async def _worker(self, task: Task):
        async with self._sem:
            self.current_level += 1
            await task.process(self)
            self._query.task_done()
            self.current_level -= 1
            if not self.is_running and self.current_level == 0:
                self._event.set()

    async def _scheduler_task(self):
        while self.is_running:
            for _ in range(self.max_rate):
                async with self._sem:
                    task = await self._query.get()
                    asyncio.create_task(self._worker(task))
            await asyncio.sleep(self.interval)

    def start(self):
        if self._scheduler is None:
            self.is_running = True
            self._scheduler = asyncio.create_task(self._scheduler_task())

    def stop(self):
        if self.is_running:
            self.is_running = False
            self._scheduler.cancel()
        if self.current_level > 0:
            self._event.wait()

    async def put(self, task: Task):
        await self._query.put(task)

    async def join(self):
        await self._query.join()
