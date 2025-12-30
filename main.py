import asyncio
import uvicorn
import logging
from src.server.login import app
from src.network.enet_server import ENetServer

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Main")

async def start_login_server():
    """Menjalankan Login Server (FastAPI) via Uvicorn."""
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    logger.info("Starting Login Server on port 8000...")
    await server.serve()

async def start_game_server():
    """Menjalankan Game Server (ENet)."""
    server = ENetServer(host_ip="0.0.0.0", port=17091)
    logger.info("Starting Game Server on port 17091...")
    await server.start()

async def main():
    logger.info("=== Starting GTPS Python Server ===")

    # Jalankan kedua server secara konkuren
    await asyncio.gather(
        start_login_server(),
        start_game_server()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopping...")
