import asyncio

from telegram_ai_app.bootstrap import create_runtime


def main() -> int:
    runtime = create_runtime()
    asyncio.run(runtime.run())
    return 0
