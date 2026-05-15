from abc import ABC, abstractmethod
from tuning.entities.order import OrderEntity

class OrderRepository(ABC):
    @abstractmethod
    def create(self, user_id, vin_id: str, base_price: int, tuning_options: list, total_price: int) -> OrderEntity:
        pass

    @abstractmethod
    def get_by_user(self, user_id) -> list:
        pass

    @abstractmethod
    def get_all(self) -> list:
        pass