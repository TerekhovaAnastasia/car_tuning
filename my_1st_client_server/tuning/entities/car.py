class CarEntity:
    def __init__(self, vin_id: str, base_price: int, description: str = ""):
        self.vin_id = vin_id
        self.base_price = base_price
        self.description = description