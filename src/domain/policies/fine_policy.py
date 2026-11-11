from decimal import Decimal
from typing import Protocol


class FinePolicy(Protocol):
    """Contrato (Interface) para estratégias de cálculo de multa por atraso."""

    def calculate_fine(self, days_overdue: int) -> Decimal: ...


class StandardDailyFinePolicy:
    """Política padrão: cobra valor fixo por cada dia de atraso."""

    def __init__(self, daily_rate: Decimal = Decimal("2.00")) -> None:
        self.daily_rate = daily_rate

    def calculate_fine(self, days_overdue: int) -> Decimal:
        if days_overdue <= 0:
            return Decimal("0.00")
        return (self.daily_rate * days_overdue).quantize(Decimal("0.01"))


class AcademicGraceFinePolicy(FinePolicy):
    """Política academica: concede dias de carência e tarifa reduzida."""

    def __init__(self, grace_days: int = 2, daily_rate: Decimal = Decimal("1.50")) -> None:
        self._grace_days = grace_days
        self._daily_rate = daily_rate

    def calculate_fine(self, days_overdue: int) -> Decimal:
        if days_overdue <= self._grace_days:
            return Decimal("0.00")
        billable_days = days_overdue - self._grace_days
        return (self._daily_rate * billable_days).quantize(Decimal("0.01"))
