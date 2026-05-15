from tuning.interfaces.car_repository import CarRepository
from tuning.models import Car
from tuning.entities.car import CarEntity

class DjangoCarRepository(CarRepository):
    def get_or_create(self, vin_id: str, base_price: int) -> CarEntity:
        car, _ = Car.objects.get_or_create(
            vin_id=vin_id,
            defaults={'base_price': base_price, 'description': ''}
        )
        return CarEntity(vin_id=car.vin_id, base_price=car.base_price, description=car.description)

    def get_by_vin(self, vin_id: str):
        try:
            car = Car.objects.get(vin_id=vin_id)
            return CarEntity(vin_id=car.vin_id, base_price=car.base_price, description=car.description)
        except Car.DoesNotExist:
            return None

    def get_by_id(self, car_id):
        try:
            car = Car.objects.get(pk=car_id)
            return CarEntity(
                vin_id=car.vin_id,
                base_price=car.base_price,
                description=car.description
            )
        except Car.DoesNotExist:
            return None