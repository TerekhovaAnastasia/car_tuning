class CalculatePriceUseCase:
    PRICE_RULES = {
        'engine': {'multiplier': 0.5, 'addition': 0},
        'nitrous': {'multiplier': 0, 'addition': 100_000},
        'turbine': {'multiplier': 0, 'addition': 50_000},
        'sound': {'multiplier': 0.2, 'addition': 0},
    }

    def execute(self, base_price: int, selected_options: list) -> int:
        total = base_price
        for option in selected_options:
            rule = self.PRICE_RULES.get(option)
            if rule:
                total += round(base_price * rule['multiplier']) + rule['addition']
        return total