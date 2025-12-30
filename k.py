import re
import os

def fast_scan(so_path, output_file):
    if not os.path.exists(so_path):
        print("[-] File .so tidak ditemukan!")
        return

    # Target yang paling krusial untuk v5.39 berdasarkan riset
    targets = [b"type2", b"beta", b"maint", b"fhash", b"klv", b"nls", b"epp", b"Version"]

    print(f"[*] Memproses {so_path}... Hasil akan disimpan di {output_file}")

    with open(so_path, "rb") as f, open(output_file, "w") as out:
        # Baca per 1MB agar tidak stuck
        chunk_size = 1024 * 1024
        offset = 0

        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            for target in targets:
                for m in re.finditer(target, chunk):
                    rel_off = m.start()
                    abs_off = offset + rel_off

                    # Ambil context biner di sekitar temuan
                    start = max(0, rel_off - 20)
                    end = min(len(chunk), rel_off + len(target) + 20)
                    ctx = chunk[start:end]

                    out.write(f"Target: {target.decode()} | Offset: {hex(abs_off)}\n")
                    out.write(f"Context (Hex): {ctx.hex(' ')}\n")
                    out.write(f"Context (Text): {''.join(chr(b) if 32 <= b <= 126 else '.' for b in ctx)}\n")
                    out.write("-" * 40 + "\n")

            offset += chunk_size
            print(f"[*] Processed {offset // (1024*1024)}MB...", end="\r")

    print(f"\n[OK] Selesai! Cek file: {output_file}")

if __name__ == "__main__":
    fast_scan("libgrowtopia.so", "hasil_pencarian.txt")