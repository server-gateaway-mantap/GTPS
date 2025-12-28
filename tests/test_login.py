import requests
import sys
import traceback

def test_login_server():
    """
    Test sederhana untuk memvalidasi endpoint server_data.php
    """
    try:
        from fastapi.testclient import TestClient
        from src.server.login import app

        client = TestClient(app)

        print("[*] Mengirim POST request ke /growtopia/server_data.php")
        response = client.post("/growtopia/server_data.php")

        print(f"[*] Status Code: {response.status_code}")
        if response.status_code != 200:
            print("[!] Gagal: Status code bukan 200")
            sys.exit(1)

        content = response.text
        print(f"[*] Response Content:\n{content}")

        expected_parts = ["server|", "port|", "type|1", "meta|localhost"]
        for part in expected_parts:
            if part not in content:
                print(f"[!] Gagal: '{part}' tidak ditemukan di response.")
                sys.exit(1)

        print("[+] Login Server Verified Successfully!")

    except Exception:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_login_server()
