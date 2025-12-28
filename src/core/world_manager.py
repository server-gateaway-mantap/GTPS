from src.core.world import World

class WorldManager:
    def __init__(self):
        self.worlds = {} # key: name (upper), value: World object

    def get_world(self, name: str) -> World:
        name = name.upper()
        if name not in self.worlds:
            # Generate new world
            new_world = World(name)
            # Isi world dengan dummy tiles jika perlu (misal border bedrock, isi dirt)
            # Untuk sekarang world kosong (tiles = 0)
            self.worlds[name] = new_world

        return self.worlds[name]
