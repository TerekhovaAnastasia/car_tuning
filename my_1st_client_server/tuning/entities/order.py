class OrderEntity:
    def __init__(self, order_id, user_id, vin_id: str, base_price: int, 
                 tuning_options: list, total_price: int, created_at=None, username: str = ""):
        self.order_id = order_id
        self.user_id = user_id
        self.vin_id = vin_id
        self.base_price = base_price
        self.tuning_options = tuning_options
        self.total_price = total_price
        self.created_at = created_at
        self.username = username