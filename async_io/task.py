import asyncio
from dataclasses import dataclass


@dataclass
class Task:
    task_id: int

    async def process(self, pool):
        print(f"start {self.task_id}")
        await asyncio.sleep(5)
        print(f"stop {self.task_id}")
