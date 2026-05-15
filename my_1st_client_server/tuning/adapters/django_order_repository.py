from tuning.interfaces.order_repository import OrderRepository
from tuning.models import Order, Car
from tuning.entities.order import OrderEntity
from django.contrib.auth.models import User

class DjangoOrderRepository(OrderRepository):
    def create(self, user_id, vin_id, base_price, tuning_options, total_price):
        user = User.objects.get(id=user_id)
        car = Car.objects.get(vin_id=vin_id)
        order = Order.objects.create(
            user=user, car=car,
            base_price=base_price,
            tuning_options=tuning_options,
            total_price=total_price
        )
        return OrderEntity(
            order_id=order.id,
            user_id=order.user.id,
            username=order.user.username,  # ← добавить
            vin_id=order.car.vin_id,
            base_price=order.base_price,
            tuning_options=order.tuning_options,
            total_price=order.total_price,
            created_at=order.created_at
        )

    def get_by_user(self, user_id):
        orders = Order.objects.filter(user_id=user_id).order_by('-created_at')
        return [
            OrderEntity(
                order_id=o.id,
                user_id=o.user.id,
                username=o.user.username,  # ← добавить
                vin_id=o.car.vin_id,
                base_price=o.base_price,
                tuning_options=o.tuning_options,
                total_price=o.total_price,
                created_at=o.created_at
            ) for o in orders
        ]

    def get_all(self):
        orders = Order.objects.all().order_by('-created_at')
        return [
            OrderEntity(
                order_id=o.id,
                user_id=o.user.id,
                username=o.user.username,  # ← добавить
                vin_id=o.car.vin_id,
                base_price=o.base_price,
                tuning_options=o.tuning_options,
                total_price=o.total_price,
                created_at=o.created_at
            ) for o in orders
        ]