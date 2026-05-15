from tuning.entities.order import OrderEntity


class GetUserOrdersUseCase:
    def __init__(self, order_repository):
        self.order_repo = order_repository

    def execute(self, user_id) -> list:
        return self.order_repo.get_by_user(user_id)