from tuning.entities.order import OrderEntity
from tuning.use_cases.calculate_price import CalculatePriceUseCase


class CreateOrderUseCase:
    """
    Сценарий создания заказа.
    Содержит ВСЮ бизнес-логику: валидацию, поиск авто, расчёт цены.
    View только передаёт данные и получает результат.
    """

    def __init__(self, order_repository, car_repository):
        self.order_repo = order_repository
        self.car_repo = car_repository
        self.calculator = CalculatePriceUseCase()

    def execute(
            self,
            user_id: int,
            vin_id: str,
            car_id,  # ID выбранного авто
            base_price: int,
            options: list
    ) -> OrderEntity:

        # 1. Определить VIN
        if not vin_id and car_id:
            # Админ выбрал авто из списка — получаем VIN через репозиторий
            car = self.car_repo.get_by_id(car_id)
            if car:
                vin_id = car.vin_id

        if not vin_id and car_id:
            car = self.car_repo.get_by_id(car_id)
            if car:
                vin_id = car.vin_id

        if not vin_id:
            raise ValueError("VIN автомобиля обязателен")

        # 2. Найти или создать автомобиль
        car = self.car_repo.get_or_create(vin_id, base_price or 500_000)

        # 3. Определить базовую цену
        final_base_price = base_price if base_price else car.base_price

        # 4. Рассчитать итоговую цену
        total_price = self.calculator.execute(final_base_price, options)

        # 5. Сохранить заказ
        order = self.order_repo.create(
            user_id=user_id,
            vin_id=car.vin_id,
            base_price=final_base_price,
            tuning_options=options,
            total_price=total_price
        )

        return order