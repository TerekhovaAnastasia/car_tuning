from tuning.entities.order import OrderEntity


class GetAllOrdersUseCase:

    def __init__(self, order_repository):
        self.order_repo = order_repository

    def execute(self) -> list:
        return self.order_repo.get_all()