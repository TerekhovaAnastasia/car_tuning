from abc import ABC, abstractmethod
from tuning.entities.car import CarEntity


class CarRepository(ABC):

    @abstractmethod
    def get_or_create(self, vin_id: str, base_price: int) -> CarEntity:
        pass

    @abstractmethod
    def get_by_vin(self, vin_id: str):
        pass

    @abstractmethod
    def get_by_id(self, car_id) -> CarEntity: 
        pass