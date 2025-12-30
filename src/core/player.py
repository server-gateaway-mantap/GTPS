import json

class Player:
    def __init__(self, net_id: int, name: str = ""):
        self.net_id = net_id
        self.name = name
        self.password = ""
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.current_world = "EXIT"
        self.is_admin = False
        self.inventory = [] # List of item IDs

    def set_position(self, x: float, y: float):
        self.pos_x = x
        self.pos_y = y

    def load_from_db_data(self, data):
        # data tuple: (username, password, x, y, world, inventory_json)
        self.name = data[0]
        self.password = data[1]
        self.pos_x = data[2]
        self.pos_y = data[3]
        self.current_world = data[4]
        try:
            self.inventory = json.loads(data[5])
        except:
            self.inventory = []

    def __repr__(self):
        return f"<Player {self.name} (NetID: {self.net_id}) World: {self.current_world}>"
