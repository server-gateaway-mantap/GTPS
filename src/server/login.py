from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.api_route("/growtopia/server_data.php", methods=["GET", "POST"])
async def server_data(request: Request):
    """
    Endpoint ini dipanggil oleh client Growtopia untuk mendapatkan informasi server.
    Mendukung GET dan POST untuk kompatibilitas browser dan client game.
    Format respons: server|IP\nport|PORT\ntype|1\nmeta|localhost\n
    """
    # Dalam produksi, ganti 127.0.0.1 dengan IP publik server Anda
    # Port 17091 adalah port default GTPS

    server_ip = "127.0.0.1"
    server_port = 17091

    response_data = (
        f"server|{server_ip}\n"
        f"port|{server_port}\n"
        f"type|1\n"
        f"meta|localhost\n"
    )

    return PlainTextResponse(content=response_data)
