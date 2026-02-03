from typing import Optional
from core.patterns.singleton import StatisticsManager

stats: Optional[StatisticsManager] = None

async def get_stats():
    global stats
    if stats is None:
        stats = await StatisticsManager.init()
    return stats
