class World:
    def __init__(self, name: str, width: int = 100, height: int = 60):
        self.name = name
        self.width = width
        self.height = height
        self.tiles = [0] * (width * height) # Flat array for tiles
        self.owner_id = -1

    def get_tile(self, x: int, y: int) -> int:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y * self.width + x]
        return 0

    def set_tile(self, x: int, y: int, tile_id: int):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y * self.width + x] = tile_id

    def __repr__(self):
        return f"<World {self.name} ({self.width}x{self.height})>"
