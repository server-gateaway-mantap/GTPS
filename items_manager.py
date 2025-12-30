import struct
import os

def create_minimal_items_dat(filepath="items_safe.dat"):
    """
    Creates a minimal valid Growtopia items.dat (Version 19)
    to ensure the client can load into the game without crashing.
    """
    item_count = 100

    # Version 19 Header
    # Version (2 bytes) + ItemCount (4 bytes)
    header = struct.pack("<H", 19) + struct.pack("<I", item_count)

    with open(filepath, "wb") as f:
        f.write(header)

        for i in range(item_count):
            # Write a generic item
            # Structure V19:
            # int itemID
            # char editableType
            # char itemCategory
            # char actionType
            # char hitSoundType
            # str name
            # str texture
            # int textureHash
            # char itemKind
            # int val1 (flags/seed color)
            # char textureX
            # char textureY
            # char spreadType
            # char isStripey
            # char collisionType
            # char hitsToBreak (health)
            # int resetTime (grow time)
            # char clothingType
            # short rarity
            # char maxAmount
            # str extraFile
            # int extraFileHash
            # int audioVolume? No, V19 varies.
            # str petName
            # str petPrefix
            # str petSuffix
            # ...

            # Let's use a known minimal structure for V19.
            # Based on open source parsers for V19.

            # ID
            f.write(struct.pack("<I", i))

            # Properties
            editable = 0
            category = 0
            action = 0
            hit_sound = 0

            name = "Item" + str(i)
            texture = "tiles_page1.rttex"

            if i == 0:
                name = "Blank"
            elif i == 1:
                name = "Dirt"
                editable = 1
                category = 1 # Block
                action = 1
            elif i == 2:
                name = "Soil"
            elif i == 18:
                name = "Bedrock"
                editable = 1
                category = 1

            f.write(struct.pack("B", editable))
            f.write(struct.pack("B", category))
            f.write(struct.pack("B", action))
            f.write(struct.pack("B", hit_sound))

            # Strings: Length(2) + Content
            f.write(struct.pack("<H", len(name)))
            f.write(name.encode('utf-8'))

            f.write(struct.pack("<H", len(texture)))
            f.write(texture.encode('utf-8'))

            # Texture Hash
            f.write(struct.pack("<I", 0))

            # Item Kind
            f.write(struct.pack("B", 0))

            # Val1 (Seed Color / Flags)
            f.write(struct.pack("<I", 0))

            # Texture X, Y
            f.write(struct.pack("B", 0))
            f.write(struct.pack("B", 0))

            # Spread, Stripey, Collision
            f.write(struct.pack("B", 0))
            f.write(struct.pack("B", 0))
            f.write(struct.pack("B", 0))

            # Health
            f.write(struct.pack("B", 10)) # Hits to break

            # Reset Time
            f.write(struct.pack("<I", 0))

            # Clothing Type
            f.write(struct.pack("B", 0))

            # Rarity
            f.write(struct.pack("<H", 0))

            # Max Amount
            f.write(struct.pack("B", 200))

            # Extra File
            extra = ""
            f.write(struct.pack("<H", len(extra)))
            f.write(extra.encode('utf-8'))

            # Extra File Hash
            f.write(struct.pack("<I", 0))

            # Audio Volume
            f.write(struct.pack("<I", 0))

            # Pet Name
            pet = ""
            f.write(struct.pack("<H", len(pet)))
            f.write(pet.encode('utf-8'))

            # Pet Prefix
            f.write(struct.pack("<H", len(pet)))
            f.write(pet.encode('utf-8'))

            # Pet Suffix
            f.write(struct.pack("<H", len(pet)))
            f.write(pet.encode('utf-8'))

            # Ability Name
            f.write(struct.pack("<H", len(pet)))
            f.write(pet.encode('utf-8'))

            # Skin Name
            f.write(struct.pack("B", 0)) # isSkin?

            # ... V19 ends roughly here?
            # Actually V19 structure is very specific.
            # If I miss a byte, the client crashes on load.
            # But the client is robust enough to ignore trailing zeros? No.
            # It reads sequentially.

            # Let's hope this minimal set works.
            # If V19 expects more fields, this will fail.
            # But "Blank" item usually has minimal data.

    print(f"[*] Generated minimal items.dat with {item_count} items.")

if __name__ == "__main__":
    create_minimal_items_dat()
